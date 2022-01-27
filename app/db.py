import os
import random

from bson.objectid import ObjectId
from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorCollection,
                                 AsyncIOMotorDatabase)
from pymongo.collection import ReturnDocument

from app.exceptions import UserHasNoRecipesError, UserHasNoSelectedRecipeError
from app.recipe_shema import Recipe, RecipeWithId
from app.constants import MAXIMUM_COUNT_OF_RETURNED_RECIPES
from loader import io_loop


def _connect_to_db() -> AsyncIOMotorDatabase:
    """Connecting to db with recipes.

    Returns:
        AsyncIOMotorDatabase: Mongo database
    """
    db_user = os.environ['MONGO_USER']
    db_password = os.environ['MONGO_PASSWORD']
    host = os.environ['MONGO_HOST']
    port = os.environ['MONGO_PORT']
    recipe_db_name = os.environ['MONGO_RECIPE_DB']

    connection_string = f'mongodb://{db_user}:{db_password}@{host}:{port}'
    client = AsyncIOMotorClient(connection_string, io_loop=io_loop)
    db = client[recipe_db_name]
    return db


db = _connect_to_db()


def _dispatch_user_id(user_id: int) -> AsyncIOMotorCollection:
    """Return user Mongo collection.

    Args:
        user_id (int): id of user in db.

    Returns:
        AsyncIOMotorCollection: user Mongo collection.
    """
    user_id = str(user_id)
    return db[user_id]


async def add_recipe_by_name(user_id: int, recipe_name: str) -> None:
    """Add new recipe to user in DB.

    Args:
        user_id (int): id of user in db.
        recipe_name (str): text name of recipe.
    """
    user_collection = _dispatch_user_id(user_id)
    recipe = Recipe(name=recipe_name)
    await user_collection.insert_one(recipe.dict())


async def _list_user_recipes_by_filter(
    user_id: int,
    filter: dict = {},
    count: int = MAXIMUM_COUNT_OF_RETURNED_RECIPES
) -> list[RecipeWithId]:
    """Return list of filtered user recipes.

    Args:
        user_id (int): id of user in db.
        filter (dict): mongoDB filter for find query.
        count (int): max count of returned recipes.

    Returns:
        list[RecipeWithId]: list of user recipes from DB.
    """
    user_collection = _dispatch_user_id(user_id)
    cursor = await user_collection.find(filter=filter).to_list(count)
    return [RecipeWithId(**document) for document in cursor]


async def list_user_recipes(
    user_id: int,
    count: int = MAXIMUM_COUNT_OF_RETURNED_RECIPES
) -> list[RecipeWithId]:
    """Return list of user recipes.

    Args:
        user_id (int): id of user in db.
        count (int): max count of returned recipes.

    Returns:
        list[RecipeWithId]: list of user recipes from DB.
    """
    return await _list_user_recipes_by_filter(user_id, count=count)


async def find_recipe_by_id(user_id: int, recipe_id: ObjectId) -> RecipeWithId:
    """Find recipe in db and return it.

    Args:
        user_id (int): id of user in db
        recipe_id (ObjectId): id of recipe in db

    Raises:
        UserHasNoSelectedRecipeError: raises if user has no this recipe.

    Returns:
        RecipeWithId: recipe
    """
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    recipe_db_document = await user_collection.find_one(filter=recipe_id_filter)
    if recipe_db_document is None:
        raise UserHasNoSelectedRecipeError
    return RecipeWithId(**recipe_db_document)


async def remove_recipe_by_id(user_id: int, recipe_id: ObjectId) -> None:
    """Remove recipe for user.

    Args:
        user_id (int): id of user in db
        recipe_id (ObjectId): id of recipe in db
    """
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    await user_collection.delete_one(filter=recipe_id_filter)


async def does_user_have_recipes(user_id: int) -> bool:
    """Checks if user has any recipe.

    Args:
        user_id (int): id of user in db.

    Returns:
        bool: True if has. Otherwise False
    """
    return bool(await list_user_recipes(user_id))


async def does_user_have_used_recipes(user_id: int) -> bool:
    """Checks if the user has used recipes.

    Args:
        user_id (int): id of user in db.

    Returns:
        bool: True if has. Otherwise False
    """
    used_recipes_filter = {'is_used': True}
    used_recipes = await _list_user_recipes_by_filter(user_id,
                                                      filter=used_recipes_filter)
    return bool(used_recipes)


async def take_random_recipe(user_id: int) -> RecipeWithId:
    """Find random non used recipe for user. And then use and return.

    Args:
        user_id (int): id of user in db.

    Raises:
        UserHasNoRecipesError: raises if there is no any recipes for this user in db

    Returns:
        RecipeWithId: used recipe
    """
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
    """Unuse all recipes for user.

    Args:
        user_id (int): id of user in db.
    """
    user_collection = _dispatch_user_id(user_id)
    as_unused_update = {'$set': {'is_used': False}}
    all_recipes_filter = {}
    if (await does_user_have_used_recipes(user_id)):
        await user_collection.update_many(filter=all_recipes_filter, update=as_unused_update)


async def take_recipe_by_id(user_id: int, recipe_id: ObjectId) -> RecipeWithId:
    """Use and return updated user recipe.

    Args:
        user_id (int): id of user in db.
        recipe_id (ObjectId): id of recipe in db.

    Raises:
        UserHasNoSelectedRecipeError: raises if there is no recipe for this user in db.

    Returns:
        RecipeWithId: unused recipe
    """
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
    """Unuse and return updated user recipe.

    Args:
        user_id (int): id of user in db.
        recipe_id (ObjectId): id of recipe in db.

    Returns:
        RecipeWithId: unused recipe
    """
    await unuse_recipe_by_id(user_id, recipe_id)
    return await find_recipe_by_id(user_id, recipe_id)


async def unuse_recipe_by_id(user_id: int, recipe_id: ObjectId) -> None:
    """Unuse recipe by id in DB.

    Args:
        user_id (int): id of user in db.
        recipe_id (ObjectId): id of recipe in db.
    """
    user_collection = _dispatch_user_id(user_id)
    recipe_id_filter = {'_id': recipe_id}
    as_unused_update = {'$set': {'is_used': False}}
    await user_collection.update_one(filter=recipe_id_filter,
                                     update=as_unused_update)
