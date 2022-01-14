import os
from functools import partial

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import db
from app.callback_data_shema import (DeleteRecipeCallbackData,
                                     RecipeDetailsCallbackData,
                                     UnuseRecipeCallbackData,
                                     UseRecipeCallbackData, is_valid_schema_for_callback)
from app.exceptions import UserHasNoRecipesError, UserHasNoSelectedRecipeError
from app.keyboards.layouts import create_recipe_details_layout
from app.keyboards.markups import recipes_list_inline_keyboard_markup


bot = Bot(token=os.environ['TG_TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class AddNewRecipeStates(StatesGroup):
    recipe_name = State()


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    welcome_message = 'Привет! Инструкция пока не готова. Но бот работоспособный.'
    await message.answer(welcome_message)


@dp.message_handler(commands=['list'])
async def show_recipes_list(message):
    recipes = await db.list_user_recipes(message.chat.id)
    if not recipes:
        await message.answer(text='Список рецептов пуст.')
    else:
        markup = recipes_list_inline_keyboard_markup(recipes)
        text = 'Список рецептов:'
        await message.answer(text=text, reply_markup=markup)


@dp.message_handler(commands=['add'])
async def add_recipe(message):
    await AddNewRecipeStates.recipe_name.set()
    await message.answer('Напишите название рецепта')


@dp.message_handler(state=AddNewRecipeStates.recipe_name)
async def process_recipe_name(message, state):
    await db.add_recipe_by_name(message.chat.id, message.text)
    await message.answer(f'Добавлен рецепт\n`{message.text}`', parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(commands=['random'])
async def take_random_recipe(message):
    try:
        recipe = await db.take_random_recipe(message.chat.id)
    except UserHasNoRecipesError:
        await message.answer(text='Список рецептов пуст. Чтобы добавить рецепт отправьте "/add"')
        return
    text = 'Рецепт:\n' \
           f'*{recipe.name}*'
    await message.answer(text=text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['unuse_all'])
async def unuse_all_recipes(message):
    await db.unuse_all_recipes(message.chat.id)
    await message.answer('Все рецепты помечены как неиспользованные.')


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=RecipeDetailsCallbackData))
async def show_recipe_details(call):
    recipe_callback_data = RecipeDetailsCallbackData.parse_raw(call.data)
    # TODO: (1) (this is how identical fragments are marked)
    # I don't know how to abstract this block.
    # I don't want to check if recipe is exists each time.
    # Because of performance and and that this situation is really an error.
    # And I think return None by db method is bad idea because of poorly
    # controlled behavior.
    # If you know good resolution for this situation, please
    # write an issue or do a pull request.
    try:
        recipe = await db.find_recipe_by_id(call.from_user.id,
                                            recipe_callback_data.id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        await call.message.delete()
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=UseRecipeCallbackData))
async def use_recipe(call):
    recipe_callback_data = UseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    # TODO: (1)
    try:
        recipe = await db.take_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        await call.message.delete()
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=UnuseRecipeCallbackData))
async def unuse_recipe(call):
    recipe_callback_data = UnuseRecipeCallbackData.parse_raw(call.data)
    recipe_id = recipe_callback_data.id
    # TODO: (1)
    try:
        recipe = await db.unuse_and_find_recipe_by_id(call.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        await call.answer(text='Ошибка! Рецепт отсутствует.')
        await call.message.delete()
        return
    recipe_details_layout = create_recipe_details_layout(recipe)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=DeleteRecipeCallbackData))
async def delete_recipe(call):
    recipe_callback_data = DeleteRecipeCallbackData.parse_raw(call.data)
    await db.remove_recipe_by_id(call.from_user.id, recipe_callback_data.id)
    answer = 'Рецепт удален.'
    await bot.edit_message_text(text=answer,
                                chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                inline_message_id=call.inline_message_id,
                                parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
