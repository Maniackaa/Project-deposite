import re
import time
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config_data.bot_conf import LOGGING_CONFIG, BASE_DIR, conf


import logging.config

from services.birpay_func import find_birpay_transaction
from services.db_func import add_pay_to_db, check_transaction, add_to_trash
from services.ocr_response_func import img_path_to_str, \
    response_m10, response_m10_short
from services.support_func import send_alarm_to_admin
from services.text_response_func import response_sms1, response_sms2, \
    response_sms3, response_sms4, response_sms5

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
        message_url = message.get_url(force_private=True)
        patterns = {
            'sms1': r'^Imtina:(.*)\nKart:(.*)\nTarix:(.*)\nMercant:(.*)\nMebleg:(.*) .+\nBalans:(.*) ',
            'sms2': r'.*Mebleg:(.+) AZN.*\nKart:(.*)\nTarix:(.*)\nMerchant:(.*)\nBalans:(.*) .*',
            'sms3': r'^.+[medaxil|mexaric] (.+?) AZN (.*)(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).+Balance: (.+?) AZN.*',
            'sms4': r'^Amount:(.+?) AZN[\n]?.*\nCard:(.*)\nDate:(.*)\nMerchant:(.*)\nBalance:(.*) .*',
            'sms5': r'.*Mebleg:(.+) AZN.*\nMedaxil Card to card (.*)\nUnvan: (.*)\n(.*)\nBalans: (.*) AZN'
        }
        response_func = {
            'sms1': response_sms1,
            'sms2': response_sms2,
            'sms3': response_sms3,
            'sms4': response_sms4,
            'sms5': response_sms5,
        }
        fields = ['response_date', 'recipient', 'sender', 'pay', 'balance',
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

        responsed_pay['message_url'] = message_url
        if text_sms_type:
            logger.info(f'Сохраняем в базу {responsed_pay}')
            addet = add_pay_to_db(responsed_pay)
            if addet is True:
                print('Добавлено в базу')
                await message.reply(f'Обработано. Шаблон {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
            elif addet == 'duplicate':
                logger.debug('Дупликат смс')
                await message.reply(
                    f'Обработано. Дубликат {text_sms_type} за {round(time.perf_counter() - start, 2)} сек.')
            else:
                await message.reply('Неизвестная ошибка')
        else:
            await message.reply('Неизвестный шаблон!')
            logger.info(f'Добавляем в нераспознанное:\n {message.text}')
            add_to_trash(message.text)

            if not message.text.startswith('OTP kod'):
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
    logger.debug('\nПолучено фото')
    try:
        chat_type = message.chat.type
        message_url = message.get_url(force_private=True)
        start = time.perf_counter()
        if message.content_type == 'photo':
            img_id = message.photo[-1].file_id
            img_path = BASE_DIR / 'photos' / f'{img_id}.jpg'
            await bot.download(message.photo[-1], destination=img_path)
        if message.content_type == 'document':
            img_id = message.document.file_id
            img_path = BASE_DIR / 'photos' / f'{img_id}.jpg'
            await bot.download(message.document, destination=img_path)
        text = img_path_to_str(img_path)
        logger.debug(f'Распозано с фото:{text}')
        patterns = {
            'm10': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).*Получатель (.*) Отправитель (.*) Код транзакции (\d+) Сумма (.+) Статус (.*) .*8',
            'm10_short': r'.*(\d\d\.\d\d\.\d\d\d\d \d\d:\d\d).* (Пополнение.*) Получатель (.*) Код транзакции (\d+) Сумма (.+) Статус (\S+).*',
        }
        response_func = {
            'm10': response_m10,
            'm10_short': response_m10_short,
        }
        fields = ['response_date', 'recipient', 'sender', 'bank', 'pay', 'balance',
                  'transaction', 'type', 'status']
        text_sms_type = ''
        responsed_pay = {}
        errors = []
        status = ''
        for sms_type, pattern in patterns.items():
            logger.debug(f'Проверяем паттерн {sms_type}')
            search_result = re.findall(pattern, text)
            logger.debug(f'{search_result}: {bool(search_result)}')
            if search_result:
                logger.debug(f'Найдено: {sms_type}: {search_result}')
                text_sms_type = sms_type
                responsed_pay: dict = response_func[text_sms_type](fields, search_result[0])
                errors = responsed_pay.pop('errors')
                status = responsed_pay.pop('status')
                break

        responsed_pay['message_url'] = message_url

        # Если шаблон распознан и статус не успешно:
        if status.lower() != 'успешно' and text_sms_type != '':
            text_sms_type = 'trash'

        if text_sms_type == 'trash':
            # Добавляем в мусор
            logger.debug('Статус не успешно. В мусор')
            trash_text = ' | '.join([f'{key}: {val}' for (key, val) in responsed_pay.items()])
            add_to_trash(trash_text)
            await message.reply('Кривой чек. В мусор')

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

                    # Пробуем найти birpay
                    try:
                        birpay = find_birpay_transaction(responsed_pay)
                        if birpay:
                            await message.reply(f'Возможный bitpay_id: <code>{birpay}</code>')
                    except Exception as err:
                        logger.error(f'Ошибка при поиске birpay: {err}')

                else:
                    logger.debug(f'Не добавлено в базу!')
            else:
                # Действия с дубликатом
                logger.debug('Дубликат')
                try:
                    if chat_type != 'private':
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

        if chat_type == 'private':
            resp_text = 'Распознано:\n\n'
            for key, val in responsed_pay.items():
                if val:
                    resp_text += str(val) + '\n'
            await message.answer(resp_text)

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

