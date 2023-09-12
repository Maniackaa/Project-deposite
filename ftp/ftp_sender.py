import time

import requests

from config_data.bot_conf import get_my_loggers
from ftp.config_data.ftp_conf import BASE_DIR

path = BASE_DIR / 'screenshots'


logger, err_log, *other = get_my_loggers()

files = list(path.glob('*.jpg'))
print(files)
for file in files:

    try:
        start = time.perf_counter()
        logger.debug(f'Отправляем {file.name, file.lstat().st_size}')
        binary = open(file, "rb")
        screen = {'image': binary}
        response = requests.post("http://localhost/api/screen/", data={'name': file.name}, files=screen)
        logger.debug(f'{response, response.status_code}')
        logger.debug(f'Время отправки: {time.perf_counter() - start}')
        binary.close()
        content = response.json()
        if response.status_code in [200, 201]:
            file.unlink()
        else:
            pass
        break
    except Exception as err:
        logger.error(err)