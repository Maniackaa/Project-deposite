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


def read_new_trashincomings(last_num=0):
    try:
        session = Session()
        with session:
            incomings = select(TrashIncoming).where(TrashIncoming.id > last_num).order_by('id')
            res = session.scalars(incomings).all()
            logger.debug(f'Результат {res}')
            return res
    except Exception as err:
        logger.debug(f'Ошибка при чтении базы', exc_info=True)


def find_new_out(last_num=0):
    # Находит новые выводы
    try:
        session = Session()
        with session:
            incomings = select(Incoming).where(Incoming.id > last_num).filter(
                Incoming.sender.regexp_match(r'\d\d\d \d\d \d\d\d \d\d \d\d')).where(
                Incoming.pay > 0
            ).order_by('id')
            results = session.scalars(incomings).all()
            logger2.debug(f'Результат {results}')
            return results

    except Exception as err:
        logger2.debug(f'Ошибка при чтении базы', exc_info=True)
        raise err



#
# def get_step_results():
#     try:
#         session = Session()
#
#         def period_report(start='00:00', end='23:59:00.999999'):
#             """
#             Находит сумму и количество pay за период времени
#             :param start: '00:00'
#             :param end: '23:59:59.999999'
#             :return: [(datetime.date(2023, 8, 26), 500.0, 1)]
#             """
#             step = select(func.cast(Incoming.register_date, Date),
#                           func.sum(Incoming.pay),
#                           func.count(Incoming.pay)).where(
#                 and_(func.cast(Incoming.register_date, Time) >= start, func.cast(Incoming.register_date, Time) <= end)
#             ).where(Incoming.pay > 0).group_by(
#                 func.cast(Incoming.register_date, Date)
#             )
#             return step
#
#         with session:
#             step1 = period_report('00:00', '07:59:00.999999')
#             results1 = session.execute(step1).all()
#
#             step2 = period_report('08:00', '15:59:00.999999')
#             results2 = session.execute(step2).all()
#
#             step3 = period_report('16:00', '23:59:00.999999')
#             results3 = session.execute(step3).all()
#
#             all_steps = period_report()
#             results_all = session.execute(all_steps).all()
#
#             dates = select(func.cast(Incoming.register_date, Date)).order_by(
#                 func.cast(Incoming.register_date, Date)).distinct()
#             dates_result = session.execute(dates).scalars().all()
#
#             rows = []
#             for date in dates_result:
#                 print(date)
#                 row = [date.strftime('%d.%m.%Y'), '0 - 0', '0 - 0', '0 - 0', '0 - 0']
#                 for num, step in enumerate([results_all, results1, results2, results3], 1):
#                     print('---', step)
#                     for step_day in step:
#                         if step_day[0] == date:
#                             day_text = f'{round(step_day[1], 2)} - {step_day[2]}'
#                         row[num] = day_text
#                 rows.append(row)
#
#             logger1.debug(f'Сменные отчеты: {rows}')
#     except Exception as err:
#         err_log.error('ошибка посдсчета смен', exc_info=True)

