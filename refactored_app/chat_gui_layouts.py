from telebot import types

from recipe_shema import RecipeWithId
from callback_shema import CallbackData


def recipes_list_layout(recipes_list: list[RecipeWithId]) -> dict:
    inline_recipes_markup = types.InlineKeyboardMarkup()
    for current_recipe in recipes_list:
        recipe_details_callback = RecipeActionCallbackData(id=current_recipe.id, action='detail')
        display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
        display_recipe_name = current_recipe.name + display_is_used_recipe
        recipe_button = types.InlineKeyboardButton(display_recipe_name,
                                                   callback_data=recipe_details_callback.json())
        inline_recipes_markup.add(recipe_button)
    random_recipe_callback = ActionCallbackData(action='random')
    random_recipe_button = types.InlineKeyboardButton('Случайный рецепт',
                                                      callback_data=random_recipe_callback.json())
    add_recipe_callback = ActionCallbackData(action='add')
    add_recipe_button = types.InlineKeyboardButton('Добавить рецепт',
                                                   callback_data=add_recipe_callback.json())
    unuse_all_callback = ActionCallbackData(action='unuse')
    unuse_all_button = types.InlineKeyboardButton('Пометить все как неиспользованный',
                                                  callback_data=unuse_all_callback.json())
    inline_recipes_markup.add(random_recipe_button, add_recipe_button)
    inline_recipes_markup.add(unuse_all_button)
    return {
        'text': 'Список',
        'reply_markup': inline_recipes_markup
    }


def create_inline_keyboard_button(
    button_text: str,
    callback_class: CallbackData,
    callback_data: dict
) -> types.InlineKeyboardMarkup:
    """Создает inline кнопку бота. В callback записывается json,
    сформированный из экземпляра callback_class.

    Args:
        button_text (str): Надпись на кнопке
        callback_class (CallbackData): pydantic класс колбэка
        callback_data (dict): все что необходимо всунуть в колбэк.

    Returns:
        types.InlineKeyboardMarkup: кнопка.
    """
    callback_data = callback_class(**callback_data)
    return types.InlineKeyboardButton(button_text, callback_data=callback_data.json())


def recipes_list_inline_keyboard(recipes_list: list[RecipeWithId]) -> dict:
    inline_recipes_markup = types.InlineKeyboardMarkup()
    for current_recipe in recipes_list:
        recipe_details_callback = RecipeActionCallbackData(id=current_recipe.id, action='detail')
        display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
        display_recipe_name = current_recipe.name + display_is_used_recipe
        recipe_button = types.InlineKeyboardButton(display_recipe_name,
                                                   callback_data=recipe_details_callback.json())
        inline_recipes_markup.add(recipe_button)
    random_recipe_callback = ActionCallbackData(action='random')
    random_recipe_button = types.InlineKeyboardButton('Случайный рецепт',
                                                      callback_data=random_recipe_callback.json())
    add_recipe_callback = ActionCallbackData(action='add')
    add_recipe_button = types.InlineKeyboardButton('Добавить рецепт',
                                                   callback_data=add_recipe_callback.json())
    unuse_all_callback = ActionCallbackData(action='unuse')
    unuse_all_button = types.InlineKeyboardButton('Пометить все как неиспользованный',
                                                  callback_data=unuse_all_callback.json())
    inline_recipes_markup.add(random_recipe_button, add_recipe_button)
    inline_recipes_markup.add(unuse_all_button)
    return inline_recipes_markup


def create_recipe_details_layout(recipe: RecipeWithId) -> dict:
    is_used_status_line = 'Использован \U0001F373' if recipe.is_used else '*Неиспользован*'
    answer = 'Рецепт:\n' \
             f'*{recipe.name}*\n' \
             f'Статус: *{is_used_status_line}*'

    inline_recipe_actions_markup = types.InlineKeyboardMarkup()
    if recipe.is_used:
        unuse_callback = RecipeActionCallbackData(id=recipe.id, action='unuse')
        unuse_button = types.InlineKeyboardButton('Пометить как неиспользованный',
                                                  callback_data=unuse_callback.json())
        inline_recipe_actions_markup.add(unuse_button)
    else:
        use_callback = RecipeActionCallbackData(id=recipe.id, action='use')
        use_button = types.InlineKeyboardButton('Использовать рецепт',
                                                callback_data=use_callback.json())
        inline_recipe_actions_markup.add(use_button)
    delete_callback = RecipeActionCallbackData(action='delete',
                                               id=recipe.id)
    delete_button = types.InlineKeyboardButton('Удалить',
                                               callback_data=delete_callback.json())

    list_recipes_callback = ActionCallbackData(action='show_recipes_list')
    list_recipes_button = types.InlineKeyboardButton('К списку рецептов',
                                                     callback_data=list_recipes_callback.json())

    inline_recipe_actions_markup.add(list_recipes_button, delete_button)
    return {
        'text': answer,
        'parse_mode': 'Markdown',
        'reply_markup': inline_recipe_actions_markup
    }