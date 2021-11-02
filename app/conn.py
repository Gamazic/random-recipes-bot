import os
import random
from typing import Optional
from bson.objectid import ObjectId
from bson import json_util

from pymongo import MongoClient
import pymongo
from pymongo.collection import Collection
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """
    Класс рецепта. Состоит из полей с индексом name и флагом использования.
    """
    name: str
    is_used: bool = False


class RecipeWithId(Recipe):
    id: ObjectId = Field(alias='_id')

    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {
        #     ObjectId: lambda object_id: json_util.dumps(object_id)
        # }
        json_dumps = json_util.dumps
        json_loads = json_util.loads


class User:
    """
    Класс пользователя с рецептами.
    Общается с базой данных, совершает операции над индексами.
    """
    @property
    def name(self) -> str:
        """Имя коллекции с пользователем."""
        return self.__collection.name

    def __init__(self, collection: Collection):
        """:collection: коллекция в базе данных"""
        self.__collection = collection

    def has_no_recipes(self) -> bool:
        return not bool(self.list_recipes())

    def list_recipes(self, filter: dict = {}) -> list[RecipeWithId]:
        """
        :param filter: - фильтр по полям рецептов.

        Example:
        ```
        user.list_recipes({'is_used': True})
        >>> [Recipe(name=..., is_used=True)]
        ```
        """
        cursor = self.__collection.find(filter)
        return [RecipeWithId(**document) for document in cursor]

    def add_recipe_by_name(self, recipe_name: str):
        recipe = Recipe(name=recipe_name)
        self.add_recipe(recipe)

    def add_recipe(self, recipe: Recipe):
        """Добавляет рецепт в коллекцию пользователя"""
        self.__collection.insert_one(recipe.dict())

    def take_recipe(self, recipe: RecipeWithId) -> RecipeWithId:
        """
        Берет рецепт из коллекции пользователя.
        Меняет значение поля рецепта в бд и в самом рецепте на is_used=True.

        :return: исходный recipe, но с полем is_used=True
        """
        recipe_id_filter = recipe.dict(include={'id'}, by_alias=True)
        if recipe.is_used:
            raise RuntimeError(f'recipe {recipe} already used')
        else:
            recipe.is_used = True
        as_used_update = {'$set': recipe.dict(include={'is_used'})}
        self.__collection.update_one(filter=recipe_id_filter,
                                     update=as_used_update)
        return recipe

    def remove_recipe(self, recipe: RecipeWithId):
        """Удаляет рецепт из коллекции"""
        self.__collection.delete_one(filter=recipe.dict(include={'id'}, by_alias=True))

    def find_recipe_by_id(self, recipe_id: ObjectId) -> RecipeWithId:
        id_filter = {'_id': recipe_id}
        return RecipeWithId(**self.__collection.find_one(filter=id_filter))

    def unuse_all_recipes(self):
        """
        Ставит всем рецептам в коллекции is_used=False
        """
        as_unused_update = {'$set': {'is_used': False}}
        self.__collection.update_many(filter={}, update=as_unused_update)

    def take_random_recipe(self) -> Optional[RecipeWithId]:
        """
        Берет случайный рецепт среди неиспользованных рецептов пользователя.

        Меняет значение поля рецепта в бд и в самом рецепте на is_used=True.
        Если у пользователя нет рецептов, то выбрасывает ошибку `IndexError`.
        Если у пользователя нет неиспользованных рецептов, метод cтавит
        всем рецептам в коллекции is_used=False

        :return: случайный рецепт с полем is_used=True
        """
        if self.has_no_recipes():
            # raise RuntimeError(f'User {self.name} has no recips')
            return None
        unused_recipes = self.list_recipes(filter={'is_used': False})
        if not unused_recipes:
            self.unuse_all_recipes()
            unused_recipes = self.list_recipes(filter={'is_used': False})
        random_recipe = random.choice(unused_recipes)
        return self.take_recipe(random_recipe)


class RecipeDB:
    """
    База данных с рецептами.
    Сама база - MongoDB.
    При обращении к методам класса происходит создание
    класса User, посредством которого записываются,
    читаются и изменяются данные в базе.
    """
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
        user_id = str(user_id)
        return User(self.db[user_id])

    def add_recipe_by_name(self, user_id: int, recipe_name: str):
        user = self.__get_user(user_id)
        user.add_recipe_by_name(recipe_name)

    def list_recipes(self, user_id: int) -> list[RecipeWithId]:
        user = self.__get_user(user_id)
        return user.list_recipes()

    def find_recipe_by_id(self, user_id: int, recipe_id: ObjectId) -> RecipeWithId:
        user = self.__get_user(user_id)
        recipe = user.find_recipe_by_id(recipe_id)
        return recipe

    def remove_recipe_by_id(self, user_id: int, recipe_id: ObjectId):
        user = self.__get_user(user_id)
        recipe = user.find_recipe_by_id(recipe_id)
        user.remove_recipe(recipe)

    def take_random_recipe(self, user_id: int) -> Optional[RecipeWithId]:
        user = self.__get_user(user_id)
        return user.take_random_recipe()


if __name__ == '__main__':
    db = RecipeDB()
    test_user_id = '42'

    recipes = db.list_recipes(test_user_id)
    assert recipes == []

    test_recipe = {'name': 'kukuha', 'is_used': False}
    db.add_recipe_by_name(test_user_id, test_recipe['name'])
    recipes = db.list_recipes(test_user_id)
    assert recipes[0].dict(exclude={'id'}) == test_recipe

    test_recipe = {'name': 'kukuha', 'is_used': False}
    try:
        db.add_recipe_by_name(test_user_id, test_recipe['name'])
    except pymongo.errors.DuplicateKeyError:
        print('key already exists')
    recipes = db.list_recipes(test_user_id)
    assert recipes[0].dict(exclude={'id'}) == test_recipe

    test_recipe['is_used'] = True
    random_recipe = db.take_random_recipe(test_user_id)
    assert random_recipe.dict(exclude={'id'}) == test_recipe
    assert db.find_recipe_by_id(test_user_id, random_recipe.id).dict(exclude={'id'}) == test_recipe

    random_recipe = db.take_random_recipe(test_user_id)
    assert random_recipe.dict(exclude={'id'}) == test_recipe

    recipes = db.list_recipes(test_user_id)
    for r in recipes:
        db.remove_recipe_by_id(test_user_id, r.id)
    recipes = db.list_recipes(test_user_id)
    assert recipes == []
