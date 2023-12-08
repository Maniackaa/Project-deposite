import datetime
import logging
import os
from time import time

import pytz
from django.conf import settings
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, DateTime, Float, Integer, MetaData, select, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker

from deposit.func import send_message_tg

load_dotenv()

logger = logging.getLogger(__name__)

user = os.getenv('BOT_POSTGRES_USER')
password = os.getenv('BOT_POSTGRES_PASSWORD')
host = os.getenv('BOT_DB_HOST')
database = os.getenv('BOT_POSTGRES_DB')
port = os.getenv('BOT_DB_PORT')
tz = pytz.timezone(os.getenv('TIMEZONE'))

metadata = MetaData()
db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_url, echo=False, pool_pre_ping=True)

Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Incoming(Base):
    __tablename__ = 'deposit_incoming'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    register_date: Mapped[time] = mapped_column(DateTime(timezone=True), nullable=True,
                                                default=lambda: datetime.datetime.now(tz=tz))
    response_date: Mapped[time] = mapped_column(DateTime(timezone=True), nullable=True)
    recipient: Mapped[str] = mapped_column(String(50), nullable=True)
    sender: Mapped[str] = mapped_column(String(50), nullable=True)
    bank: Mapped[str] = mapped_column(String(50), nullable=True)
    pay: Mapped[float] = mapped_column(Float())
    balance: Mapped[float] = mapped_column(Float(), nullable=True)
    transaction: Mapped[int] = mapped_column(Integer(), nullable=True, unique=True)
    type: Mapped[str] = mapped_column(String(20), default='unknown')
    message_url: Mapped[str] = mapped_column(String(100), nullable=True)

    def __repr__(self):
        return f'{self.id}. {self.register_date}'


class TrashIncoming(Base):
    __tablename__ = 'deposit_trashincoming'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    register_date: Mapped[time] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.datetime.now(tz=tz))
    text: Mapped[str] = mapped_column(Text())


def add_incoming_from_asu_to_bot_db(asu_incoming: Incoming):
    """
    Добавляет платеж в базу с ботом на основании распознанного сркина с asu-payme
    """
    try:
        logger.debug(
            f'Сохраняем:'
            f'response_date: {str(asu_incoming.response_date)}\n'
            f'recipient: {asu_incoming.recipient}\n'
            f'sender: {asu_incoming.sender}\n'
            f'pay: {asu_incoming.pay}\n'
            f'balance: {asu_incoming.balance}\n'
            f'transaction: {asu_incoming.transaction}\n'
            f'type: {asu_incoming.type}'
            )
        with Session() as session:
            bot_incoming = Incoming(
                response_date=asu_incoming.response_date,
                recipient=asu_incoming.recipient,
                sender=asu_incoming.sender,
                pay=asu_incoming.pay,
                balance=asu_incoming.balance,
                transaction=asu_incoming.transaction,
                type=asu_incoming.type,
            )
            session.add(bot_incoming)
            session.commit()
            logger.debug(f'Добавлен в базу бота: {bot_incoming}')
            return bot_incoming
    except Exception as err:
        logger.error(f'Ошибка добавления в базу бота: {err}')
        send_message_tg(message=f'Срин не добавился в базу. ({err})', chat_id=settings.ADMIN_IDS)
        send_message_tg(message=f'Срин не добавился в базу. ({err})', chat_id='6051226224')


def add_pay_to_db2(pay: dict):
    """
    Добавляет распознанеое смс в базу2 бота
    """
    logger.debug(f'Добавление в базу2 бота {pay}')
    try:
        session = Session()
        with session:
            response_date = pay.get('response_date')
            sender = pay.get('sender')
            pay_sum = pay.get('pay')
            balance = pay.get('balance')
            old_incomings = session.execute(select(Incoming).where(Incoming.response_date == response_date,
                                                                   Incoming.sender == sender,
                                                                   Incoming.pay == pay_sum,
                                                                   Incoming.balance == balance)).all()
            if old_incomings:
                logger.warning(f'Транзакция уже есть')
                return 'duplicate'
            incoming = Incoming(**pay)
            session.add(incoming)
            session.commit()
            return True
    except IntegrityError as err:
        logger.error(err)
        logger.warning(f'Транзакция уже есть')

    except Exception as err:
        logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
        send_message_tg(message=f'Смс не добавилось в базу. ({err})', chat_id=settings.ADMIN_IDS)
        send_message_tg(message=f'Смс не добавилось в базу. ({err})', chat_id='6051226224')


def add_to_trash(text: str):
    logger.debug(f'Добавление в нераспознанное базы2 бота {text}')
    try:
        session = Session()
        with session:
            trash = TrashIncoming(text=text)
            session.add(trash)
            session.commit()
            return True
    except Exception as err:
        logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
        send_message_tg(message=f'Смс не добавилось в мусор. ({err})', chat_id=settings.ADMIN_IDS)
        send_message_tg(message=f'Смс не добавилось в мусор. ({err})', chat_id='6051226224')



# with Session() as session:
#     try:
#         bot_incoming = Incoming(
#             response_date=datetime.datetime.now(),
#             recipient='test recep',
#             sender='тестовый с сайта',
#             pay=0,
#             balance=10,
#             transaction=123456789,
#             type='m10',
#         )
#         session.add(bot_incoming)
#         session.commit()
#     except Exception as err:
#         print(err)