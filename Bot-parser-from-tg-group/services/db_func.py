import asyncio
import time
import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config_data.bot_conf import get_my_loggers
from database.db import Session, Incoming

logger, err_log = get_my_loggers()


def add_pay_to_db(pay: dict):
    logger.debug(f'Добавление в базу {pay}')
    counter = 75612731
    while True:
        try:
            pay['transaction'] = counter
            session = Session()
            with session:
                incoming = Incoming(**pay)
                session.add(incoming)
                session.commit()
                counter += 1
                print(counter)
        except IntegrityError as err:
            logger.warning(f'Транзакция уже есть')
        except Exception as err:
            logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
            raise err

def check_transaction(transaction_num):
    start = time.perf_counter()
    session = Session()
    with session:
        result = session.execute(select(Incoming).where(Incoming.transaction == transaction_num)).scalars().all()
        print(result)
        # result = session.execute(select(Incoming).where()).scalars().all()
        # print(result)
    print(time.perf_counter() - start)

check_transaction(80011554)

if __name__ == '__main__':
    pay = {'response_date': datetime.datetime(2023, 8, 25, 1, 7), 'sender': '+994 70 *** ** 27', 'bank': None, 'pay': 5.0, 'balance': None, 'transaction': 55555150, 'type': 'm10'}
    # add_pay_to_db(pay)