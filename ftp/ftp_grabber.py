import time
from ftplib import FTP, all_errors
from pathlib import Path

from config_data.ftp_conf import get_my_loggers, ftp_conf

logger, *other = get_my_loggers()

BASE_DIR = Path(__file__).resolve().parent


def main():
    while True:
        start = time.perf_counter()
        try:
            ftp = FTP()
            ftp.connect(ftp_conf.ftp.FTP_HOST, ftp_conf.ftp.FTP_PORT, timeout=ftp_conf.ftp.FTP_TIMEOUT)
            ftp.login(user=ftp_conf.ftp.FTP_USER, passwd=ftp_conf.ftp.FTP_PASSWD)
            ftp.cwd(ftp_conf.ftp.SCREEN_FOLDER)
            data = ftp.nlst()
            logger.debug(f'Количество скринов: {len(data)}')
            if data:
                file = data[0]
                logger.debug(f'Скачиваем файл {file}')
                with open(BASE_DIR / 'screenshots' / file, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {file}', local_file.write)
                    try:
                        ftp.delete(file)
                    except all_errors as error:
                        logger.debug(f'Ошибка при удалении файла {file}: {error}')
            logger.debug(f'Время обработки файла: {time.perf_counter() - start}')
            time.sleep(0.1)
        except Exception as err:
            logger.debug(err)
            time.sleep(1)


if __name__ == '__main__':
    main()
