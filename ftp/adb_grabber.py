import subprocess
import time
from ftplib import FTP, all_errors
from pathlib import Path

from config_data.ftp_conf import get_my_loggers, ftp_conf

logger, *other = get_my_loggers()

BASE_DIR = Path(__file__).resolve().parent

SCREEN_FOLDER = ftp_conf.adb.SCREEN_FOLDER
TARGET_DIR = BASE_DIR / 'screenshots'


def adb_command(command):
    """
    Выполнение adb-команды и возврат вывода
    """
    print(command)
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    error.decode(), type(error.decode())
    if 'error: no devices/emulators found' in error.decode():
        logger.debug('no devices/emulators found')
        time.sleep(3)
    return output.decode('utf-8')


def get_file_list(directory):
    """
    Получение списка файлов из директории с их размерами
    """
    command = f'adb shell ls -l {directory}'
    files_output = adb_command(command)
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


def download_file(file_path, output_path):
    """
    Скачивание файла с устройства
    """
    command = f'adb pull -p {file_path} {output_path}'
    adb_command(command)


def delete_file(file_path):
    """
    Удаление файла с устройства
    """
    command = f'adb shell rm {file_path}'
    adb_command(command)


def main():
    while True:
        start = time.perf_counter()
        try:
            data = get_file_list(SCREEN_FOLDER.as_posix())
            logger.debug(f'Количество скринов: {len(data)}')
            if data:
                file, size = data[0][0], data[0][1]
                file_path = SCREEN_FOLDER / file
                if size > 0:
                    logger.debug(f'Скачиваем файл {file}')
                    download_file(file_path.as_posix(), './screenshots')
                    logger.debug(f'Удаляем файл {file}')
                    delete_file(file_path.as_posix())
            logger.debug(f'Время обработки файла: {time.perf_counter() - start}')
            time.sleep(0.5)
        except Exception as err:
            logger.debug(err)
            time.sleep(1)


if __name__ == '__main__':
    main()
