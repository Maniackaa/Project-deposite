import datetime
import time

from sqlalchemy import select

from config_data.bot_conf import get_my_loggers
from database.db import Session, Incoming

logger, err_log = get_my_loggers()


def read_last_rows():
    start = time.perf_counter()
    logger.debug(f'Читаем базу')
    try:
        session = Session()
        with session:

            incomings = select(Incoming).filter(Incoming.register_date > '2023-08-24 16:00:00').order_by('id')
            res = session.scalars(incomings).all()
            print(res)
            for i in res:
                print(i)
        print(time.perf_counter() - start)
    except Exception as err:
        logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
        # raise err

read_last_rows()
datetime.datetime(2023, 8, 24)