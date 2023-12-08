import re
text = """+10 AZN\r\nPBMB C2C O\r\nBalans 170.01 AZN\r\nKart: *4197"""
text = text.replace('\r\n', '\n')
print(repr(text))
sms7 = r'(.+) AZN.*\n(.*)\nBalans (.*) AZN\nKart:(.*)'
search_result = re.findall(sms7, text)
print(search_result)
