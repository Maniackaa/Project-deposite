import asyncio
import time

import aioschedule

from config_data.bot_conf import get_my_loggers, conf
from database.db import Incoming
from database.redis_db import r
from services.db_func import find_new_out, get_out_report_rows, read_all_out
from services.google_func import write_to_table

logger, err_log, logger1, logger2 = get_my_loggers()


async def write_sheets2():
    try:
        logger2.info('Добавляем репорт выводов')
        rows = get_out_report_rows()
        await write_to_table(rows, start_row=2, url=conf.tg_bot.TABLE_2, sheets_num=1)
    except Exception as err:
        logger2.error('Ошибка при записи в таблицу 2', exc_info=True)


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
            table2_last_id = r.get('table2_last_id')
            table2_last_row = r.get('table2_last_row')
            if not table2_last_id:
                table2_last_id = 0
                table2_last_row = 0
            else:
                table2_last_id = int(table2_last_id.decode())
                table2_last_row = int(table2_last_row.decode())
            logger2.debug(f'table2_last_id: {table2_last_id}')
            start = time.perf_counter()
            new_outs: list[Incoming] = find_new_out(table2_last_id)[:2000]
            rows = []
            for new_out in new_outs:
                pk = new_out.id
                row = [
                    new_out.id,
                    new_out.register_date.strftime('%Y.%m.%d %H:%M'),
                    new_out.response_date.strftime('%Y.%m.%d %H:%M'),
                    new_out.sender,
                    new_out.pay,
                    new_out.transaction,
                ]
                rows.append(row)
            if rows:
                logger.debug(f'Найдены новых выводов: {len(rows)}')
                await write_to_table(rows, start_row=table2_last_row + 2, url=conf.tg_bot.TABLE_2)
                r.set('table2_last_id', pk)
                r.set('table2_last_row', table2_last_row + len(rows))
                logger2.debug(f'Записи добавлены за {time.perf_counter() - start}')

            time.sleep(10)

        except Exception as err:
            logger2.error(err, exc_info=True)
            time.sleep(5)
            pass


if __name__ == '__main__':
    logger2.info('Starting Table writer 2')
    try:
        # r.set('table2_last_id', 0)
        # read_all_out()
        # print('Новые выводы', find_new_out(0))
        # get_out_report_rows()
        # asyncio.run(write_sheets2())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger2.info('Table writer 2 stopped!')