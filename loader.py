import asyncio

from motor.motor_asyncio import (AsyncIOMotorClient,
                                 AsyncIOMotorDatabase)
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from app.data.config import TG_TOKEN, MONGO_URI, MONGO_RECIPE_DB_NAME


def _connect_to_db() -> AsyncIOMotorDatabase:
    """Connecting to db with recipes.

    Returns:
        AsyncIOMotorDatabase: Mongo database
    """
    client = AsyncIOMotorClient(MONGO_URI, io_loop=io_loop)
    client.get_io_loop = asyncio.get_running_loop
    db = client[MONGO_RECIPE_DB_NAME]
    return db


io_loop = asyncio.get_event_loop()

db_connection = _connect_to_db()

bot = Bot(TG_TOKEN, loop=io_loop)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logger.add("logs/recipe_bot.log", rotation="5 MB")
