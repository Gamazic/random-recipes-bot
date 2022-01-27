from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from pydantic import BaseModel

from app.callback_data_schema import (DeleteRecipeCallbackData,
                                      RecipeDetailsCallbackData,
                                      UnuseRecipeCallbackData,
                                      UseRecipeCallbackData)
from app.recipe_shema import RecipeWithId
from app.data.messages_text import (MARK_AS_UNUSED_RECIPE_BUTTON_TEXT,
                                    MARK_AS_USED_RECIPE_BUTTON_TEXT,
                                    DELETE_RECIPE_BUTTON_TEXT)


def create_inline_keyboard_button(
    button_text: str,
    callback_class: BaseModel,
    callback_data: dict = {}
) -> InlineKeyboardMarkup:
    """Creates an inline bot keyboard button.
    The json generated from the callback_class instance is written to the callback.

    Args:
        button_text (str): button text.
        callback_class (BaseModel): callback data schema.
        callback_data (dict): callback data for schema.

    Returns:
        InlineKeyboardMarkup: telegram bot button.
    """
    callback_data = callback_class(**callback_data)
    return InlineKeyboardButton(button_text, callback_data=callback_data.json())


def create_inline_markup_from_buttons(buttons: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """Create bot markup with keyboard buttons.

    Args:
        buttons (list[list[InlineKeyboardButton]]): telegram button

    Returns:
        InlineKeyboardMarkup: telegram bot markup.
    """
    inline_markup = InlineKeyboardMarkup()
    for button_row in buttons:
        inline_markup.add(*button_row)
    return inline_markup


def recipe_details_markup(recipe: RecipeWithId) -> InlineKeyboardMarkup:
    """Recipe details telegram bot keyboard markup.

    Args:
        recipe (RecipeWithId): recipe.

    Returns:
        InlineKeyboardMarkup: recipe details markup.
    """
    buttons = []
    id_data = {'id': recipe.id}
    if recipe.is_used:
        unuse_recipe_button = create_inline_keyboard_button(MARK_AS_UNUSED_RECIPE_BUTTON_TEXT,
                                                            UnuseRecipeCallbackData,
                                                            id_data)
        buttons.append([unuse_recipe_button])
    else:
        use_recipe_button = create_inline_keyboard_button(MARK_AS_USED_RECIPE_BUTTON_TEXT,
                                                          UseRecipeCallbackData,
                                                          id_data)
        buttons.append([use_recipe_button])
    delete_button = create_inline_keyboard_button(DELETE_RECIPE_BUTTON_TEXT, DeleteRecipeCallbackData, id_data)
    buttons.append([delete_button])
    markup = create_inline_markup_from_buttons(buttons)
    return markup


def recipes_list_inline_keyboard_markup(recipes_list: list[RecipeWithId]) -> InlineKeyboardMarkup:
    """List of recipes telegram bot keyboard markup.
    Args:
        recipes_list (list[RecipeWithId]): list of recipes.

    Returns:
        InlineKeyboardMarkup: markup with list of recipes.
    """
    buttons = []
    for current_recipe in recipes_list:
        display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
        display_recipe_name = current_recipe.name + display_is_used_recipe

        id_data = {'id': current_recipe.id}
        recipe_button = create_inline_keyboard_button(display_recipe_name, RecipeDetailsCallbackData, id_data)
        buttons.append([recipe_button])
    markup = create_inline_markup_from_buttons(buttons)
    return markup
