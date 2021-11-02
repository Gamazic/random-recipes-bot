import os
from bson import json_util
from bson.objectid import ObjectId

import telebot
from telebot import types
from pydantic import BaseModel

from conn import RecipeDB, RecipeWithId


bot = telebot.TeleBot(os.environ['TG_TOKEN'])
db = RecipeDB()


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


def parse_callback_data(callback_data):
    parsed_data = json_util.loads(callback_data)
    if 'action' in parsed_data:
        callback_data = ActionCallbackData(**parsed_data)
    elif 'id' in parsed_data:
        callback_data = RecipeDetailsCallbackData(**parsed_data)
    return callback_data


def validate_recipe_details_callback(callback_data):
    parsed_data = json_util.loads(callback_data)
    return ('id' in parsed_data) and ('action' not in parsed_data)


def validate_recipe_action_callback(callback_data):
    parsed_data = json_util.loads(callback_data)
    return ('id' in parsed_data) and ('action' in parsed_data)


def validate_change_recipe_callback(callback_data):
    is_recipe_action = validate_recipe_action_callback(callback_data)
    parsed_data = json_util.loads(callback_data)
    is_change_action = parsed_data['action'] == 'change'
    return is_recipe_action and is_change_action


def validate_delete_recipe_callback(callback_data):
    is_recipe_action = validate_recipe_action_callback(callback_data)
    parsed_data = json_util.loads(callback_data)
    is_change_action = parsed_data['action'] == 'delete'
    return is_recipe_action and is_change_action


def validate_action_callback(callback_data):
    parsed_data = json_util.loads(callback_data)
    return ('id' not in parsed_data) and ('action' in parsed_data)


user_keyboard = [
    ['Выбрать случайный'],
    ['Список'],
    ['Добавить']
]


@bot.message_handler(commands=['start'])
def start(message):
    keyboard_markup = types.ReplyKeyboardMarkup()
    for row in user_keyboard:
        row_buttons = []
        for text_line in row:
            row_buttons.append(types.KeyboardButton(text_line))
        keyboard_markup.row(*row_buttons)
    bot.send_message(message.chat.id, 'Выберите действие.',
                     reply_markup=keyboard_markup)


@bot.message_handler(regexp='[Сс]писок')
def show_recipes(message):
    recipes = db.list_recipes(message.chat.id)
    if not recipes:
        bot.reply_to(message, text='Список рецептов пуст.')
    else:
        inline_recipes_markup = types.InlineKeyboardMarkup()
        for current_recipe in recipes:
            recipe_details_callback = RecipeDetailsCallbackData(id=current_recipe.id)
            display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
            display_recipe_name = current_recipe.name + display_is_used_recipe
            recipe_keyboard = types.InlineKeyboardButton(display_recipe_name,
                                                         callback_data=recipe_details_callback.json())
            inline_recipes_markup.add(recipe_keyboard)

        # used_recipes_callback = ActionCallbackData(action='show_used_recipes')
        # used_recipes_button = types.InlineKeyboardButton('Неиспользованные',
        #                                                  callback_data=used_recipes_callback.json())

        # unused_recipes_callback = ActionCallbackData(action='show_unused_recipes')
        # unused_recipes_button = types.InlineKeyboardButton('Использованные',
        #                                                    callback_data=unused_recipes_callback.json())

        # inline_recipes_markup.add(used_recipes_button, unused_recipes_button)

        bot.reply_to(message, text='Список:',
                     reply_markup=inline_recipes_markup)


@bot.message_handler(regexp='[Дд]обав')
def add_recipe(message):
    msg = bot.reply_to(message, 'Напишите название рецепта')
    bot.register_next_step_handler(msg, process_adding_recipe)


def process_adding_recipe(message):
    db.add_recipe_by_name(message.chat.id, message.text)
    bot.send_message(message.chat.id, f'Добавлен рецепт\n`{message.text}`',
                     parse_mode='Markdown')


@bot.message_handler(regexp='[Сс]луч')
def take_random_recipe(message):
    recipe = db.take_random_recipe(message.chat.id)
    if recipe is None:
        bot.reply_to(message, text='Список рецептов пуст. Чтобы добавить рецепт нажмите кнопку "Добавить"')
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        bot.reply_to(message, **recipe_details_layout)


@bot.callback_query_handler(func=lambda call: validate_recipe_details_callback(call.data))
def show_recipe_details(call):
    recipe_callback_data = RecipeDetailsCallbackData.parse_raw(call.data)
    recipe = db.find_recipe_by_id(call.from_user.id,
                                  recipe_callback_data.id)

    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


def create_recipe_details_layout(recipe: RecipeWithId) -> dict:
    is_used_status_line = 'Использован \U0001F373' if recipe.is_used else '*Неиспользован*'
    answer = 'Рецепт:\n' \
             f'*{recipe.name}*\n' \
             f'Статус: *{is_used_status_line}*'

    inline_recipe_actions_markup = types.InlineKeyboardMarkup()
    delete_callback = RecipeActionCallbackData(action='delete',
                                               id=recipe.id)
    delete_button = types.InlineKeyboardButton('Удалить',
                                               callback_data=delete_callback.json())

    inline_recipe_actions_markup.add(delete_button)
    return {
        'text': answer,
        'parse_mode': 'Markdown',
        'reply_markup': inline_recipe_actions_markup
    }


@bot.callback_query_handler(func=lambda call: validate_delete_recipe_callback(call.data))
def delete_recipe(call):
    recipe_callback_data = RecipeActionCallbackData.parse_raw(call.data)
    recipe = db.find_recipe_by_id(call.from_user.id,
                                  recipe_callback_data.id)
    answer = 'Удален рецепт\n' \
             f'*{recipe.name}*'
    db.remove_recipe_by_id(call.from_user.id, recipe_callback_data.id)
    bot.edit_message_text(text=answer,
                          chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          parse_mode='Markdown',
                          reply_markup=None)


bot.polling()
