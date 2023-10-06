import datetime
import time

import requests

from birpay.get_token import get_new_token
from config_data.bot_conf import tz
from database.db import Incoming


def get_birpay_list(results=50):
    try:
        with open('token.txt', 'r') as file:
            token = file.read()

        cookies = None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/json;charset=utf-8',
            'Referer': 'https://birpay-gate.com/refill-orders/list',
            'Origin': 'https://birpay-gate.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Authorization': f'Bearer {token}',
            'Connection': 'keep-alive',
        }

        json_data = {
            'filter': {
                'refillMethodTypeId': 104,  # m10
            },
            'sort': {},
            'limit': {
                'lastId': 0,
                'maxResults': results,
                'descending': True,
            },
        }

        response = requests.post(
            'https://birpay-gate.com/api/operator/refill_order/find',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        if response.status_code == 401:
            # Обновление токена
            token = get_new_token()
            headers['Authorization']= f'Bearer {token}'
            response = requests.post(
                'https://birpay-gate.com/api/operator/refill_order/find',
                cookies=cookies,
                headers=headers,
                json=json_data,
            )

        if response.status_code == 200:
            print(response.text)
            data = response.json()
            birpay_deposits = []
            for row in data:
                id = row.get('merchantTransactionId')
                status = row.get('status')
                sender = row.get('customerWalletId')
                requisite = row.get('paymentRequisite')
                recipient = requisite.get('payload')['phone_number']
                pay = float(row.get('amount'))
                created_time = datetime.datetime.fromisoformat(row.get('createdAt'))
                print(id, sender, recipient, created_time, pay)
                birpay_deposits.append({
                    'id': id,
                    'status': status,
                    'sender': sender,
                    'recipient': recipient,
                    'created_time': created_time,
                    'pay': pay,
                })
                # for key, val in row.items():
                #     print(f'{key}: {val}')
                # print('-------------------\n')
            return birpay_deposits
    except Exception as err:
        print(err)


def find_birpay_transaction(m10_incoming, birpay_list, threshold=10):
    """
    Находит первый неподтвержденный депозит за последние 10 минут
     при совпадении суммы, отправителя/
    """
    for deposit in birpay_list:
        print(deposit)
        m10_sender_first_part = m10_incoming.sender[:7].strip().replace(' ', '').replace('+', '')
        print(m10_sender_first_part)

        m10_sender_end = m10_incoming.sender[-2:]
        result = all([
            deposit['status'] == 0,
            deposit['sender'].startswith(m10_sender_first_part),
            deposit['sender'].endswith(m10_sender_end),
            deposit['pay'] == m10_incoming.pay,
            datetime.datetime.now(tz=tz) - deposit['created_time'] < datetime.timedelta(minutes=threshold)
        ])
        if result:
            return deposit['id']


start = time.perf_counter()
birpay_list = get_birpay_list()
# print(birpay_list)
print(time.perf_counter() - start)

m10_incoming = Incoming(
    id=36390,
    register_date=datetime.datetime(2023, 10, 6, 10, 11, 53),
    response_date=datetime.datetime(2023, 10, 6, 10, 00),
    recipient='+994 51 776 40 97',
    sender='+994 55 *** ** 46',
    # sender='5522 09** **** 9189',
    pay=100
)
bir_transaction = find_birpay_transaction(m10_incoming, birpay_list)
print(bir_transaction)

x = '9940515907027'
print(x[:3] + x[4:6])