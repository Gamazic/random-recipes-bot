import asyncio
import os

from motor.motor_asyncio import (AsyncIOMotorClient,
                                 AsyncIOMotorDatabase)
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.data.config import TG_TOKEN


io_loop = asyncio.get_event_loop()


def _connect_to_db() -> AsyncIOMotorDatabase:
    """Connecting to db with recipes.

    Returns:
        AsyncIOMotorDatabase: Mongo database
    """
    db_user = os.environ['MONGO_USER']
    db_password = os.environ['MONGO_PASSWORD']
    host = os.environ['MONGO_HOST']
    port = os.environ['MONGO_PORT']
    recipe_db_name = os.environ['MONGO_RECIPE_DB']

    connection_string = f'mongodb://{db_user}:{db_password}@{host}:{port}'
    client = AsyncIOMotorClient(connection_string, io_loop=io_loop)
    db = client[recipe_db_name]
    return db


db = _connect_to_db()


# bot = Bot(TG_TOKEN, loop=io_loop)
bot = Bot(TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
