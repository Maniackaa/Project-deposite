import requests


def get_new_token():
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
        'username': 'Operator6_Zajon_AZN',
        'password': 'hRQLVYCJ',
    }

    response = requests.post('https://birpay-gate.com/api/login_check', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        token = response.json().get('token')
        with open('token.txt', 'w') as file:
            file.write(token)
        return token


# x = get_new_token()
# print(x)