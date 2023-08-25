import re
import time
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from config_data.bot_conf import LOGGING_CONFIG, BASE_DIR, conf


import logging.config

from services.db_func import add_pay_to_db
from services.ocr_response_func import img_path_to_str, \
    response_m10
from services.support_func import send_alarm_to_admin
from services.text_response_func import response_sms1, response_sms2, \
    response_sms3

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot_logger')
err_log = logging.getLogger('errors_logger')

router: Router = Router()


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
            if await add_pay_to_db(responsed_pay):
                print('Добавлено в базу')
                await message.reply(f'Обработано. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
        else:
            await message.reply('Неизвестный шаблон!')
            logger.info(f'Добавляем в нераспознанное:\n {message.text}')

        if errors:
            await send_alarm_to_admin(text, errors, bot)
        print(f'{round(time.perf_counter() - start, 2)} сек.')
    except Exception as err:
        logger.error(f'Неизвестная ошибка при распознавании сообщения\n')
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
        print(text)
        patterns = {
            'm10': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).*Получатель (.*) Отправитель (.*) Код транзакции (\d+) Сумма (.+) Статус',
        }
        response_func = {
            'm10': response_m10,
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
                responsed_pay: dict = response_func[text_sms_type](fields,
                                                                   search_result[
                                                                       0])
                errors = responsed_pay.pop('errors')
                break
        if text_sms_type:
            logger.debug(f'Сохраняем в базу {responsed_pay}')
            if await add_pay_to_db(responsed_pay):
                logger.info(f'Сохранено базу {responsed_pay}')
                await message.reply(f'Добавлено в базу. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
            else:
                await message.reply(f'Дубликат. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
        else:
            for admin in conf.tg_bot.admin_ids:
                try:
                    await bot.send_message(admin, 'Не распознан скриншот')
                    await message.forward(chat_id=admin)
                except Exception as err:
                    pass

        if errors:
            await send_alarm_to_admin(text, errors, bot)
        print(f'{round(time.perf_counter() - start, 2)} сек.')
    except Exception as err:
        logger.error(f'Неизвестная ошибка при распознавании скриншота\n')
        await send_alarm_to_admin(message.text, [f'\nНеизвестная ошибка при распознавании скриншота!\n\n{err}'], bot)
        raise err
    finally:
        Path.unlink(img_path)


@router.message()
async def send_echo(message: Message):
    print('echo message:', message.content_type)


@router.callback_query()
async def send_echo(callback: CallbackQuery):
    print('echo callback:', callback)

