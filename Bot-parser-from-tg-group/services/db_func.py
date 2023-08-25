import asyncio
from sqlalchemy.exc import IntegrityError

from config_data.bot_conf import get_my_loggers
from database.db import Session, Incoming

logger, err_log = get_my_loggers()


async def add_pay_to_db(pay: dict):
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


if __name__ == '__main__':
    pass