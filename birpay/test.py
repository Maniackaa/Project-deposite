import requests

cookies = {
    'PHPSESSID': 't0fqh9tu473mssn7lk84uvuhpq',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=utf-8',
    'Referer': 'https://birpay-gate.com/refill-orders/list',
    'Origin': 'https://birpay-gate.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2OTQ2ODUwODYsImV4cCI6MTY5NDcyNTIwMCwicm9sZXMiOlsiUk9MRV9PUEVSQVRPUiJdLCJ1c2VybmFtZSI6Ik9wZXJhdG9yNl9aYWpvbl9BWk4ifQ.pEQSbSyngJOgWK2VoBPxiATZZqeG7965uGn8Eg5L5ru015chW_L1iQUdSTzLSXoXFIfhn1Iex38Og0iUNPJeC-5dSBp7sNJnN0UeLYFHb2_SICcc9MWiKLsAEBO2O2H_4ryJiobDj7_Bzg5hIR02kvE9PeSorPeSN19FkKxQ7tAObBd4wPwd6kZ0gUb4s3LkQ1w1PfE3nZOkCUEQuBrdQD1bjyaNLVYptkkYMApR2PwNSvp3LhgWCVgVv5eoDcg-OQDBTsG69KfrGFSveP6HvO5YjcasrG4WVkOmtV50BBI0bWOSsDfqicDOac-4L6P1RFlhb76vs7wf0ByI_yA52A',
    'Connection': 'keep-alive',
    # 'Cookie': 'PHPSESSID=t0fqh9tu473mssn7lk84uvuhpq',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

json_data = {
    'filter': {},
    'sort': {},
    'limit': {
        'lastId': 0,
        'maxResults': 4,
        'descending': True,
    },
}

response = requests.post(
    'https://birpay-gate.com/api/operator/refill_order/find',
    cookies=cookies,
    headers=headers,
    json=json_data,
)


data = response.json()
for row in data:
    for key, val in row.items():
        print(key, val)
print()
for key, val in data[0].items():
    print(key, val)