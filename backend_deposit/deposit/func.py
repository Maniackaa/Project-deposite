import datetime
import logging

import cv2
import numpy as np
import pytesseract
from django.conf import settings
LOGCONFIG = settings.LOGCONFIG
TZ = settings.TZ
logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGCONFIG)


def get_unrecognized_field_error_text(response_fields, result):
    """Добавляет текст ошибки по полю если оно пустое (не распозналось)"""
    errors = []
    for field in response_fields:
        if not result.get(field):
            error_text = f'Не распознано поле {field} при распознавании шаблона {result.get("type")}'
            errors.append(error_text)
    return errors


def response_operations(fields: list[str], groups: tuple[str], response_fields, sms_type: str):
    result = dict.fromkeys(fields)
    result['type'] = sms_type
    errors = []
    for key, options in response_fields.items():
        try:
            value = groups[options['pos']].strip().replace(',', '')
            if options.get('func'):
                func = options.get('func')
                result[key] = func(value)
            else:
                result[key] = value
        except Exception as err:
            error_text = f'Ошибка распознавания поля {key}: {err}'
            logger.error(error_text)
            errors.append(error_text)

    errors.extend(get_unrecognized_field_error_text(response_fields, result))
    result['errors'] = errors
    return result


def img_path_to_str(file_bytes):
    try:
        logger.debug(f'Распознаем байты: {file_bytes[:100]}')
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(img, 215, 255, cv2.THRESH_BINARY)
        string = pytesseract.image_to_string(binary, lang='rus')
        string = string.replace('\n', ' ')
        logger.debug(f'Распознали')
        return string
    except Exception as err:
        logger.error(f'Ошибка в cv2 {err}')


def date_m10_response(data_text: str) -> datetime.datetime:
    """Преобразование строки m10 в datetime"""
    logger.debug(f'Распознавание даты из текста: {data_text}')
    try:
        native_datetime = datetime.datetime.strptime(data_text, '%d.%m.%Y %H:%M')
        response_data = TZ.localize(native_datetime)
        return response_data
    except Exception as err:
        logger.error(f'Ошибка распознавания даты из текста: {err}')
        raise err


def response_m10(fields, groups) -> dict[str, str | float]:
    """
    Функия распознавания шаблона m10
    :param fields: ['response_date', 'sender', 'recipient', 'bank', 'pay', 'balance', 'transaction', 'type', 'status']
    :param groups: ('25.08.2023 01:07', '+994 51 927 05 68', '+994 70 *** ** 27', '55555150', '5.00 м', 'Успешно ')
    :return: dict[str, str | float]
    """
    logger.debug('Преобразование текста m10')
    response_fields = {
        'response_date':    {'pos': 0, 'func': date_m10_response},
        'recipient':        {'pos': 1},
        'sender':           {'pos': 2},
        'pay':              {'pos': 4, 'func': lambda x: float(''.join([c if c in ['.', '-'] or c.isdigit() else '' for c in x]))},
        'transaction':      {'pos': 3, 'func': int},
        'status':           {'pos': 5},
    }
    sms_type = 'm10'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        logger.debug(result)
        return result
    except Exception as err:
        logger.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err


def response_m10_short(fields, groups) -> dict[str, str | float]:
    """
    Функия распознавания шаблона m10_short
    :param fields: ['response_date', 'recipient', 'bank', 'pay', 'balance', 'transaction', 'type', 'status']
    :param groups: ('27.08.2023 01:48', 'Пополнение С МИНОМ', '+994 51 927 05 68', '56191119', '10.00 м', 'Успешно')
    :return: dict[str, str | float]
    """
    logger.debug(f'Преобразование текста m10_short {groups}')
    response_fields = {
        'response_date':    {'pos': 0, 'func': date_m10_response},
        'recipient':        {'pos': 2},
        'sender':           {'pos': 1},
        'pay':              {'pos': 4, 'func': lambda x: float(''.join([c if c in ['.', '-'] or c.isdigit() else '' for c in x]))},
        'transaction':      {'pos': 3, 'func': int},
        'status':           {'pos': 5},
    }
    sms_type = 'm10_short'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        return result
    except Exception as err:
        logger.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err