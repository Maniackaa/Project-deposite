import asyncio
import time

from config_data.bot_conf import get_my_loggers, conf
from database.db import Incoming
from database.redis_db import r
from services.db_func import find_new_out
from services.google_func import write_to_table

logger, err_log, logger1, logger2 = get_my_loggers()


async def main():
    table2_last_num = r.get('table2_last_num')
    if not table2_last_num:
        table2_last_num = 0
    else:
        table2_last_num = int(table2_last_num.decode())
    logger2.debug(f'table2_last_num: {table2_last_num}')
    while True:
        try:
            start = time.perf_counter()
            new_outs: list[Incoming] = find_new_out(table2_last_num)
            rows = []
            for new_out in new_outs:
                print(new_out)
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
                print('rows')
                await write_to_table(rows, start_row=table2_last_num + 2, url=conf.tg_bot.TABLE_2)
                r.set('table2_last_num', pk)
                table2_last_num = pk
                logger2.debug(f'Записи добавлены за {time.perf_counter() - start}')
            else:
                pass
            time.sleep(5)

        except Exception as err:
            time.sleep(5)
            pass


if __name__ == '__main__':
    logger2.info('Starting Table writer 2')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger2.info('Table writer 2 stopped!')