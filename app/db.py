import os
import random

from bson.objectid import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorCollection,
                                 AsyncIOMotorDatabase)
from pymongo.collection import ReturnDocument

from app.exceptions import UserHasNoRecipesError, UserHasNoSelectedRecipeError
from app.recipe_shema import Recipe, RecipeWithId


def _connect_to_db() -> AsyncIOMotorDatabase:
    load_dotenv()
    db_user = os.environ['MONGO_USER']
    db_password = os.environ['MONGO_PASSWORD']
    host = os.environ['MONGO_HOST']
    port = os.environ['MONGO_PORT']
    recipe_db_name = os.environ['MONGO_RECIPE_DB']

    connection_string = f'mongodb://{db_user}:{db_password}@{host}:{port}'
    client = AsyncIOMotorClient(connection_string)
    db = client[recipe_db_name]
    return db


db = _connect_to_db()


def _dispatch_user_id(user_id: int) -> AsyncIOMotorCollection:
    user_id = str(user_id)
    return db[user_id]


async def add_recipe_by_name(user_id: int, recipe_name: str) -> None:
    """Add recipe to user in DB.

    Args:
        user_id (int): ID of user
        recipe_name (str): Text name of recipe.
    """
    user_collection = _dispatch_user_id(user_id)
    recipe = Recipe(name=recipe_name)
    await user_collection.insert_one(recipe.dict())


async def _list_user_recipes_by_filter(user_id: int, filter: dict = {}) -> list[RecipeWithId]:
    user_collection = _dispatch_user_id(user_id)
    cursor = await user_collection.find(filter=filter).to_list(100) # TODO: remove magic constant
    return [RecipeWithId(**document) for document in cursor]


async def list_user_recipes(user_id: int) -> list[RecipeWithId]:
    """
    Args:
        user_id (int): ID of user.

    Returns:
        list[RecipeWithId]: list of user recipes from DB.
    """
    return await _list_user_recipes_by_filter(user_id)


async def find_recipe_by_id(user_id: int, recipe_id: ObjectId) -> RecipeWithId:
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    recipe_db_document = await user_collection.find_one(filter=recipe_id_filter)
    if recipe_db_document is None:
        raise UserHasNoSelectedRecipeError
    return RecipeWithId(**recipe_db_document)


async def remove_recipe_by_id(user_id: int, recipe_id: ObjectId) -> None:
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    await user_collection.delete_one(filter=recipe_id_filter)


async def does_user_have_recipes(user_id: int) -> bool:
    return bool(await list_user_recipes(user_id))


async def does_user_have_used_recipes(user_id: int) -> bool:
    used_recipes_filter = {'is_used': True}
    used_recipes = await _list_user_recipes_by_filter(user_id,
                                                      filter=used_recipes_filter)
    return bool(used_recipes)


async def take_random_recipe(user_id: int) -> RecipeWithId:
    if not (await does_user_have_recipes(user_id)):
        raise UserHasNoRecipesError(f'User {user_id} has no recipes')
    not_used_recipes_filter = {'is_used': False}
    unused_recipes = await _list_user_recipes_by_filter(user_id, not_used_recipes_filter)
    if not unused_recipes:
        await unuse_all_recipes(user_id)
        unused_recipes = await _list_user_recipes_by_filter(user_id, not_used_recipes_filter)
    random_recipe = random.choice(unused_recipes)
    return await take_recipe_by_id(user_id, random_recipe.id)


async def unuse_all_recipes(user_id: int) -> None:
    user_collection = _dispatch_user_id(user_id)
    as_unused_update = {'$set': {'is_used': False}}
    all_recipes_filter = {}
    await user_collection.update_many(filter=all_recipes_filter, update=as_unused_update)


async def take_recipe_by_id(user_id: int, recipe_id: ObjectId) -> RecipeWithId:
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    as_used_update = {'$set': {'is_used': True}}
    recipe_db_document = await user_collection.find_one_and_update(filter=recipe_id_filter,
                                                                   update=as_used_update,
                                                                   return_document=ReturnDocument.AFTER)
    if recipe_db_document is None:
        raise UserHasNoSelectedRecipeError
    recipe = RecipeWithId(**recipe_db_document)
    return recipe


async def unuse_and_find_recipe_by_id(user_id: int, recipe_id: ObjectId) -> RecipeWithId:
    await unuse_recipe_by_id(user_id, recipe_id)
    return await find_recipe_by_id(user_id, recipe_id)


async def unuse_recipe_by_id(user_id: int, recipe_id: ObjectId) -> None:
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    as_unused_update = {'$set': {'is_used': False}}
    await user_collection.update_one(filter=recipe_id_filter,
                                     update=as_unused_update)
