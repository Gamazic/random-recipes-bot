import os

import telebot
from telebot import types

from conn import MongoRecipe


bot = telebot.TeleBot(os.environ['TG_TOKEN'])
db = MongoRecipe()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    btn_add = types.KeyboardButton('Добавить рецепт')
    btn_random = types.KeyboardButton('Случайный рецепт')
    btn_recipe_list = types.KeyboardButton('Список рецептов')
    markup.add(btn_add, btn_random, btn_recipe_list)
    bot.send_message(message.chat.id, 'Выберите действие.',
                     reply_markup=markup)


@bot.message_handler(regexp='[Дд]обав')
def add_recipe(message):
    msg = bot.reply_to(message, 'Напишите название рецепта')
    bot.register_next_step_handler(msg, process_recipe)


@bot.message_handler(regexp='[Сс]лучайн')
def random_recipe(message):
    try:
        answer = db.random_recipe(message.chat.id)
    except IndexError:
        answer = 'Для начала добавьте рецепт.'

    markup = types.InlineKeyboardMarkup()
    # btn_details = types.InlineKeyboardButton(text='Описание',
    #                                          callback_data='recipe_details')
    btn_change = types.InlineKeyboardButton(text='Удалить',
                                            callback_data='delete_recipe')
    # markup.add(btn_details, btn_change)
    markup.add(btn_change)
    bot.reply_to(message, answer, reply_markup=markup)


@bot.message_handler(regexp='[Сс]писок')
def show_recipes(message):
    recipes = db.list_recipe(message.chat.id)
    raw_answer = []
    for rec in recipes:
        name = rec['name']
        if rec['used']:
            line = name
        else:
            line = f'*{name}*'
        raw_answer.append(line)
    if raw_answer:
        answer = '\n'.join(raw_answer)
    else:
        answer = 'Рецепты отсутствуют.'
    bot.reply_to(message, answer, parse_mode='Markdown')


# @bot.callback_query_handler(func=lambda call: call.data == 'recipe_details')
# def recipe_details_callback(call):
#     message = call.message
#     chat_id = message.chat.id
#     recipe = message.text
#     details = db.get_recipe_details(chat_id, recipe)
#     if details:
#         answer = f'Рецепт:\n{recipe}\nОписание:\n{details}'
#     else:
#         answer = 'Описание отсутствует.'
#     bot.send_message(chat_id, answer)


@bot.callback_query_handler(func=lambda call: call.data == 'delete_recipe')
def delete_recipe_callback(call):
    message = call.message
    chat_id = message.chat.id
    recipe = message.text
    db.delete_recipe(chat_id, recipe)
    bot.send_message(chat_id, f'Рецепт {recipe} удален.')


def process_recipe(message):
    chat_id = message.chat.id
    db.insert_recipe(chat_id, message.text)
    bot.send_message(chat_id, f'Успешно вставлено {message.text}')


bot.polling()
