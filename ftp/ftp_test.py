import time
from ftplib import FTP, all_errors
from pathlib import Path

from config_data.bot_conf import get_my_loggers

logger, *other = get_my_loggers()

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)

while True:
    try:
        start = time.perf_counter()
        HOST = '192.168.1.226'
        PORT = 2121
        try:
            ftp = FTP()
            ftp.connect(HOST, PORT, timeout=5)
            ftp.login()
            ftp.cwd('/DCIM/Screenshots/')
            data = ftp.nlst()
            logger.debug(len(data))
            if data:
                file = data[0]
                with open(BASE_DIR / 'screenshots' / file, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {file}', local_file.write)
                    try:
                        ftp.delete(file)
                    except all_errors as error:
                        logger.debug(f'Error deleting file: {error}')

                logger.debug(data)
                logger.debug(time.perf_counter() - start)
            time.sleep(1)
        except Exception as err:
            logger.debug(err)

    except Exception as err:
        logger.debug(err)
        time.sleep(1)