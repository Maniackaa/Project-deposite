import datetime
import cv2
import numpy as np
import pytesseract

from config_data.bot_conf import tz
from services.text_response_func import response_operations


def get_my_loggers():
    from config_data.bot_conf import LOGGING_CONFIG
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('bot_logger'), logging.getLogger('errors_logger')


logger, err_log = get_my_loggers()


def img_path_to_str(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    string = pytesseract.image_to_string(binary, lang='rus')
    string = string.replace('\n', ' ')
    return string


def date_m10_response(data_text: str) -> datetime.datetime:
    """Преобразование строки m10 в datetime"""
    logger.debug(f'Распознавание даты из текста: {data_text}')
    try:
        native_datetime = datetime.datetime.strptime(data_text, '%d.%m.%Y %H:%M')
        response_data = tz.localize(native_datetime)
        return response_data
    except Exception as err:
        err_log.error(f'Ошибка распознавания даты из текста: {err}')
        raise err


def response_m10(fields, groups) -> dict[str, str | float]:
    """
    Функия распознавания шаблона m10
    :param fields: ['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type']
    :param groups: ('25.08.2023 01:07', '+994 51 927 05 68', '+994 70 *** ** 27', '55555150', '5.00 м')
    :return: dict[str, str | float]
    """
    logger.debug('Преобразование текста m10')
    response_fields = {
        'response_date':    {'pos': 0, 'func': date_m10_response},
        'sender':           {'pos': 2},
        'pay':              {'pos': 4, 'func': lambda x: float(''.join([c if c in ['.'] or c.isdigit() else '' for c in x]))},
        'transaction':      {'pos': 3, 'func': int},
    }
    sms_type = 'm10'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        return result
    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err

# response_m10(['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type'], ('25.08.2023 01:07', '+994 51 927 05 68', '+994 70 *** ** 27', '55555150', '5.00 м'))