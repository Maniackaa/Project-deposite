import datetime
import os
import time

import requests

from config_data.bot_conf import BASE_DIR, tz, get_my_loggers

logger, err_log, *other = get_my_loggers()

birpay_login = os.getenv('BIRPAY_LOGIN')
birpay_password = os.getenv('BIRPAY_PASSWORD')


def get_new_token(username=birpay_login, password=birpay_password):
    """Обновляет токен и сохраняет в файл"""
    logger.debug('Обновляем токен')
    cookies = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://birpay-gate.com',
        'Connection': 'keep-alive',
        'Referer': 'https://birpay-gate.com/login',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    json_data = {
        'username': username,
        'password': password,
    }

    response = requests.post('https://birpay-gate.com/api/login_check', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        token = response.json().get('token')
        with open(BASE_DIR / 'token.txt', 'w') as file:
            file.write(token)
        return token


def get_birpay_list(results=50) -> list[dict]:
    try:
        token_path = BASE_DIR / 'token.txt'
        token = ''

        if token_path.exists():
            with open(token_path, 'r') as file:
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
        logger.debug(f'response: {response.status_code}')
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
            # print(response.text)
            data = response.json()
            birpay_deposits = []
            for row in data:
                bir_id = row.get('merchantTransactionId')
                status = row.get('status')
                sender = row.get('customerWalletId')
                requisite = row.get('paymentRequisite')
                recipient = requisite.get('payload')['phone_number']
                pay = float(row.get('amount'))
                created_time = datetime.datetime.fromisoformat(row.get('createdAt'))
                logger.debug(f'{bir_id, sender, recipient, created_time, pay}')
                birpay_deposits.append({
                    'id': bir_id,
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
        logger.debug(f'{response.text}')
    except Exception as err:
        print(err)


def find_birpay_transaction(m10_incoming: dict, threshold=10):
    """
    Находит первый неподтвержденный депозит за последние 10 минут
     при совпадении суммы, отправителя/
    """
    try:
        logger.debug(f'Ищем birpay для {m10_incoming}')
        birpay_list = get_birpay_list()
        for birpay_deposit in birpay_list[::-1]:
            try:
                # +994 55 *** ** 46
                m10_sender_first_part = m10_incoming.get('sender')[:7].strip().replace(' ', '').replace('+', '')
                m10_sender_end = m10_incoming.get('sender')[-2:]
                birpay_sender_without_zero = birpay_deposit['sender'][:3] + birpay_deposit['sender'][4:]  # убираем нолик
                result = all([
                    birpay_deposit['status'] == 0,
                    birpay_deposit['sender'].startswith(m10_sender_first_part) or birpay_sender_without_zero == m10_sender_first_part,  # 9940515907027 или 994515907027 (99451)
                    birpay_deposit['sender'].endswith(m10_sender_end),
                    birpay_deposit['pay'] == m10_incoming.get('pay'),
                    datetime.datetime.now(tz=tz) - birpay_deposit['created_time'] < datetime.timedelta(minutes=threshold)
                ])
                logger.debug(f'birpay_deposit: {birpay_deposit} without zero: {birpay_sender_without_zero}')
                logger.debug(f'm10_first: {m10_sender_first_part}, end: {m10_sender_end}')
                logger.debug(
                    (birpay_deposit['status'] == 0,
                     birpay_deposit['sender'].startswith(
                     m10_sender_first_part) or birpay_sender_without_zero == m10_sender_first_part,  # 9940515907027 или 994515907027 (99451)
                     birpay_deposit['sender'].endswith(m10_sender_end),
                     birpay_deposit['pay'] == m10_incoming.get('pay'),
                     datetime.datetime.now(tz=tz) - birpay_deposit['created_time'] < datetime.timedelta(minutes=threshold)
                    )
                )
                if result:
                    logger.debug(f'Найден: {birpay_deposit["id"]}')
                    return birpay_deposit['id']
            except Exception as err:
                logger.warning(f'Ошибка в депозите {birpay_deposit}: {err}')
                err_log.error(err, exc_info=True)
        logger.debug('birpay не найден')
    except Exception as err:
        err_log.error(f'Ошибка при поиске birpay: {err}')


if __name__ == '__main__':
    start = time.perf_counter()
    birpay_list = get_birpay_list()
    # print(birpay_list)
    print(time.perf_counter() - start)

    m10_incoming = {
        'id': 36390,
        'register_date': datetime.datetime(2023, 10, 6, 10, 11, 53),
        'response_date': datetime.datetime(2023, 10, 6, 10, 00),
        'recipient': '+994 51 776 40 97',
        'sender': '+994 55 *** ** 46',
        'pay': 100
    }
    bir_transaction = find_birpay_transaction(m10_incoming)
    print(bir_transaction)