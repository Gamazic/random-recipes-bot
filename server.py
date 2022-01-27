import ssl
import argparse

from aiogram import executor

from app.data.config import (WEBAPP_HOST, WEBAPP_PORT,
                             WEBHOOK_PATH, WEBHOOK_URL, WEBHOOK_SSL_CERT,
                             WEBHOOK_SSL_PRIV)
from loader import bot, logger
from app.handlers import dp


parser = argparse.ArgumentParser(description='Start bot via polling or webhook')
parser.add_argument('-e', '--executor-type', type=str,
                    help='`polling` or `webhook`')


def start_polling():
    logger.info("Bot starts with polling.")
    executor.start_polling(dp, skip_updates=True)


def start_webhook():
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
    logger.info("Bot starts with webhook.")
    executor.start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_webhook_startup,
                           skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)


async def on_webhook_startup(app):
    webhook = await bot.get_webhook_info()

    if webhook.url != WEBHOOK_URL:
        if not webhook.url:
            await bot.delete_webhook()

        await bot.set_webhook(WEBHOOK_URL, certificate=open(WEBHOOK_SSL_CERT, 'rb'))


if __name__ == '__main__':
    args = parser.parse_args()
    executor_type = args.executor_type
    if executor_type == 'polling':
        start_polling()
    elif executor_type == 'webhook':
        start_webhook()
    else:
        raise argparse.ArgumentError('Bad value for executor type argument')
