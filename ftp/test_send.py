import requests

from config_data.bot_conf import get_my_loggers
from ftp.config_data.bot_conf import BASE_DIR

path = BASE_DIR / 'screenshots'
files = list(path.glob('*.jpg'))

logger, err_log, *other = get_my_loggers()
print(other)

for file in files:
    try:
        logger.debug(f'{file.name, file.lstat().st_size}')
        binary = open(file, "rb")
        screen = {'image': binary}
        response = requests.post("http://localhost/api/screen/", data={'name': file.name}, files=screen)
        binary.close()
        logger.debug(f'{response, response.status_code}')
        content = response.json()
        if response.status_code == 201:
            file.unlink()
        else:
            pass
    except Exception as err:
        logger.error(err)