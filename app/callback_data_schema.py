from typing import Union

from aiogram.types.callback_query import CallbackQuery
from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel, ValidationError


class ActionCallbackData(BaseModel):
    """
    The action that performce InlineKeyboard.
    """
    action: str


class RecipeIdCallbackData(BaseModel):
    """ID of the recipe to perform the action on."""
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
    """Check whether callback query matched to schema.

    Args:
        callback (CallbackQuery): telegram callback query.
        schema (ActionCallbackData | RecipeIdCallbackData): one of the shemes

    Returns:
        bool: True if callback is formed by schema. Otherwise False.
    """
    raw_data = callback.data
    try:
        callback_data = schema.parse_raw(raw_data)
    except ValidationError:
        return False
    is_same_action = (schema.__fields__['action'].default == callback_data.action)
    return is_same_action
