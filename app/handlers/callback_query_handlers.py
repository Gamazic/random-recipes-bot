from functools import partial

from aiogram.types import ParseMode

from app import db
from app.callback_data_schema import (DeleteRecipeCallbackData,
                                      RecipeDetailsCallbackData,
                                      UnuseRecipeCallbackData,
                                      UseRecipeCallbackData,
                                      is_valid_schema_for_callback)

from app.exceptions import UserHasNoSelectedRecipeError
from app.keyboards.layouts import create_recipe_details_layout
from app.data.messages_text import ERROR_THERE_IS_NO_RECIPE_CALLBACK_MESSAGE, RECIPE_DELETED_MESSAGE
from loader import dp, bot, logger


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=RecipeDetailsCallbackData))
async def show_recipe_details(callback_query):
    recipe_callback_data = RecipeDetailsCallbackData.parse_raw(callback_query.data)
    # TODO: (1) (this is how identical fragments are marked)
    # I don't know how to abstract this block.
    # I don't want to check if recipe is exists each time.
    # Because of performance and and that this situation is really an error.
    # And I think return None by db method is bad idea because of poorly
    # controlled behavior.
    # If you know good resolution for this situation, please
    # write an issue or do a pull request.
    try:
        recipe = await db.find_recipe_by_id(callback_query.from_user.id,
                                            recipe_callback_data.id)
    except UserHasNoSelectedRecipeError:
        logger.exception(
            f"user {callback_query.from_user.id} clicked on already"
            "deleted recipe with id {recipe_callback_data.id}"
            )
        await callback_query.answer(text=ERROR_THERE_IS_NO_RECIPE_CALLBACK_MESSAGE)
        await callback_query.message.delete()
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=UseRecipeCallbackData))
async def use_recipe(callback_query):
    recipe_callback_data = UseRecipeCallbackData.parse_raw(callback_query.data)
    recipe_id = recipe_callback_data.id
    # TODO: (1)
    try:
        recipe = await db.take_recipe_by_id(callback_query.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        logger.exception(
            f"user {callback_query.from_user.id} clicked on already"
            "deleted recipe with id {recipe_callback_data.id}"
            )
        await callback_query.answer(text=ERROR_THERE_IS_NO_RECIPE_CALLBACK_MESSAGE)
        await callback_query.message.delete()
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    inline_message_id=callback_query.inline_message_id,
                                    **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=UnuseRecipeCallbackData))
async def unuse_recipe(callback_query):
    recipe_callback_data = UnuseRecipeCallbackData.parse_raw(callback_query.data)
    recipe_id = recipe_callback_data.id
    # TODO: (1)
    try:
        recipe = await db.unuse_and_find_recipe_by_id(callback_query.from_user.id, recipe_id)
    except UserHasNoSelectedRecipeError:
        logger.exception(
            f"user {callback_query.from_user.id} clicked on already"
            "deleted recipe with id {recipe_callback_data.id}"
            )
        await callback_query.answer(text=ERROR_THERE_IS_NO_RECIPE_CALLBACK_MESSAGE)
        await callback_query.message.delete()
    else:
        recipe_details_layout = create_recipe_details_layout(recipe)
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    inline_message_id=callback_query.inline_message_id,
                                    **recipe_details_layout)


@dp.callback_query_handler(partial(is_valid_schema_for_callback, schema=DeleteRecipeCallbackData))
async def delete_recipe(callback_query):
    recipe_callback_data = DeleteRecipeCallbackData.parse_raw(callback_query.data)
    await db.remove_recipe_by_id(callback_query.from_user.id, recipe_callback_data.id)
    answer = RECIPE_DELETED_MESSAGE
    await bot.edit_message_text(text=answer,
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                inline_message_id=callback_query.inline_message_id,
                                parse_mode=ParseMode.MARKDOWN)
