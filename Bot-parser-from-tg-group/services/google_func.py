import asyncio
import datetime
import time

import gspread
import gspread_asyncio
from gspread.utils import rowcol_to_a1

from config_data.bot_conf import BASE_DIR, conf, get_my_loggers
from google.oauth2.service_account import Credentials

logger, err_log = get_my_loggers()


def get_creds():
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    json_file = BASE_DIR / 'credentials.json'
    creds = Credentials.from_service_account_file(json_file)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


async def write_to_table(rows: list[list], start_row=1, sheets_num=0):
    """Записывает строки в таблицу"""
    if not rows:
        return
    logger.debug(f'Добавляем c {start_row}: {rows}')
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    agc = await agcm.authorize()
    url = conf.tg_bot.TABLE_1
    sheet = await agc.open_by_url(url)
    table = await sheet.get_worksheet(sheets_num)
    # await table.append_rows(rows)
    num_rows = len(rows)
    num_col = len(rows[0])

    last_row = start_row
    print(last_row)
    logger.debug(f'{rowcol_to_a1(last_row, 1)}:{rowcol_to_a1(last_row + num_rows, num_col)}')
    x = await table.batch_update([{
        'range': f'{rowcol_to_a1(last_row, 1)}:{rowcol_to_a1(last_row + num_rows, num_col)}',
        'values': rows,
    }])
    print('x', x)
    return True




if __name__ == '__main__':
    pass





