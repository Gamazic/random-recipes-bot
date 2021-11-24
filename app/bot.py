import os

import telebot
from telebot import types

from conn import RecipeDB, RecipeWithId
from callback_shema import (RecipeActionCallbackData,
                            ActionCallbackData, CallbackValidator)


bot = telebot.TeleBot(os.environ['TG_TOKEN'])
db = RecipeDB()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Инструкция:')


@bot.message_handler(commands=['list'])
def show_recipes_list(message):
    recipes = db.list_recipes(message.chat.id)
    if not recipes:
        bot.send_message(message.chat.id, text='Список рецептов пуст.')
    else:
        layout = recipes_list_layout(recipes)
        bot.send_message(message.chat.id, **layout)


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_action_type(call.data, 'show_recipes_list'))
def show_recipes_list_from_details(call):
    recipes = db.list_recipes(call.from_user.id)
    if not recipes:
        bot.edit_message_text(chat_id=call.from_user.id,
                              message_id=call.message.id,
                              inline_message_id=call.inline_message_id,
                              text='Список рецептов пуст.')
    else:
        layout = recipes_list_layout(recipes)
        bot.edit_message_text(chat_id=call.from_user.id,
                              message_id=call.message.id,
                              inline_message_id=call.inline_message_id,
                              **layout)


def recipes_list_layout(recipes_list: list[RecipeWithId]) -> dict:
    inline_recipes_markup = types.InlineKeyboardMarkup()
    for current_recipe in recipes_list:
        recipe_details_callback = RecipeActionCallbackData(id=current_recipe.id, action='detail')
        display_is_used_recipe = '\U0001F373' if current_recipe.is_used else ''
        display_recipe_name = current_recipe.name + display_is_used_recipe
        recipe_keyboard = types.InlineKeyboardButton(display_recipe_name,
                                                     callback_data=recipe_details_callback.json())
        inline_recipes_markup.add(recipe_keyboard)
    return {
        'text': 'Список',
        'reply_markup': inline_recipes_markup
    }


@bot.message_handler(commands=['add'])
def add_recipe(message):
    msg = bot.send_message(message.chat.id, 'Напишите название рецепта')
    bot.register_next_step_handler(msg, process_adding_recipe)


def process_adding_recipe(message):
    db.add_recipe_by_name(message.chat.id, message.text)
    bot.send_message(message.chat.id, f'Добавлен рецепт\n`{message.text}`',
                     parse_mode='Markdown')


@bot.message_handler(commands=['random'])
def take_random_recipe(message):
    recipe = db.take_random_recipe(message.chat.id)
    if recipe is None:
        bot.send_message(message.chat.id, text='Список рецептов пуст. Чтобы добавить рецепт нажмите кнопку "Добавить"')
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        bot.send_message(message.chat.id, **recipe_details_layout)


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_recipe_action_type(call.data, 'detail'))
def show_recipe_details(call):
    recipe_callback_data = RecipeActionCallbackData.parse_raw(call.data)
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


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_recipe_action_type(call.data, 'use'))
def use_recipe(call):
    recipe_callback_data = RecipeActionCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    recipe = db.take_recipe_by_id(call.from_user.id, recipe_id)
    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_recipe_action_type(call.data, 'unuse'))
def unuse_recipe(call):
    recipe_callback_data = RecipeActionCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    recipe = db.unuse_recipe_by_id(call.from_user.id, recipe_id)
    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_recipe_action_type(call.data, 'delete'))
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
