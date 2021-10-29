import os
import random
from typing import Optional
from bson.objectid import ObjectId

from pymongo import MongoClient
from pymongo.collection import Collection
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias='_id')
    name: str
    is_used: bool = False

    def take(self):
        if self.is_used:
            raise RuntimeError(f'recipe {self} already used')
        self.is_used = True
        return self

    def get_index(self):
        return self.dict(include={'id'}, by_alias=True)

    def get_data_without_index(self):
        return self.dict(exclude={'id'}, by_alias=True)

    class Config:
        arbitrary_types_allowed = True


class User:
    @property
    def name(self):
        return self.__collection.name

    def __init__(self, collection: Collection):
        self.__collection = collection

    def is_empty(self):
        return not bool(self.list_recipes())

    def list_recipes(self, filter: dict = {}) -> list[Recipe]:
        """
        :param filter: - фильтр по полям рецептов.

        Example:
        ```
        user.list_recipes({'is_used': True})
        >>> [Recipe(id=..., name=..., is_used=True)]
        ```
        """
        cursor = self.__collection.find(filter)
        return [Recipe(**document) for document in cursor]

    def add_recipe(self, recipe_name: str):
        new_recipe = Recipe(name=recipe_name)
        self.__collection.insert_one(new_recipe.get_data_without_index())

    def take_recipe(self, recipe: Recipe) -> Recipe:
        recipe_index_filter = recipe.get_index()
        used_recipe = recipe.take()
        as_used_update = {'$set': used_recipe.get_data_without_index()}
        self.__collection.update_one(filter=recipe_index_filter,
                                     update=as_used_update)
        return used_recipe

    def remove_recipe(self, recipe: Recipe):
        self.__collection.delete_one(filter=recipe.dict(by_alias=True))

    def unuse_all_recipes(self):
        as_unused_update = {'$set': {'is_used': False}}
        self.__collection.update_many(filter={}, update=as_unused_update)

    def random_recipe(self) -> Recipe:
        if self.is_empty():
            raise IndexError(f'User {self.name} has no recips')
        unused_recipes = self.list_recipes(filter={'is_used': False})
        if not unused_recipes:
            self.unuse_all_recipes()
            unused_recipes = self.list_recipes(filter={'is_used': False})
        random_recipe = random.choice(unused_recipes)
        return self.take_recipe(random_recipe)


class RecipeDB:
    def __init__(self):
        db_user = os.environ['MONGO_USER']
        password = os.environ['MONGO_PASSWORD']
        host = os.environ['MONGO_HOST']
        port = os.environ['MONGO_PORT']
        db_name = os.environ['MONGO_RECIPE_DB']

        connection_string = f'mongodb://{db_user}:{password}@{host}:{port}'
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def __get_user(self, user_id: int) -> User:
        return User(self.db[user_id])

    def add_recipe(self, user_id: int, recipe_name: str):
        user = self.__get_user(user_id)
        user.add_recipe(recipe_name)

    def list_recipes(self, user_id: int) -> list[Recipe]:
        user = self.__get_user(user_id)
        return user.list_recipes()

    def remove_recipe(self, user_id: int, recipe: Recipe):
        user = self.__get_user(user_id)
        user.remove_recipe(recipe)

    def random_recipe(self, user_id: int) -> Recipe:
        user = self.__get_user(user_id)
        return user.random_recipe()


if __name__ == '__main__':
    db = RecipeDB()
    test_user_id = '42'

    recipes = db.list_recipes(test_user_id)
    assert recipes == []

    test_recipe = {'name': 'kukuha', 'is_used': False}
    db.add_recipe(test_user_id, test_recipe['name'])
    recipes = db.list_recipes(test_user_id)
    assert recipes[0].get_data_without_index() == test_recipe

    test_recipe['is_used'] = True
    random_recipe = db.random_recipe(test_user_id)
    assert random_recipe.get_data_without_index() == test_recipe

    random_recipe = db.random_recipe(test_user_id)
    assert random_recipe.get_data_without_index() == test_recipe

    recipes = db.list_recipes(test_user_id)
    for r in recipes:
        db.remove_recipe(test_user_id, r)
    recipes = db.list_recipes(test_user_id)
    assert recipes == []
