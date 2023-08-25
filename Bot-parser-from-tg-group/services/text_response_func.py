import datetime

from config_data.bot_conf import tz


def get_my_loggers():
    from config_data.bot_conf import LOGGING_CONFIG
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('bot_logger'), logging.getLogger('errors_logger')


logger, err_log = get_my_loggers()


def get_unrecognized_field_error_text(response_fields, result):
    """Добавляет текст ошибки по полю если оно пустое (не распозналось)"""
    errors = []
    for field in response_fields:
        if not result.get(field):
            error_text = f'Не распознано поле {field} при распознавании шаблона {result.get("type")}'
            errors.append(error_text)
    return errors


def date_response(data_text: str) -> datetime.datetime:
    """Преобразование строки в datetime"""
    logger.debug(f'Распознавание даты из текста: {data_text}')
    try:
        native_datetime = datetime.datetime.fromisoformat(data_text.strip()) - datetime.timedelta(hours=1)
        response_data = tz.localize(native_datetime)
        return response_data
    except Exception as err:
        err_log.error(f'Ошибка распознавания даты из текста: {err}')
        raise err


# date_response('2023-08-19 12:30:14')


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


def float_digital(string):
    result = ''.join([c if c in ['.', '-'] or c.isdigit() else '' for c in string])
    return float(result)


def response_sms1(fields: list[str], groups: tuple[str]) -> dict[str, str | float]:
    """
    Функия распознавания шаблона 1
    :param fields: ['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type']
    :param groups: ('Bloklanmish kart', '4127***6869', '2023-08-22 15:17:19', 'P2P SEND- LEO APP', '29.00', '569.51')
    :return: dict[str, str | float]
    """
    logger.debug('Распознавание шаблона sms1')
    response_fields = {
        'response_date':    {'pos': 2, 'func': date_response},
        'sender':           {'pos': 1},
        'bank':             {'pos': 3},
        'pay':              {'pos': 4, 'func': float_digital},
        'balance':          {'pos': 5, 'func': float_digital},
    }
    sms_type = 'sms1'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        return result
    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err


# x = response_sms1(['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type'], ('Bloklanmish kart', '4127***6869', '2023-08-22 25:17:19', 'P2P SEND- LEO APP', '29.00', '569.51'))
# print(x)


def response_sms2(fields, groups) -> dict[str, str | float]:
    """
    Функия распознавания шаблона 1
    :param fields: ['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type']
    :param groups: ('+80.00', '4127*6869', '2023-08-22 15:17:19', 'P2P SEND- LEO APP', '569.51')
    :return: dict[str, str | float]
    """
    response_fields = {
        'response_date':    {'pos': 2, 'func': date_response},
        'sender':           {'pos': 1},
        'bank':             {'pos': 3},
        'pay':              {'pos': 0, 'func': float_digital},
        'balance':          {'pos': 4, 'func': float_digital},
    }
    sms_type = 'sms2'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        return result
    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err

sms2 = response_sms2(['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type'], ('-1 080.00', '4127*6869', '2023-08-22 15:17:19', 'P2P SEND- LEO APP', '569.51'))
print(sms2)

def response_sms3(fields, groups) -> dict[str, str | float]:
    """
    Функия распознавания шаблона 1
    :param fields: ['response_date', 'sender', 'bank', 'pay', 'balance', 'transaction', 'type']
    :param groups: ('5.00', '1000020358154 terminal payment ', '2023-08-19 02:30:14', '319.38')
                   ('10.01', 'ACCOUNT TO ACCOUNT TRANSFER   ', '2023-08-23 00:00:00', '222.96')
    :return: dict[str, str | float]
    """
    response_fields = {
        'response_date':    {'pos': 2, 'func': date_response},
        'sender':           {'pos': 1, 'func': lambda x: x.split('terminal payment')[0].strip() if 'terminal payment' in x else x},
        'bank':             {'pos': 0, 'func': lambda x: 'Hesaba medaxil'},
        'pay':              {'pos': 0, 'func': float_digital},
        'balance':          {'pos': 3, 'func': float_digital},
    }
    sms_type = 'sms3'
    try:
        result = response_operations(fields, groups, response_fields, sms_type)
        return result
    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании: {fields, groups} ({err})')
        raise err



