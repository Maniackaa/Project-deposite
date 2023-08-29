import asyncio
import time
import datetime

from sqlalchemy import select, func, Date, Time, and_
from sqlalchemy.exc import IntegrityError

from config_data.bot_conf import get_my_loggers
from database.db import Session, Incoming, TrashIncoming

logger, err_log, logger1, logger2 = get_my_loggers()


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


def add_to_trash(text: str):
    logger.debug(f'Добавление в нераспознанное {text}')
    try:
        session = Session()
        with session:
            trash = TrashIncoming(text=text)
            session.add(trash)
            session.commit()
            return True
    except Exception as err:
        logger.debug(f'Ошибка при добавлении в базу', exc_info=True)
        raise err


def read_new_incomings(last_num=0, sms_types: list[str] = []):
    logger.debug(f'Читаем базу где id > {last_num}')
    try:
        session = Session()
        with session:
            incomings = select(Incoming).where(Incoming.id > last_num).order_by('id')
            res = session.scalars(incomings).all()
            logger.debug(f'Результат {res}')
            return res
    except Exception as err:
        logger.debug(f'Ошибка при чтении базы', exc_info=True)


def find_new_out(last_num=0):
    try:
        session = Session()
        with session:
            incomings = select(Incoming).where(Incoming.id > last_num).filter(Incoming.sender.regexp_match(r'\d\d\d \d\d \d\d\d \d\d \d\d')).order_by('id')
            results = session.scalars(incomings).all()
            logger2.debug(f'Результат {results}')
            return results

    except Exception as err:
        logger2.debug(f'Ошибка при чтении базы', exc_info=True)


def get_day_report_rows():
    logger.debug(f'Читаем сменные отчеты')
    try:
        session = Session()
        with session:
            step1 = select(func.cast(Incoming.register_date, Date),
                               func.sum(Incoming.pay),
                               func.count(Incoming.pay)).where(
                and_(func.cast(Incoming.register_date, Time) >= '00:00', func.cast(Incoming.register_date, Time) < '08:00')
            ).group_by(
                func.cast(Incoming.register_date, Date)
            )
            results1 = session.execute(step1).all()

            step2 = select(func.cast(Incoming.register_date, Date),
                               func.sum(Incoming.pay),
                               func.count(Incoming.pay)).where(
                and_(func.cast(Incoming.register_date, Time) >= '08:00', func.cast(Incoming.register_date, Time) < '16:00')
            ).group_by(
                func.cast(Incoming.register_date, Date)
            )
            results2 = session.execute(step2).all()

            step3 = select(func.cast(Incoming.register_date, Date),
                           func.sum(Incoming.pay),
                           func.count(Incoming.pay)).where(
                and_(func.cast(Incoming.register_date, Time) >= '16:00',
                     func.cast(Incoming.register_date, Time) <= '23:59:59.999999')
            ).group_by(
                func.cast(Incoming.register_date, Date)
            )
            results3 = session.execute(step3).all()

            all_steps = select(func.cast(Incoming.register_date, Date),
                               func.sum(Incoming.pay),
                               func.count(Incoming.pay)).group_by(
                func.cast(Incoming.register_date, Date)
            )
            results_all = session.execute(all_steps).all()

            dates = select(func.cast(Incoming.register_date, Date)).order_by(func.cast(Incoming.register_date, Date)).distinct()
            dates_result = session.execute(dates).scalars().all()
            rows = []
            for date in dates_result:
                row = [date.strftime('%d.%m.%Y'), '0 - 0', '0 - 0', '0 - 0', '0 - 0']
                for all_day in results_all:
                    if all_day[0] == date:
                        step1_text = f'{round(all_day[1], 2)} - {all_day[2]}'
                        row[1] = step1_text

                for step1_day in results1:
                    if step1_day[0] == date:
                        step1_text = f'{round(step1_day[1], 2)} - {step1_day[2]}'
                        row[2] = step1_text
                for step2_day in results2:
                    if step2_day[0] == date:
                        step2_text = f'{round(step2_day[1], 2)} - {step2_day[2]}'
                        row[3] = step2_text
                for step3_day in results3:
                    if step3_day[0] == date:
                        step3_text = f'{round(step3_day[1], 2)} - {step3_day[2]}'
                        row[4] = step3_text
                rows.append(row)
            logger1.debug(f'Сменные отчеты: {rows}')
            return rows

    except Exception as err:
        err_log.debug(f'Ошибка при чтении отчетов', exc_info=True)


# check_transaction(80011554)

if __name__ == '__main__':
    pay = {'response_date': datetime.datetime(2023, 8, 25, 1, 7), 'sender': '+994 70 *** ** 27', 'bank': None, 'pay': 5.0, 'balance': None, 'transaction': 55555150, 'type': 'm10'}
    print(get_day_report_rows())
