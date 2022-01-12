import os
from functools import partial

from aiogram.types import ParseMode
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from app import db
from app.callback_shema import (DeleteRecipeCallbackData,
                                RecipeDetailsCallbackData,
                                UnuseRecipeCallbackData, UseRecipeCallbackData,
                                is_valid_schema)
from app.exceptions import UserHasNoRecipesError, UserHasNoSelectedRecipeError
from app.gui.layouts import create_recipe_details_layout
from app.gui.markups import recipes_list_inline_keyboard_markup


load_dotenv()

bot = Bot(token=os.environ['TG_TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class AddRecipeStates(StatesGroup):
    recipe_name = State()


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    welcome_message = 'Привет! Инструкция пока не готова. Но бот работоспособный.'
    await message.answer(welcome_message)


@dp.message_handler(commands=['list'])
async def show_recipes_list(message):
    recipes = db.list_user_recipes(message.chat.id)
    if not recipes:
        await message.answer(text='Список рецептов пуст.')
    else:
        markup = recipes_list_inline_keyboard_markup(recipes)
        text = 'Список рецептов:'
        await message.answer(text=text, reply_markup=markup)


@dp.message_handler(commands=['add'])
async def add_recipe(message):
    await AddRecipeStates.recipe_name.set()
    await message.answer('Напишите название рецепта')


@dp.message_handler(state=AddRecipeStates.recipe_name)
async def process_recipe_name(message, state):
    db.add_recipe_by_name(message.chat.id, message.text)
    await message.answer(f'Добавлен рецепт\n`{message.text}`', parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(commands=['random'])
async def take_random_recipe(message):
    try:
        recipe = db.take_random_recipe(message.chat.id)
    except UserHasNoRecipesError:
        await message.answer(text='Список рецептов пуст. Чтобы добавить рецепт отправьте "/add"')
        return
    text = 'Рецепт:\n' \
           f'*{recipe.name}*'
    await message.answer(text=text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['unuse_all'])
async def mark_all_recipes_as_unused(message):
    # Все таки лучше избавится от этого условия, слишком много логики для сервера
    if db.does_user_have_used_recipes(message.chat.id):
        db.unuse_all_recipes(message.chat.id)
    await message.answer('Все рецепты помечены как неиспользованные.')


@dp.callback_query_handler(partial(is_valid_schema, schema=RecipeDetailsCallbackData))
async def show_recipe_details(call):
    recipe_callback_data = RecipeDetailsCallbackData.parse_raw(call.data)
    try:
        recipe = db.find_recipe_by_id(call.from_user.id,
                                      recipe_callback_data.id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema, schema=UseRecipeCallbackData))
async def use_recipe(call):
    recipe_callback_data = UseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    try:
        recipe = db.take_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema, schema=UnuseRecipeCallbackData))
async def unuse_recipe(call):
    recipe_callback_data = UnuseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    try:
        recipe = db.unuse_and_find_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema, schema=DeleteRecipeCallbackData))
async def delete_recipe(call):
    recipe_callback_data = DeleteRecipeCallbackData.parse_raw(call.data)
    db.remove_recipe_by_id(call.from_user.id, recipe_callback_data.id)
    answer = 'Рецепт удален.'
    await bot.edit_message_text(text=answer,
                                chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
