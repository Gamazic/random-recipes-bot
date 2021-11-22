from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel


class ActionCallbackData(BaseModel):
    action: str


class RecipeDetailsCallbackData(BaseModel):
    id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads


class RecipeActionCallbackData(BaseModel):
    action: str
    id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads


class CallbackValidator:
    @staticmethod
    def parse_callback_data(callback_data):
        parsed_data = json_util.loads(callback_data)
        if 'action' in parsed_data:
            callback_data = ActionCallbackData(**parsed_data)
        elif 'id' in parsed_data:
            callback_data = RecipeDetailsCallbackData(**parsed_data)
        return callback_data

    @staticmethod
    def recipe_details(callback_data):
        parsed_data = json_util.loads(callback_data)
        return ('id' in parsed_data) and ('action' not in parsed_data)

    @staticmethod
    def recipe_action(callback_data):
        parsed_data = json_util.loads(callback_data)
        return ('id' in parsed_data) and ('action' in parsed_data)

    @staticmethod
    def change_recipe(callback_data):
        is_recipe_action = CallbackValidator.recipe_action(callback_data)
        parsed_data = json_util.loads(callback_data)
        is_change_action = parsed_data['action'] == 'change'
        return is_recipe_action and is_change_action

    @staticmethod
    def delete_recipe(callback_data):
        is_recipe_action = CallbackValidator.recipe_action(callback_data)
        parsed_data = json_util.loads(callback_data)
        is_change_action = parsed_data['action'] == 'delete'
        return is_recipe_action and is_change_action

    @staticmethod
    def action(callback_data):
        parsed_data = json_util.loads(callback_data)
        return ('id' not in parsed_data) and ('action' in parsed_data)
