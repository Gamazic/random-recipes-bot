from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel, ValidationError
from aiogram.types.callback_query import CallbackQuery


class CallbackData(BaseModel):
    action: str


class RecipeIdCallbackData(BaseModel):
    id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads


class RecipeDetailsCallbackData(CallbackData, RecipeIdCallbackData):
    action: str = 'detail'


class UnuseRecipeCallbackData(CallbackData, RecipeIdCallbackData):
    action: str = 'unuse'


class UseRecipeCallbackData(CallbackData, RecipeIdCallbackData):
    action: str = 'use'


class DeleteRecipeCallbackData(CallbackData, RecipeIdCallbackData):
    action: str = 'delete'


def is_valid_schema(callback: CallbackQuery, schema: CallbackData) -> bool:
    """Проверяет, подходит ли json raw_data к схеме schema

    Args:
        raw_data (str): json с колбэком.
        schema (CallbackData): Одна из схем CallbackData

    Returns:
        bool: Если json образован от schema - возвращает True. Иначе False.
    """
    raw_data = callback.data
    try:
        callback_data = schema.parse_raw(raw_data)
    except ValidationError:
        return False
    is_same_action = (schema.__fields__['action'].default == callback_data.action)
    return is_same_action
