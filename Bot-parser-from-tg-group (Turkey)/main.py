import asyncio
import datetime

from aiogram import Bot, Dispatcher


from handlers import bot_handlers

from config_data.bot_conf import LOGGING_CONFIG, conf
import logging.config

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot_logger')
err_log = logging.getLogger('errors_logger')


async def main():
    logger.info('Starting bot')
    bot: Bot = Bot(token=conf.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Регистриуем
    dp.include_router(bot_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        if conf.tg_bot.admin_ids:
            await bot.send_message(
                conf.tg_bot.admin_ids[0], f'Бот запущен.\n{datetime.datetime.now()}')
    except Exception:
        err_log.error(f'Не могу отравить сообщение {conf.tg_bot.admin_ids[0]}')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')