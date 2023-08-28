import asyncio
import time

from config_data.bot_conf import get_my_loggers
from database.db import Incoming
from database.redis_db import r
from services.db_func import read_new_incomings
from services.google_func import write_to_table

logger, err_log = get_my_loggers()


async def main():
    table1_last_num = r.get('table1_last_num').decode()
    if not table1_last_num:
        table1_last_num = 0
    else:
        table1_last_num = int(table1_last_num)
    logger.debug(f'table1_last_num: {table1_last_num}')
    while True:
        try:
            start = time.perf_counter()
            sms_types = ['sms1', 'sms2', 'sms3', 'm10']
            new_incomings: list[Incoming] = read_new_incomings(table1_last_num, sms_types)
            rows = []
            for incoming in new_incomings:
                print(incoming)
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
                print('rows')
                await write_to_table(rows, start_row=table1_last_num + 2)
                r.set('table1_last_num', pk)
                table1_last_num = pk
                logger.debug(f'Записи добавлены за {time.perf_counter() - start}')
            else:
                pass
            time.sleep(1)

        except Exception as err:
            raise err
            time.sleep(1)
            pass


if __name__ == '__main__':
    logger.info('Starting Table writer 1')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Table writer 1 stopped!')