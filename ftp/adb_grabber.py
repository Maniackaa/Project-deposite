
import time
from pathlib import Path

from adbutils import AdbClient

from config_data.ftp_conf import get_my_loggers, ftp_conf

logger, *other = get_my_loggers()

BASE_DIR = Path(__file__).resolve().parent

SCREEN_FOLDER = Path(ftp_conf.adb.SCREEN_FOLDER)
TARGET_DIR = BASE_DIR / 'screenshots'


def get_file_list(directory, adb_device):
    """
    Получение списка файлов из директории с их размерами
    """
    command = f'ls -l {directory}'
    files_output = adb_device.shell(command)
    files = files_output.splitlines()
    file_list = []
    for file in files:
        if file.startswith('total'):
            continue
        items = file.split()
        if len(items) >= 5:
            file_name = items[-1]
            file_size = int(items[4])
            file_list.append((file_name, file_size))
    return file_list


def main():

    while True:
        adb_client = AdbClient(host="host.docker.internal", port=5037)
        # adb_client = AdbClient(host="127.0.0.1", port=5037)
        adb_devices = adb_client.device_list()
        print(adb_devices)
        if adb_devices:
            adb_device = adb_devices[0]
        else:
            time.sleep(5)
            continue
        start = time.perf_counter()
        try:
            data = get_file_list(SCREEN_FOLDER.as_posix(), adb_device)
            logger.debug(f'Количество скринов: {len(data)}')
            logger.debug(str(data))
            if data:
                file, size = data[0][0], data[0][1]
                file_path = SCREEN_FOLDER / file
                if size > 0:
                    logger.debug(f'Скачиваем файл {file} {size} кб')
                    target_path = TARGET_DIR / file
                    downloaded = adb_device.sync.pull(file_path.as_posix(), target_path.as_posix())
                    if downloaded:
                        logger.debug(f'Удаляем файл {file}: {downloaded}')
                        adb_device.shell(f'rm {file_path.as_posix()}')
            # logger.debug(f'Время обработки файла: {time.perf_counter() - start}')
            time.sleep(0.5)
        except Exception as err:
            logger.debug(err, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
