import time

import requests

from config_data.bot_conf import get_my_loggers
from ftp.config_data.ftp_conf import BASE_DIR

path = BASE_DIR / 'screenshots'

logger, err_log, *other = get_my_loggers()
endpoint = 'http://127.0.0.1:8000/api/screen/'

worker = 'station 1'
def main():
    while True:
        try:
            files = list(path.glob('*.jpg'))
            for file in files:
                try:
                    start = time.perf_counter()
                    logger.debug(f'Отправляем {file.name, file.lstat().st_size}')
                    binary = open(file, "rb")
                    screen = {'image': binary}
                    response = requests.post(endpoint, data={'name': file.name, 'worker': worker}, files=screen)
                    logger.debug(f'{response, response.status_code}')
                    logger.debug(f'Время отправки: {time.perf_counter() - start}')
                    content = response.json()
                    logger.debug(f'content: {content}')
                    binary.close()
                    if response.status_code in [200, 201]:
                        file.unlink()
                        logger.debug(f'Скрин удален')
                    else:
                        pass
                except Exception as err:
                    logger.eror(f'Ошибка обработки файла {file.name}: {err}')
                    err_log.error(err, exc_info=True)
            time.sleep(1)

        except Exception as err:
            logger.eror(err)
            err_log.error(err, exc_info=True)


if __name__ == '__main__':
    main()