def get_day_report_rows():
    logger.debug(f'Считаем сменные отчеты')

    def period_report(start='00:00', end='23:59:00.999999'):
        """
        Находит сумму и количество pay за период времени
        :param start: '00:00'
        :param end: '23:59:59.999999'
        :return: [(datetime.date(2023, 8, 26), 500.0, 1)]
        """
        step = select(func.cast(Incoming.register_date, Date),
                      func.sum(Incoming.pay),
                      func.count(Incoming.pay)).where(
            and_(func.cast(Incoming.register_date, Time) >= start, func.cast(Incoming.register_date, Time) <= end)
        ).where(Incoming.pay > 0).group_by(
            func.cast(Incoming.register_date, Date)
        )
        return step

    try:
        session = Session()

        with session:
            step1 = period_report('00:00', '07:59:00.999999')
            results1 = session.execute(step1).all()

            step2 = period_report('08:00', '15:59:00.999999')
            results2 = session.execute(step2).all()

            step3 = period_report('16:00', '23:59:00.999999')
            results3 = session.execute(step3).all()

            all_steps = period_report()
            results_all = session.execute(all_steps).all()

            dates = select(func.cast(Incoming.register_date, Date)).order_by(func.cast(Incoming.register_date, Date)).distinct()
            dates_result = session.execute(dates).scalars().all()

            rows = []
            for date in dates_result:
                print(date)
                row = [date.strftime('%d.%m.%Y'), '0 - 0', '0 - 0', '0 - 0', '0 - 0']
                for num, step in enumerate([results_all, results1, results2, results3], 1):
                    print('---', step)
                    for step_day in step:
                        if step_day[0] == date:
                            day_text = f'{round(step_day[1], 2)} - {step_day[2]}'
                            row[num] = day_text
                rows.append(row)

            logger1.debug(f'Сменные отчеты: {rows}')
            return rows

    except Exception as err:
        err_log.debug(f'Ошибка при чтении отчетов', exc_info=True)



def get_out_report_rows():
    logger.debug(f'Считаем сменные отчеты выводов')
    try:
        session = Session()

        def out_period_report(start='00:00', end='23:59:00.999999'):
            """
            Находит сумму и количество pay выводов за период времени
            :param start: '00:00'
            :param end: '23:59:59.999999'
            :return: [(datetime.date(2023, 8, 26), 500.0, 1)]
            """
            step = select(func.cast(Incoming.register_date, Date),
                          func.sum(Incoming.pay),
                          func.count(Incoming.pay)).filter(
                Incoming.sender.regexp_match(r'\d\d\d \d\d \d\d\d \d\d \d\d')).where(
                and_(
                    func.cast(Incoming.register_date, Time) >= start,
                    func.cast(Incoming.register_date, Time) <= end)).where(
                Incoming.pay > 0).group_by(func.cast(Incoming.register_date, Date))
            return step

        with session:
            step1 = out_period_report('00:00', '07:59:00.999999')
            results1 = session.execute(step1).all()

            step2 = out_period_report('08:00', '15:59:00.999999')
            results2 = session.execute(step2).all()

            step3 = out_period_report('16:00', '23:59:00.999999')
            results3 = session.execute(step3).all()

            all_steps = out_period_report()
            results_all = session.execute(all_steps).all()

            dates = select(func.cast(Incoming.register_date, Date)).order_by(func.cast(Incoming.register_date, Date)).distinct()
            dates_result = session.execute(dates).scalars().all()

            rows = []
            for date in dates_result:
                print(date)
                row = [date.strftime('%d.%m.%Y'), '0 - 0', '0 - 0', '0 - 0', '0 - 0']
                for num, step in enumerate([results_all, results1, results2, results3], 1):
                    print('---', step)
                    for step_day in step:
                        if step_day[0] == date:
                            day_text = f'{round(step_day[1], 2)} - {step_day[2]}'
                            row[num] = day_text
                rows.append(row)

            logger1.debug(f'Сменные отчеты выводов: {rows}')
            return rows

    except Exception as err:
        err_log.debug(f'Ошибка при чтении отчетов выводов', exc_info=True)


def read_all_out():
    """Тестовое чтение всех выводов (где полный sender)"""
    try:
        logger.debug('read_all_out')
        session = Session()
        all_out = select(Incoming).filter(
            Incoming.sender.regexp_match(r'\d\d\d \d\d \d\d\d \d\d \d\d'))
        res = session.execute(all_out).scalars().all()
        print('res read_all_out:', res)
        for row in res:
            print(row.id, row.sender)
        return res
    except Exception as err:
        print(err)


if __name__ == '__main__':
    pay = {'response_date': datetime.datetime(2023, 8, 25, 1, 7), 'sender': '+994 70 *** ** 27', 'bank': None, 'pay': 5.0, 'balance': None, 'transaction': 55555150, 'type': 'm10'}
    # print(get_day_report_rows())
    # print(get_out_report_rows())
    find_new_out()