import time

import requests

from config_data.ftp_conf import get_my_loggers
from config_data.ftp_conf import BASE_DIR, ftp_conf

path = BASE_DIR / 'screenshots'

logger, err_log, *other = get_my_loggers()

ENDPOINT = ftp_conf.ftp.ENDPOINT
WORKER = ftp_conf.ftp.WORKER


def main():
    while True:
        try:
            files = list(path.glob('*.jpg'))
            for file in files:
                try:
                    start = time.perf_counter()
                    logger.debug(f'Отправляем {file.name, file.lstat().st_size}')
                    with open(file, "rb") as binary:
                        screen = {'image': binary}
                        response = requests.post(ENDPOINT, data={'name': file.name, 'WORKER': WORKER}, files=screen, timeout=1)
                        reason = response.reason
                        print(reason)
                        logger.debug(f'{response, response.status_code}')
                        logger.debug(f'Время отправки: {time.perf_counter() - start}')

                    if response.status_code in [200, 201]:
                        file.unlink()
                        logger.debug(f'Скрин удален')
                    else:
                        pass
                    break
                except Exception as err:
                    logger.error(f'Ошибка обработки файла {file.name}: {err}')
                    err_log.error(err, exc_info=True)
            time.sleep(0.1)

        except Exception as err:
            time.sleep(1)
            logger.eror(err)
            err_log.error(err, exc_info=True)


if __name__ == '__main__':
    main()
