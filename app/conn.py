import os
import random
from typing import Optional
from bson.objectid import ObjectId

from pymongo import MongoClient
import pymongo
from pymongo.collection import Collection
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """
    Класс рецепта. Состоит из полей с индексом (name) и флагом использования.
    """
    name: str
    is_used: bool = False

    def take(self):
        """
        :return: Использованный рецепт. Меняет значение поля is_used на True
        :rtype: Recipe
        """
        if self.is_used:
            raise RuntimeError(f'recipe {self} already used')
        self.is_used = True
        return self


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
        if self.is_empty():
            self.__create_recipe_name_index()

    def is_empty(self) -> bool:
        return not bool(self.list_recipes())

    def __create_recipe_name_index(self):
        self.__collection.create_index([('name', pymongo.TEXT)])

    def list_recipes(self, filter: dict = {}) -> list[Recipe]:
        """
        :param filter: - фильтр по полям рецептов.

        Example:
        ```
        user.list_recipes({'is_used': True})
        >>> [Recipe(name=..., is_used=True)]
        ```
        """
        cursor = self.__collection.find(filter)
        return [Recipe(**document) for document in cursor]

    def add_recipe(self, recipe_name: str):
        """Добавляет рецепт в коллекцию пользователя"""
        new_recipe = Recipe(name=recipe_name)
        self.__collection.insert_one(new_recipe.dict())

    def take_recipe(self, recipe: Recipe) -> Recipe:
        """
        Берет рецепт из коллекции пользователя.
        Меняет значение поля рецепта в бд и в самом рецепте на is_used=True.

        :return: исходный recipe, но с полем is_used=True
        """
        recipe_name_filter = recipe.dict(include={'name'})
        used_recipe = recipe.take()
        as_used_update = {'$set': used_recipe.dict(include={'is_used'})}
        self.__collection.update_one(filter=recipe_name_filter,
                                     update=as_used_update)
        return used_recipe

    def remove_recipe(self, recipe: Recipe):
        """Удаляет рецепт из коллекции"""
        self.__collection.delete_one(filter=recipe.dict(include={'name'}))

    def unuse_all_recipes(self):
        """
        Ставит всем рецептам в коллекции is_used=False
        """
        as_unused_update = {'$set': {'is_used': False}}
        self.__collection.update_many(filter={}, update=as_unused_update)

    def take_random_recipe(self) -> Recipe:
        """
        Берет случайный рецепт среди неиспользованных рецептов пользователя.

        Меняет значение поля рецепта в бд и в самом рецепте на is_used=True.
        Если у пользователя нет рецептов, то выбрасывает ошибку `IndexError`.
        Если у пользователя нет неиспользованных рецептов, метод cтавит
        всем рецептам в коллекции is_used=False

        :return: случайный рецепт с полем is_used=True
        """
        if self.is_empty():
            raise IndexError(f'User {self.name} has no recips')
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

    def add_recipe(self, user_id: int, recipe_name: str):
        user = self.__get_user(user_id)
        user.add_recipe(recipe_name)

    def list_recipes(self, user_id: int) -> list[Recipe]:
        user = self.__get_user(user_id)
        return user.list_recipes()

    def remove_recipe(self, user_id: int, recipe: Recipe):
        user = self.__get_user(user_id)
        user.remove_recipe(recipe)

    def take_random_recipe(self, user_id: int) -> Recipe:
        user = self.__get_user(user_id)
        return user.take_random_recipe()


if __name__ == '__main__':
    db = RecipeDB()
    test_user_id = '42'

    recipes = db.list_recipes(test_user_id)
    assert recipes == []

    test_recipe = {'name': 'kukuha', 'is_used': False}
    db.add_recipe(test_user_id, test_recipe['name'])
    recipes = db.list_recipes(test_user_id)
    assert recipes[0].dict() == test_recipe

    test_recipe['is_used'] = True
    random_recipe = db.take_random_recipe(test_user_id)
    assert random_recipe.dict() == test_recipe

    random_recipe = db.take_random_recipe(test_user_id)
    assert random_recipe.dict() == test_recipe

    recipes = db.list_recipes(test_user_id)
    for r in recipes:
        db.remove_recipe(test_user_id, r)
    recipes = db.list_recipes(test_user_id)
    assert recipes == []
