import asyncio
import time

import aioschedule


from config_data.bot_conf import get_my_loggers, conf
from database.db import Incoming
from database.redis_db import r
from services.db_func import read_new_incomings, get_day_report_rows
from services.google_func import write_to_table

logger, err_log, logger1, logger2 = get_my_loggers()


async def write_sheets2():
    logger1.info('Добавляем репорт')
    rows = get_day_report_rows()
    await write_to_table(rows, start_row=2, url=conf.tg_bot.TABLE_1, sheets_num=1)


async def jobs():
    print('sheets2_report')
    aioschedule.every().hour.do(write_sheets2)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


async def main():
    asyncio.create_task(jobs())

    while True:
        try:
            start = time.perf_counter()
            table1_last_num = r.get('table1_last_num')
            if not table1_last_num:
                table1_last_num = 0
            else:
                table1_last_num = int(table1_last_num.decode())
            logger1.debug(f'table1_last_num: {table1_last_num}')

            # sms_types = ['sms1', 'sms2', 'sms3', 'm10', 'm10_short']
            new_incomings: list[Incoming] = read_new_incomings(table1_last_num)
            rows = []
            for incoming in new_incomings:
                logger1.debug(incoming)
                pk = incoming.id
                row = [
                    incoming.id,
                    incoming.register_date.strftime('%Y.%m.%d %H:%M'),
                    incoming.response_date.strftime('%Y.%m.%d %H:%M'),
                    incoming.sender,
                    incoming.bank,
                    incoming.pay,
                    incoming.balance,
                    incoming.transaction,
                ]
                rows.append(row)
            if rows:
                await write_to_table(rows, start_row=table1_last_num + 2)
                r.set('table1_last_num', pk)
                logger1.debug(f'Записи добавлены за {time.perf_counter() - start}')
            else:
                pass
            await asyncio.sleep(1)

        except Exception as err:
            await asyncio.sleep(1)
            pass


if __name__ == '__main__':
    logger1.info('Starting Table writer 1')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger1.info('Table writer 1 stopped!')