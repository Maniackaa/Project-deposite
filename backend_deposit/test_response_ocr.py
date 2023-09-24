import time

import cv2
import numpy as np
import pytesseract

from backend_deposit.settings import BASE_DIR
from deposit.screen_response import screen_text_to_pay

path = BASE_DIR / 'test' / 'ocr_test' / '1.jpg'


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'backend_deposit.settings')

import django
django.setup()


def main():
    nums = set()
    start = time.perf_counter()
    for i in range(0, 255):

        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(img, i, 242, cv2.THRESH_BINARY)
        # plt.imshow(binary, cmap='gray')
        # plt.show()
        string = pytesseract.image_to_string(binary, lang='rus')
        text = string.replace('\n', ' ')
        pay = screen_text_to_pay(text)
        if pay and pay.get('type'):
            pay['response_date'] = str(pay.get('response_date'))
            print(f'{i} ({len(nums)}), {pay}')
            # if pay == {'response_date': '2023-09-24 12:26:00+03:00', 'recipient': '+994 51 776 40 97', 'sender': '+994 77 *** ** 27', 'pay': 30.0, 'balance': None, 'transaction': 65948435, 'type': 'm10', 'status': 'Успешно', 'errors': []}:
            if pay == {'response_date': '2023-09-13 15:33:00+03:00', 'recipient': '+994 51 785 07 68', 'sender': '+994 51 *** ** 97', 'pay': 1.0, 'balance': None, 'transaction': 62176505, 'type': 'm10', 'status': 'Успешно', 'errors': []}:
                nums.add(i)
    print('nums', sorted(nums))


if __name__ == '__main__':
    nums_1 = set([31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 44, 47, 48, 49, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252])
    nums_2 = set([29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252])
    print(nums_1.intersection(nums_2))
    # main()
