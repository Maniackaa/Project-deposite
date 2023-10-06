from aiogram import Bot


from config_data.bot_conf import conf


def get_my_loggers():
    from config_data.bot_conf import LOGGING_CONFIG
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('bot_logger'), logging.getLogger('errors_logger')


logger, err_log, *other_log = get_my_loggers()

last_send_error = ['']


async def send_alarm_to_admin(text: str, errors: list, bot: Bot):
    # Отправка сообщениий в телегу
    admin_ids = conf.tg_bot.admin_ids
    logger.debug(f'Отправка сообщений для {admin_ids}'
                 f'Текст:\n{text}\n\n'
                 f'errors: {errors}\n')
    error_text = (f'Ошибки при распознавании сообщения:\n'
                  f'<code>{text}</code>\n\n'
                  )

    error_text += '\n\n'.join(errors)
    if error_text != last_send_error[0]:
        for admin in admin_ids:
            try:
                print(error_text)
                await bot.send_message(chat_id=int(admin), text=error_text)
            except Exception as err:
                err_log.error(f'Ошибка отправки сообщения {admin}')
        last_send_error[0] = error_text
