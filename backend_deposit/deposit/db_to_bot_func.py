import datetime
import logging
import os
from time import time

import pytz
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, DateTime, Float, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker


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
engine = create_engine(db_url, echo=False)

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


def add_incoming_from_asu_to_bot_db(asu_incoming):
    """
    Добавляет платеж в базу с ботом на основании распознанного сркина с asu-payme
    """
    try:
        logger.debug(
            f'Сохраняем:'
            f'response_date: {str(asu_incoming.response_date)}\n'
            f'recipient: {asu_incoming.recipient}'
            f'sender: {asu_incoming.sender}'
            f'pay: {asu_incoming.pay}'
            f'balance: {asu_incoming.balance}'
            f'transaction: {asu_incoming.transaction}'
            f'type: {type}'
            )
        with Session() as session:
            bot_incoming = Incoming(
                response_date=asu_incoming.response_date,
                recipient=asu_incoming.recipient,
                sender='тестовый с сайта',
                pay=0,
                balance=asu_incoming.balance,
                transaction=99999999,
                type=asu_incoming.type,
            )
            session.add(bot_incoming)
            session.commit()
            logger.debug(f'Добавлен в базу бота: {bot_incoming}')
            return bot_incoming
    except Exception as err:
        logger.error(f'Ошибка добавления в базу бота: {err}')

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