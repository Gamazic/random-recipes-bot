import os


TG_TOKEN = os.environ['TG_TOKEN']

WEBHOOK_HOST = os.environ['WEBHOOK_HOST']
WEBHOOK_PATH = os.environ['WEBHOOK_PATH']
WEBHOOK_PORT = os.environ['WEBHOOK_PORT']
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

WEBAPP_HOST = os.environ['WEBAPP_HOST']
WEBAPP_PORT = os.environ['WEBAPP_PORT']

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

MONGO_USER = os.environ['MONGO_USER']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = os.environ['MONGO_PORT']
MONGO_RECIPE_DB_NAME = os.environ['MONGO_RECIPE_DB']
MONGO_URI = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}'
