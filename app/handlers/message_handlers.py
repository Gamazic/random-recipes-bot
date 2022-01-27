from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import db
from app.exceptions import UserHasNoRecipesError
from app.keyboards.markups import recipes_list_inline_keyboard_markup
from app.data.messages_text import (WELCOME_MESSAGE, EMPTY_RECIPES_LIST_MESSAGE,
                                    SHOWN_RECIPES_MESSAGE, WRITE_RECIPE_NAME_MESSAGE,
                                    ADDED_RECIPE_MESSAGE, SINGLE_SHOWN_RECIPE_MESSAGE,
                                    ALL_RECIPES_MARKED_AS_UNUSED_MESSAGE)
from loader import dp, logger


class AddNewRecipeStates(StatesGroup):
    """Finite state machine for recipe addition processing"""
    recipe_name = State()


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    welcome_message = WELCOME_MESSAGE
    await message.answer(welcome_message)


@dp.message_handler(commands=['list'])
async def show_recipes_list(message):
    recipes = await db.list_user_recipes(message.chat.id)
    if not recipes:
        await message.answer(text=EMPTY_RECIPES_LIST_MESSAGE)
    else:
        markup = recipes_list_inline_keyboard_markup(recipes)
        await message.answer(text=SHOWN_RECIPES_MESSAGE, reply_markup=markup)


@dp.message_handler(commands=['add'])
async def add_recipe(message):
    await AddNewRecipeStates.recipe_name.set()
    await message.answer(WRITE_RECIPE_NAME_MESSAGE)


@dp.message_handler(state=AddNewRecipeStates.recipe_name)
async def process_recipe_name(message, state):
    await db.add_recipe_by_name(message.chat.id, message.text)
    await message.answer(f'{ADDED_RECIPE_MESSAGE}`{message.text}`', parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(commands=['random'])
async def take_random_recipe(message):
    try:
        recipe = await db.take_random_recipe(message.chat.id)
    except UserHasNoRecipesError:
        logger.exception(f"user {message.chat.id} called /random without recipes")
        await message.answer(text=EMPTY_RECIPES_LIST_MESSAGE)
    else:
        text = f'{SINGLE_SHOWN_RECIPE_MESSAGE}' \
               f'*{recipe.name}*'
        await message.answer(text=text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['unuse_all'])
async def unuse_all_recipes(message):
    await db.unuse_all_recipes(message.chat.id)
    await message.answer(ALL_RECIPES_MARKED_AS_UNUSED_MESSAGE)
