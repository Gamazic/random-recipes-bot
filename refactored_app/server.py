"""Как мне кажется, фреймворк для бота выбран не очень удачно,
потому что сложно найти хорошие примеры разбиения хэндлеров по модулям.
Я не понял как грамотно избежать circular import в этой библиотеке,
поэтому все хэндлеры будут тут."""
import os

import telebot
from telebot import types

# from db import RecipeDB, RecipeWithId
# from callback_shema import (RecipeActionCallbackData,
#                             ActionCallbackData, CallbackValidator)
# from layouts import recipes_list_layout
from new_app import db
from new_app.chat_gui_layouts import *
from new_app.recipe_shema import RecipeWithId


bot = telebot.TeleBot(os.environ['TG_TOKEN'])


@bot.message_handler(commands=['start'])
def start(message):
    welcome_message = 'Привет! Инструкция пока не готова. Но бот работоспособный.'
    bot.send_message(message.chat.id, welcome_message)


@bot.message_handler(commands=['list'])
def show_recipes_list(message):
    recipes = db.list_user_recipes(message.chat.id)
    if not recipes:
        bot.send_message(message.chat.id, text='Список рецептов пуст.')
    else:
        layout = recipes_list_layout(recipes)
        bot.send_message(message.chat.id, **layout)


@bot.message_handler(commands=['add'])
def add_recipe(message):
    msg = bot.send_message(message.chat.id, 'Напишите название рецепта')
    bot.register_next_step_handler(msg, process_adding_recipe)


@bot.message_handler(commands=['random'])
def take_random_recipe(message):
    recipe = db.take_random_recipe(message.chat.id)
    if recipe is None:
        bot.send_message(message.chat.id, text='Список рецептов пуст. Чтобы добавить рецепт нажмите кнопку "Добавить"')
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        bot.send_message(message.chat.id, **recipe_details_layout)


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



@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_action_type(call.data, 'add'))
def add_recipe_callback(call):
    msg = bot.send_message(call.from_user.id, 'Напишите название рецепта')
    bot.register_next_step_handler(msg, process_adding_recipe)


def process_adding_recipe(message):
    db.add_recipe_by_name(message.chat.id, message.text)
    bot.send_message(message.chat.id, f'Добавлен рецепт\n`{message.text}`',
                     parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_action_type(call.data, 'unuse'))
def mark_all_recipes_as_unused(call):
    if db.user_has_used_recipes(call.from_user.id):
        db.unuse_all_recipes(call.from_user.id)
        recipes = db.list_recipes(call.from_user.id)
        layout = recipes_list_layout(recipes)
        bot.edit_message_text(chat_id=call.from_user.id,
                              message_id=call.message.id,
                              inline_message_id=call.inline_message_id,
                              **layout)


@bot.callback_query_handler(func=lambda call: CallbackValidator.validate_action_type(call.data, 'random'))
def take_random_recipe_callback(call):
    recipe = db.take_random_recipe(call.from_user.id)
    if recipe is None:
        bot.edit_message_text(chat_id=call.from_user.id,
                              message_id=call.message.id,
                              inline_message_id=call.inline_message_id,
                              text='Список рецептов пуст. Чтобы добавить рецепт нажмите кнопку "Добавить"')
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        bot.edit_message_text(chat_id=call.from_user.id,
                              message_id=call.message.id,
                              inline_message_id=call.inline_message_id,
                              **recipe_details_layout)


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
