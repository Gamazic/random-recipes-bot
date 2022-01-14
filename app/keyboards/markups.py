from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

from app.callback_data_shema import (ActionCallbackData,
                                     DeleteRecipeCallbackData,
                                     RecipeDetailsCallbackData,
                                     UnuseRecipeCallbackData,
                                     UseRecipeCallbackData)
from app.recipe_shema import RecipeWithId


def create_inline_keyboard_button(
    button_text: str,
    callback_class: ActionCallbackData,
    callback_data: dict = {}
) -> InlineKeyboardMarkup:
    """Создает inline кнопку бота. В callback записывается json,
    сформированный из экземпляра callback_class.

    Args:
        button_text (str): Надпись на кнопке
        callback_class (CallbackData): pydantic класс колбэка
        callback_data (dict): все что необходимо всунуть в колбэк.

    Returns:
        InlineKeyboardMarkup: кнопка.
    """
    callback_data = callback_class(**callback_data)
    return InlineKeyboardButton(button_text, callback_data=callback_data.json())


def create_inline_markup_from_buttons(buttons: list[list[InlineKeyboardButton]]):
    inline_markup = InlineKeyboardMarkup()
    for button_row in buttons:
        inline_markup.add(*button_row)
    return inline_markup


def recipe_details_markup(recipe: RecipeWithId) -> dict:
    buttons = []
    id_data = {'id': recipe.id}
    if recipe.is_used:
        unuse_recipe_button = create_inline_keyboard_button('Пометить как неиспользованный',
                                                            UnuseRecipeCallbackData,
                                                            id_data)
        buttons.append([unuse_recipe_button])
    else:
        use_recipe_button = create_inline_keyboard_button('Использовать рецепт',
                                                          UseRecipeCallbackData,
                                                          id_data)
        buttons.append([use_recipe_button])
    delete_button = create_inline_keyboard_button('Удалить', DeleteRecipeCallbackData, id_data)
    buttons.append([delete_button])
    markup = create_inline_markup_from_buttons(buttons)
    return markup


def recipes_list_inline_keyboard_markup(recipes_list: list[RecipeWithId]) -> dict:
    buttons = []
    for current_recipe in recipes_list:
        display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
        display_recipe_name = current_recipe.name + display_is_used_recipe

        id_data = {'id': current_recipe.id}
        recipe_button = create_inline_keyboard_button(display_recipe_name, RecipeDetailsCallbackData, id_data)
        buttons.append([recipe_button])
    markup = create_inline_markup_from_buttons(buttons)
    return markup