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
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2OTY1MDg1NTgsImV4cCI6MTY5NjUzOTYwMCwicm9sZXMiOlsiUk9MRV9PUEVSQVRPUiJdLCJ1c2VybmFtZSI6Ik9wZXJhdG9yNl9aYWpvbl9BWk4ifQ.cx6fD1o2bAmEJkmTS-CaSWg4ylYkTlq4wdIMmB1Q72Qx2tbnj_r8rKd7Ty016YMdLeqgw3dBKGjma8TnheGlHttn8lacP8abGZy-YvCSenB_ChTsIq_9zeSLSHEmQNnQAVntbm_AvtDIb8aIuLaK4q8-UrLcsBPxt2YO1Vk7u2lODZbdbmNbeNWZBwxK1haZjyBMIE1Vo35BiUZiDc9uRxc4zONxBm89Xuwx2BOBsqSRE-V5kIOK6Q8ylzI4s3jOkEANp0ugNYK9YzKxZEmXd_WqDDtCONCmoxEEawfB_oeVR9JDXmMdVJVm3_G_9a9C3pJ23b4PDEsJlx4CaDs1qg',
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

print(response.text)
data = response.json()
print(data)
for row in data:
    for key, val in row.items():
        print(key, val)
print()
for key, val in data[0].items():
    print(key, val)