import requests

# cookies = {
#     'PHPSESSID': '30b7kecfdhlrdcksbfrbutpcoj',
# }
cookies = None

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2OTY1MDgzNTYsImV4cCI6MTY5NjUzOTYwMCwicm9sZXMiOlsiUk9MRV9PUEVSQVRPUiJdLCJ1c2VybmFtZSI6Ik9wZXJhdG9yNl9aYWpvbl9BWk4ifQ.Sgfm2o2ZjWqIVCgVZJe206M2nxX8sv4A1WJ8s9bn-iVY_9jXogGGsMhEl2ODLuEnllE9JvlUA467k3ksYQfMgKQ3PmC6oPEOZH-OlERAX-abldrkwobSfh_ibhZMU04i0IMYNUOOZTXyzw-VL8AAO3laja-hbRwdxXAc7qWpd2-4LxbGeeGsrsggEEUlZh5S86jOK-0kVSZeG299iwemvxDy_Iict0be6se1zGdwk_XqUSZfSePaesngN7TcBZf8vOPEZc8GXVRE-_mzJaCpddGYFFcDadtQ5d-ReQW2RVTTKjXdLFYHZ39PbtJf76sJ1X8BJw4sndfeOnxr3MOuSQ',
    'Content-Type': 'application/json;charset=utf-8',
    'Origin': 'https://birpay-gate.com',
    'Connection': 'keep-alive',
    'Referer': 'https://birpay-gate.com/login',
    # 'Cookie': 'PHPSESSID=30b7kecfdhlrdcksbfrbutpcoj',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

json_data = {
    'username': 'Operator6_Zajon_AZN',
    'password': 'hRQLVYCJ',
}

response = requests.post('https://birpay-gate.com/api/login_check', cookies=cookies, headers=headers, json=json_data)
print(response)
print(response.text)
print(response.json())