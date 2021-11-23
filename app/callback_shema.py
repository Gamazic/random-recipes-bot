from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel, ValidationError


class ActionCallbackData(BaseModel):
    action: str


class RecipeActionCallbackData(BaseModel):
    id: ObjectId
    action: str

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads


def is_valid_schema(raw_data: str, schema: BaseModel) -> bool:
    is_valid = True
    try:
        schema.parse_raw(raw_data)
    except ValidationError:
        is_valid = False
    return is_valid


class CallbackValidator:
    @staticmethod
    def validate_recipe_action_type(callback_data: str, action_type: str):
        is_recipe_action = is_valid_schema(callback_data, RecipeActionCallbackData)
        if is_recipe_action:
            parsed_data = RecipeActionCallbackData.parse_raw(callback_data)
            is_correct_action = (parsed_data.action == action_type)
            return is_correct_action
        else:
            return False

    @staticmethod
    def validate_action_type(callback_data: str, action_type: str):
        is_action = is_valid_schema(callback_data, ActionCallbackData)
        if is_action:
            parsed_data = ActionCallbackData.parse_raw(callback_data)
            is_correct_action = (parsed_data.action == action_type)
            return is_correct_action
        else:
            return False
