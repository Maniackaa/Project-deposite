import datetime
import time

import numpy as np
import pytesseract
import cv2
# import matplotlib.pyplot as plt

from config_data.bot_conf import BASE_DIR


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
    # pay_from = ''
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
            # if 'Перевод' in row:
            #     transaction = row.split('Перевод')[1]
            #     pay_from = transaction
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
        'transaction': transaction,
        # 'pay_from': pay_from
    }
    # result = [msg_date, msg_time, balance_change, sender, transaction]
    return result


from collections import Counter


def img_path_to_str(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    string = pytesseract.image_to_string(binary, lang='rus')
    result = response_screenshot_template(string)
    return result


def test_img_path_to_str():
    path_test = [
        ('1.jpg', {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '01:07', 'balance_change': 5.0, 'transaction': '55555150'}),
        ('2.jpg', {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '01:03', 'balance_change': 100.0, 'transaction': '55554745'}),
        ('3.jpg', {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '00:39', 'balance_change': 5.0, 'transaction': '55551881'}),
        ('4.jpg', {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '00:33', 'balance_change': 50.0, 'transaction': '55551154'}),
        ('5.jpg', {'msg_date': '2023-08-24', 'sender': '+994 55 *** ** 77', 'receiver': '+994 51 927 05 68', 'msg_time': '22:17', 'balance_change': 12.0, 'transaction': '55522337'}),

    ]
    counter = Counter()
    for path_pair in path_test:

        path = BASE_DIR / 'photos' / path_pair[0]

        for i in range(255):
            nums = set()
            start = time.perf_counter()
            img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(img, i, 255, cv2.THRESH_BINARY)
            # plt.imshow(binary, cmap='gray')
            # plt.show()
            string = pytesseract.image_to_string(binary, lang='rus')
            result = response_screenshot_template(string)
            print(result)
            # if result == path_pair[1]:
            #     nums.add(i)
            #     print(i, result, time.perf_counter() - start)
            #     counter.update(nums)
        print(counter)
    return result


# test_img_path_to_str()

# text_response = img_path_to_str()

res = {85: 5, 88: 5, 89: 5, 90: 5, 91: 5, 93: 5, 94: 5, 119: 5, 120: 5, 121: 5, 126: 5, 127: 5, 128: 5, 129: 5, 130: 5, 131: 5, 132: 5, 133: 5, 134: 5, 135: 5, 136: 5, 137: 5, 138: 5, 139: 5, 140: 5, 141: 5, 142: 5, 143: 5, 144: 5, 145: 5, 146: 5, 147: 5, 148: 5, 149: 5, 151: 5, 152: 5, 153: 5, 154: 5, 155: 5, 156: 5, 158: 5, 159: 5, 160: 5, 161: 5, 162: 5, 163: 5, 166: 5, 167: 5, 168: 5, 169: 5, 173: 5, 175: 5, 183: 5, 184: 5, 203: 5, 204: 5, 205: 5, 206: 5, 207: 5, 208: 5, 209: 5, 210: 5, 211: 5, 212: 5, 213: 5, 214: 5, 215: 5, 216: 5, 225: 5, 226: 5, 231: 5, 232: 5, 233: 5, 234: 5, 235: 5, 237: 5, 40: 4, 82: 4, 84: 4, 164: 4, 171: 4, 172: 4, 174: 4, 177: 4, 178: 4, 181: 4, 182: 4, 223: 4, 236: 4, 42: 3, 69: 3, 71: 3, 118: 3, 123: 3, 150: 3, 170: 3, 92: 3, 108: 3, 110: 3, 111: 3, 112: 3, 117: 3, 165: 3, 186: 3, 41: 2, 44: 2, 60: 2, 62: 2, 63: 2, 64: 2, 65: 2, 66: 2, 67: 2, 68: 2, 70: 2, 72: 2, 73: 2, 74: 2, 75: 2, 76: 2, 157: 2, 217: 2, 218: 2, 219: 2, 220: 2, 222: 2, 227: 2, 228: 2, 229: 2, 230: 2, 38: 2, 39: 2, 81: 2, 83: 2, 95: 2, 105: 2, 176: 2, 179: 2, 180: 2, 185: 2, 224: 2, 86: 1, 87: 1, 107: 1, 109: 1, 114: 1, 115: 1, 116: 1, 122: 1, 124: 1, 125: 1, 187: 1, 188: 1}
#120-149,
res_linux = {48: 5, 49: 5, 50: 5, 51: 5, 52: 5, 53: 5, 54: 5, 55: 5, 56: 5, 57: 5, 58: 5, 59: 5, 60: 5, 61: 5, 62: 5, 63: 5, 64: 5, 65: 5, 66: 5, 67: 5, 68: 5, 69: 5, 70: 5, 71: 5, 75: 5, 76: 5, 77: 5, 78: 5, 79: 5, 80: 5, 81: 5, 82: 5, 83: 5, 84: 5, 85: 5, 86: 5, 87: 5, 88: 5, 89: 5, 90: 5, 91: 5, 92: 5, 93: 5, 94: 5, 95: 5, 96: 5, 97: 5, 98: 5, 99: 5, 100: 5, 101: 5, 102: 5, 103: 5, 104: 5, 105: 5, 106: 5, 107: 5, 108: 5, 109: 5, 110: 5, 111: 5, 112: 5, 113: 5, 114: 5, 115: 5, 116: 5, 117: 5, 118: 5, 119: 5, 120: 5, 121: 5, 122: 5, 123: 5, 124: 5, 125: 5, 126: 5, 127: 5, 128: 5, 129: 5, 130: 5, 131: 5, 132: 5, 133: 5, 134: 5, 137: 5, 144: 5, 154: 5, 155: 5, 156: 5, 167: 5, 168: 5, 170: 5, 171: 5, 179: 5, 180: 5, 181: 5, 189: 5, 190: 5, 191: 5, 192: 5, 193: 5, 194: 5, 195: 5, 196: 5, 197: 5, 198: 5, 199: 5, 200: 5, 201: 5, 202: 5, 203: 5, 204: 5, 205: 5, 206: 5, 207: 5, 208: 5, 209: 5, 210: 5, 211: 5, 212: 5, 213: 5, 214: 5, 215: 5, 216: 5, 217: 5, 218: 5, 219: 5, 220: 5, 231: 5, 232: 5, 233: 5, 234: 5, 235: 5, 236: 5, 42: 4, 43: 4, 44: 4, 45: 4, 46: 4, 47: 4, 72: 4, 73: 4, 74: 4, 135: 4, 136: 4, 138: 4, 139: 4, 140: 4, 141: 4, 142: 4, 143: 4, 145: 4, 146: 4, 147: 4, 148: 4, 149: 4, 150: 4, 151: 4, 152: 4, 153: 4, 157: 4, 158: 4, 159: 4, 160: 4, 161: 4, 162: 4, 163: 4, 164: 4, 165: 4, 166: 4, 169: 4, 172: 4, 173: 4, 174: 4, 175: 4, 176: 4, 177: 4, 178: 4, 182: 4, 183: 4, 184: 4, 185: 4, 186: 4, 187: 4, 188: 4, 221: 4, 222: 4, 227: 4, 228: 4, 229: 4, 230: 4, 237: 4, 39: 2, 223: 2, 224: 2, 225: 2, 226: 2, 239: 2}
#49-71, 76-134

#120-134 -> 127

# last = 0
# for num, val in res_linux.items():
#     print(num, val, last - num)
#     last = num


def ocr_test():

    path_test = [
        ('1.jpg', {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '01:07', 'balance_change': 5.0, 'transaction': '55555150'}),
        ('2.jpg', {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '01:03', 'balance_change': 100.0, 'transaction': '55554745'}),
        ('3.jpg', {'msg_date': '2023-08-25', 'sender': '+994 70 *** ** 27', 'receiver': '+994 51 927 05 68', 'msg_time': '00:39', 'balance_change': 5.0, 'transaction': '55551881'}),
        ('4.jpg', {'msg_date': '2023-08-25', 'sender': '+994 55 *** ** 57', 'receiver': '+994 51 927 05 68', 'msg_time': '00:33', 'balance_change': 50.0, 'transaction': '55551154'}),
        ('5.jpg', {'msg_date': '2023-08-24', 'sender': '+994 55 *** ** 77', 'receiver': '+994 51 927 05 68', 'msg_time': '22:17', 'balance_change': 12.0, 'transaction': '55522337'}),
    ]

    for path_pair in path_test:
        path = BASE_DIR / 'tests' / path_pair[0]
        resp = img_path_to_str(path)
        assert resp == path_pair[1], f'Ошибка при расознавании:\nОбразец:\n{path_pair[1]}\nРезультат:\n{resp}'

ocr_test()