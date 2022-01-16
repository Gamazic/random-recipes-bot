from aiogram.types.callback_query import CallbackQuery
from bson.objectid import ObjectId

from app.callback_data_schema import (DeleteRecipeCallbackData,
                                      RecipeDetailsCallbackData,
                                      UnuseRecipeCallbackData,
                                      UseRecipeCallbackData)
from app.callback_data_schema import is_valid_schema_for_callback


test_schema_classes = [
    DeleteRecipeCallbackData,
    RecipeDetailsCallbackData,
    UnuseRecipeCallbackData,
    UseRecipeCallbackData
    ]


def test_is_valid_schema_for_callback():
    random_object_id = ObjectId('666f6f2d6261722d71757578')
    id_data = {'id': random_object_id}
    for test_class in test_schema_classes:
        callback_data = test_class(**id_data)
        json_callback_data = callback_data.json()
        callback_query = CallbackQuery(data=json_callback_data)
        assert is_valid_schema_for_callback(callback_query, test_class) is True
