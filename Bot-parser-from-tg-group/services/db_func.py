import asyncio
import time
import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config_data.bot_conf import get_my_loggers
from database.db import Session, Incoming

logger, err_log = get_my_loggers()


def check_transaction(transaction_num) -> bool:
    """Возвразает True если транзакция есть в базе"""
    logger.debug(f'Проверка наличия транзакции')
    try:
        session = Session()
        with session:
            result = session.execute(select(Incoming).where(Incoming.transaction == transaction_num)).scalars().all()
            if result:
                logger.debug(f'Транзакция {transaction_num} найдена')
                return True
        return False
    except Exception as err:
        err_log.error('Ошибка при проверке транзакции')
        raise err


def add_pay_to_db(pay: dict):
    logger.debug(f'Добавление в базу {pay}')
    try:
        session = Session()
        with session:
            incoming = Incoming(**pay)
            session.add(incoming)
            session.commit()
            return True
    except IntegrityError as err:
        logger.warning(f'Транзакция уже есть')
    except Exception as err:
        logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
        raise err


# check_transaction(80011554)

if __name__ == '__main__':
    pay = {'response_date': datetime.datetime(2023, 8, 25, 1, 7), 'sender': '+994 70 *** ** 27', 'bank': None, 'pay': 5.0, 'balance': None, 'transaction': 55555150, 'type': 'm10'}
    # add_pay_to_db(pay)