from typing import Union

from aiogram.types.callback_query import CallbackQuery
from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel, ValidationError


class ActionCallbackData(BaseModel):
    """
    Действие, которое выполняет InlineKeyboard
    """
    action: str


class RecipeIdCallbackData(BaseModel):
    """Id рецепта, над которым нужно совершить действие."""
    id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads


class RecipeDetailsCallbackData(ActionCallbackData, RecipeIdCallbackData):
    action: str = 'detail'


class UnuseRecipeCallbackData(ActionCallbackData, RecipeIdCallbackData):
    action: str = 'unuse'


class UseRecipeCallbackData(ActionCallbackData, RecipeIdCallbackData):
    action: str = 'use'


class DeleteRecipeCallbackData(ActionCallbackData, RecipeIdCallbackData):
    action: str = 'delete'


def is_valid_schema_for_callback(
    callback: CallbackQuery,
    schema: Union[ActionCallbackData, RecipeIdCallbackData]

) -> bool:
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
