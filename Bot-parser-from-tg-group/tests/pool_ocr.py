from itertools import repeat

import numpy as np
import pandas as pd
import pytesseract
import cv2
import datetime
# import matplotlib.pyplot as plt

from pathlib import Path
import time

from pandas import Series

BASE_DIR = Path(__file__).resolve().parent
path = BASE_DIR / 'image3.jpg'
print(path.resolve())


def get_right_text(string, key):
    splitted_string = string.split(key)
    if splitted_string:
        return splitted_string[1]


def response_screenshot_template(text):
    """
    1000.00 м

    02.08.2023 16:01

    Перевод от 1110
    Получатель +994 99 360 35 55
    Отправитель +994 99 *** ** 09
    Код транзакции 48675116
    Сумма 1000.00 м
    Статус Успешно

    8810)
    """
    msg_date = ''
    msg_time = ''
    sender = ''
    receiver = ''
    transaction = ''
    balance_change = ''
    for row in text.split('\n'):
        try:
            if 'Сумма ' in row:
                try:
                    raw_balance_change = get_right_text(row, 'Сумма ')
                    chars = [c if c in ['.'] or c.isdigit() else ''
                             for c in raw_balance_change]
                    balance_change = float(''.join(chars))
                except ValueError:
                    pass
            if 'Отправитель ' in row:
                raw_sender = row.split('Отправитель ')
                raw_sender = raw_sender[1]
                # sender_tel = re.findall(r'^.*?\+994(.+)$', raw_sender)
                # if sender_tel:
                #     sender = sender_tel[0]
                # else:
                sender = raw_sender
            if 'Получатель ' in row:
                raw_receiver = row.split('Получатель ')
                if raw_receiver:
                    raw_receiver = raw_receiver[1]
                    receiver = raw_receiver
            if 'Код транзакции ' in row:
                transaction = row.split('Код транзакции ')[1]
            try:
                raw_date_time = datetime.datetime.strptime(row, "%d.%m.%Y %H:%M")
                msg_date = str(raw_date_time.date())
                msg_time = str(raw_date_time.time())[:-3]
            except ValueError as err:
                pass
        except Exception as err:
            print('Ошибка распознаания строки', err)
            raise err
    result = {
        'msg_date': msg_date,
        'sender': sender,
        'receiver': receiver,
        'msg_time': msg_time,
        'balance_change': balance_change,
        'transaction': transaction
    }
    # result = [msg_date, msg_time, balance_change, sender, transaction]
    return result


from collections import Counter


def check_pair(args):
    path_pair, black = args
    print('black', black)
    path = BASE_DIR / 'images' / path_pair[0]
    nums = set()
    for i in range(40, 240):
        start = time.perf_counter()
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(img, i, black, cv2.THRESH_BINARY)
        # plt.imshow(binary, cmap='gray')
        # plt.show()
        string = pytesseract.image_to_string(binary, lang='rus')
        result = response_screenshot_template(string)

        if result == path_pair[1]:
            nums.add(i)
            print(i, result, time.perf_counter() - start)
    print(nums)
    return nums

path_test = [
	('11-7.jpg', {'msg_date': '2023-09-04', 'sender': '+994 51 *** ** 02', 'receiver': '+994 51 927 05 68', 'msg_time': '08:40', 'balance_change': 10.0, 'transaction': '58950711'}),
        ('1.jpg',
         {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '01:07',
          'balance_change': 5.0, 'transaction': '55555150'}),
        ('2.jpg',
         {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '01:03',
          'balance_change': 100.0, 'transaction': '55554745'}),
        # ('3.jpg',
        #  {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '00:39',
        #   'balance_change': 5.0, 'transaction': '55551881'}),
        # ('4.jpg',
        #  {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '00:33',
        #   'balance_change': 50.0, 'transaction': '55551154'}),
        # ('5.jpg',
        #  {'msg_date': '2023-08-24', 'sender': '+994 55 *** ** 77', 'receiver': '+994 51 927 05 68', 'msg_time': '22:17',
        #   'balance_change': 12.0, 'transaction': '55522337'}),
        # ('wrong1_2.jpg',
        #  {'msg_date': '2023-08-29', 'sender': '+994 70 *** ** 61', 'receiver': '+994 51 927 05 68', 'msg_time': '16:43',
        #   'balance_change': 5.0, 'transaction': '56980169'}),
        # ('wrong1.jpg',
        #  {'msg_date': '2023-08-29', 'sender': '+994 51 *** ** 01', 'receiver': '+994 51 927 05 68', 'msg_time': '16:25',
        #   'balance_change': 7.0, 'transaction': '56973239'}),
        # ('wrong_price.jpg',
        #  {'msg_date': '2023-08-30', 'sender': '+994 55 *** ** 91', 'receiver': '+994 51 927 05 68', 'msg_time': '13:33',
        #   'balance_change': 20.0, 'transaction': '57253009'}),
        # ('wrong_price2.jpg',
        #  {'msg_date': '2023-08-30', 'sender': '+994 50 *** ** 99', 'receiver': '+994 51 927 05 68', 'msg_time': '13:32',
        #   'balance_change': 70.0, 'transaction': '57252522'}
        #  ),

    ]


from multiprocessing import Pool


def pool_handler(black):
    start = time.perf_counter()
    p = Pool(4)
    res = p.map(check_pair, zip(path_test, repeat(black)))
    counter = Counter()
    for r in res:
        counter.update(r)
    print(counter)
    last_num = 0
    for key, val in sorted(counter.items()):
        delta = key - last_num
        # print(f'{delta if delta == 1 else "--" + str(delta)}. {key}: {val}')
        last_num = key
    print(time.perf_counter() - start)
    return counter


if __name__ == '__main__':
    df = pd.read_excel('map.xlsx', index_col=[0])
    df = df.reindex(columns=sorted(list(df.columns), reverse=True))
    df.to_excel('exit_map.xlsx')
    print(df)
    bad_black = list()
    maximum = max(df.max())
    print(maximum)
    for col in df.columns:
        is_good = any(df[col] == maximum)
        print(col, is_good)
        if not is_good:
            bad_black.append(col)
    print('bad_black', bad_black)




    # df = pd.DataFrame(index=range(1, 256))
    # for black in range(255, 0, -1):
    #     print(black, df.columns, black in df.columns)
    #     if black in df.columns:
    #         continue
    #     row = pool_handler(black)
    #     df.loc[:, black] = row
    #     df.to_excel('map.xlsx')