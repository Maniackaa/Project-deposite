import re
import time
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config_data.bot_conf import LOGGING_CONFIG, BASE_DIR, conf


import logging.config

from services.db_func import add_pay_to_db, check_transaction, add_to_trash
from services.ocr_response_func import img_path_to_str, \
    response_m10, response_m10_short
from services.support_func import send_alarm_to_admin
from services.text_response_func import response_sms1, response_sms2, \
    response_sms3

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot_logger')
err_log = logging.getLogger('errors_logger')

router: Router = Router()


@router.message(Command('start'))
async def sms_receiver(message: Message, bot: Bot):
    await message.answer('Бот запущен')


@router.message(F.text)
async def sms_receiver(message: Message, bot: Bot):
    # Распознование текстовых сообщений
    start = time.perf_counter()
    print()
    print(message.text)
    print()
    try:
        text = message.text
        patterns = {
            'sms1': r'^Imtina:(.*)\nKart:(.*)\nTarix:(.*)\nMercant:(.*)\nMebleg:(.*) .+\nBalans:(.*) ',
            'sms2': r'^Mebleg:(.+) AZN.*\nKart:(.*)\nTarix:(.*)\nMerchant:(.*)\nBalans:(.*) .*',
            'sms3': r'^.+medaxil (.+?) AZN (.*)(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).+Balance: (.+?) AZN.*',
        }
        response_func = {
            'sms1': response_sms1,
            'sms2': response_sms2,
            'sms3': response_sms3,
        }
        fields = ['response_date', 'sender', 'bank', 'pay', 'balance',
                  'transaction', 'type']
        text_sms_type = ''
        responsed_pay = {}
        errors = []
        for sms_type, pattern in patterns.items():
            search_result = re.findall(pattern, text)
            if search_result:
                logger.debug(f'Найдено: {sms_type}: {search_result}')
                text_sms_type = sms_type
                responsed_pay: dict = response_func[text_sms_type](fields, search_result[0])
                errors = responsed_pay.pop('errors')
                break

        if text_sms_type:
            logger.info(f'Сохраняем в базу {responsed_pay}')
            addet = add_pay_to_db(responsed_pay)
            if addet:
                print('Добавлено в базу')
                await message.reply(f'Обработано. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
        else:
            await message.reply('Неизвестный шаблон!')
            logger.info(f'Добавляем в нераспознанное:\n {message.text}')
            add_to_trash(message.text)

            for admin in conf.tg_bot.admin_ids:
                try:
                    await bot.send_message(admin, 'Не распознано сообщение')
                    await message.forward(chat_id=admin)
                except Exception as err:
                    print(err)
                    pass

        if errors:
            await send_alarm_to_admin(text, errors, bot)
        print(f'{round(time.perf_counter() - start, 2)} сек.')
    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании сообщения\n', exc_info=True)
        await send_alarm_to_admin(message.text, [f'\nНеизвестная ошибка при распознавании сообщения\n{message.text}\n\n{err}'], bot)
        raise err


# Распознавание чеков
@router.message(F.content_type.in_({'photo', 'document'}))
async def ocr_photo(message: Message, bot: Bot):
    try:
        start = time.perf_counter()
        if message.content_type == 'photo':
            img_id = message.photo[-1].file_id
            img_path = BASE_DIR / 'photos' / f'{img_id}.jpg'
            await bot.download(message.photo[-1], destination=img_path)
        if message.content_type == 'document':
            print(message.document)
            img_id = message.document.file_id
            img_path = BASE_DIR / 'photos' / f'{img_id}.jpg'
            await bot.download(message.document, destination=img_path)
        text = img_path_to_str(img_path)
        print('text', text)
        patterns = {
            'm10': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).*Получатель (.*) Отправитель (.*) Код транзакции (\d+) Сумма (.+) Статус',
            'm10_short': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).* (Пополнение.*) Получатель (.*) Код транзакции (\d+) Сумма (.+) Статус',
        }
        response_func = {
            'm10': response_m10,
            'm10_short': response_m10_short,
        }
        fields = ['response_date', 'sender', 'bank', 'pay', 'balance',
                  'transaction', 'type']
        text_sms_type = ''
        responsed_pay = {}
        errors = []
        for sms_type, pattern in patterns.items():
            search_result = re.findall(pattern, text)
            if search_result:
                logger.debug(f'Найдено: {sms_type}: {search_result}')
                text_sms_type = sms_type
                responsed_pay: dict = response_func[text_sms_type](fields, search_result[0])
                errors = responsed_pay.pop('errors')
                break
        if responsed_pay.get('sender') == '':
            text_sms_type = 'trash'

        if text_sms_type == 'trash':
            # Добавляем в мусор
            logger.debug('Пустой отправитель. В мусор')
            trash_text = ' | '.join([f'{key}: {val}' for (key, val) in responsed_pay.items()])
            add_to_trash(trash_text)
            await message.reply('Пустой отправитель. В мусор')

        elif text_sms_type:
            # Шаблон распознан
            logger.debug(f'Сохраняем в базу {responsed_pay}')
            is_used_transaction = check_transaction(responsed_pay['transaction'])

            if not is_used_transaction:
                # пробуем добавлять в базу
                is_add_to_db = add_pay_to_db(responsed_pay)
                if is_add_to_db:
                    logger.info(f'Сохранено базу {responsed_pay}')
                    await message.reply(f'Добавлено в базу. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
                else:
                    logger.debug(f'Не добавлено в базу!')
            else:
                # Действия с дубликатом
                logger.debug('Дубликат')
                try:
                    await message.delete()
                except:
                    pass
        else:
            # Шаблон не распознан
            logger.debug('Шаблон не распознан')
            for admin in conf.tg_bot.admin_ids:
                try:
                    await bot.send_message(chat_id=int(admin), text='Не распознан скриншот')
                    await message.forward(chat_id=admin)
                except Exception as err:
                    print(err)
                    raise err
                    pass

        if errors:
            await send_alarm_to_admin(text, errors, bot)
        print(f'{round(time.perf_counter() - start, 2)} сек.')

    except Exception as err:
        err_log.error(f'Неизвестная ошибка при распознавании скриншота\n', exc_info=True)
        await send_alarm_to_admin(message.text, [f'\nНеизвестная ошибка при распознавании скриншота!\n\n{err}'], bot)

    finally:
        Path.unlink(img_path)


@router.message()
async def send_echo(message: Message):
    print('echo message:', message.content_type)


@router.callback_query()
async def send_echo(callback: CallbackQuery):
    print('echo callback:', callback)

