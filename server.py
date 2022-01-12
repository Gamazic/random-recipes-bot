import os
from functools import partial

import telebot

from app import db
from app.callback_shema import (DeleteRecipeCallbackData,
                                RecipeDetailsCallbackData,
                                UnuseRecipeCallbackData, UseRecipeCallbackData,
                                is_valid_schema)
from app.exceptions import UserHasNoRecipesError, UserHasNoSelectedRecipeError
from app.gui.layouts import create_recipe_details_layout
from app.gui.markups import recipes_list_inline_keyboard_markup


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
        markup = recipes_list_inline_keyboard_markup(recipes)
        text = 'Список рецептов:'
        bot.send_message(message.chat.id, text=text, reply_markup=markup)


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
    try:
        recipe = db.take_random_recipe(message.chat.id)
    except UserHasNoRecipesError:
        bot.send_message(message.chat.id, text='Список рецептов пуст. Чтобы добавить рецепт нажмите кнопку "Добавить"')
        return
    text = 'Рецепт:\n' \
           f'**{recipe.name}**'
    bot.send_message(message.chat.id, text=text)


@bot.message_handler(commands=['unuse_all'])
def mark_all_recipes_as_unused(message):
    # Все таки лучше избавится от этого условия, слишком много логики для сервера
    if db.does_user_have_used_recipes(message.chat.id):
        db.unuse_all_recipes(message.chat.id)
    bot.send_message(message.chat.id, f'Все рецепты помечены как неиспользованные.')


@bot.callback_query_handler(func=partial(is_valid_schema, schema=RecipeDetailsCallbackData))
def show_recipe_details(call):
    recipe_callback_data = RecipeDetailsCallbackData.parse_raw(call.data)
    try:
        recipe = db.find_recipe_by_id(call.from_user.id,
                                      recipe_callback_data.id)
    except UserHasNoSelectedRecipeError:
        bot.send_message(chat_id=call.from_user.id, text='Ошибка! Рецепт отсутствует.')
        return

    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


@bot.callback_query_handler(func=partial(is_valid_schema, schema=UseRecipeCallbackData))
def use_recipe(call):
    recipe_callback_data = UseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    try:
        recipe = db.take_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        bot.send_message(chat_id=call.from_user.id, text='Ошибка! Рецепт отсутствует.')
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


@bot.callback_query_handler(func=partial(is_valid_schema, schema=UnuseRecipeCallbackData))
def unuse_recipe(call):
    recipe_callback_data = UnuseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    try:
        recipe = db.unuse_and_find_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        bot.send_message(chat_id=call.from_user.id, text='Ошибка! Рецепт отсутствует.')
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    bot.edit_message_text(chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          **recipe_details_layout)


@bot.callback_query_handler(func=partial(is_valid_schema, schema=DeleteRecipeCallbackData))
def delete_recipe(call):
    recipe_callback_data = DeleteRecipeCallbackData.parse_raw(call.data)
    db.remove_recipe_by_id(call.from_user.id, recipe_callback_data.id)
    answer = 'Рецепт удален.'
    bot.edit_message_text(text=answer,
                          chat_id=call.from_user.id,
                          message_id=call.message.id,
                          inline_message_id=call.inline_message_id,
                          parse_mode='Markdown')


bot.polling()
