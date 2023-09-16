import logging
import re


from deposit.func import response_m10, response_m10_short

logger = logging.getLogger(__name__)



def screen_text_to_pay(text):
    logger.debug(f'Распознаем текст {text}')
    patterns = {
        'm10': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).*Получатель (.*) Отправитель (.*) Код транзакции (\d+) Сумма (.+) Статус (.*) .*8',
        'm10_short': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).* (Пополнение.*) Получатель (.*) Код транзакции (\d+) Сумма (.+) Статус (\S+).*',
    }
    response_func = {
        'm10': response_m10,
        'm10_short': response_m10_short,
    }
    fields = ['response_date', 'recipient', 'sender', 'pay', 'balance',
              'transaction', 'type', 'status']
    text_sms_type = ''
    responsed_pay = {'status': '', 'type': '', 'errors': ''}
    errors = []
    status = ''
    for sms_type, pattern in patterns.items():
        logger.debug(f'Проверяем паттерн {sms_type}')
        search_result = re.findall(pattern, text)
        logger.debug(f'{search_result}: {bool(search_result)}')
        if search_result:
            logger.debug(f'Найдено: {sms_type}: {search_result}')
            text_sms_type = sms_type  # m10 / m10_short
            responsed_pay: dict = response_func[text_sms_type](fields, search_result[0])
            # errors = responsed_pay.pop('errors')
            # status = responsed_pay.pop('status')
            break
    return responsed_pay
    # Если шаблон распознан и статус не успешно:
    if status.lower() != 'успешно' and text_sms_type != '':
        text_sms_type = 'trash'

    if text_sms_type == 'trash':
        # Добавляем в мусор
        logger.debug('Статус не успешно. В мусор')
        trash_text = ' | '.join([f'{key}: {val}' for (key, val) in responsed_pay.items()])
        pass
        logger.debug('Кривой чек. В мусор')

    elif text_sms_type:
        # Шаблон распознан
        logger.debug(f'Сохраняем в базу {responsed_pay}')
        is_used_transaction = False

        if not is_used_transaction:
            # пробуем добавлять в базу
            is_add_to_db = True
            if is_add_to_db:
                logger.info(f'Сохранено базу {responsed_pay}')

            else:
                logger.debug(f'Не добавлено в базу!')
        else:
            # Действия с дубликатом
            logger.debug('Дубликат')

    else:
        # Шаблон не распознан
        logger.debug('Шаблон не распознан')

    if errors:
        pass

    return responsed_pay
