import os
from random import choice
from typing import Optional
from bson.objectid import ObjectId

from pymongo import MongoClient
from pymongo.collection import Collection


class MongoRecipe:
    def __init__(self):
        user = os.environ['MONGO_USER']
        password = os.environ['MONGO_PASSWORD']
        host = os.environ['MONGO_HOST']
        port = os.environ['MONGO_PORT']
        db_name = os.environ['MONGO_DB']

        connection_string = f'mongodb://{user}:{password}@{host}:{port}'
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def __dispatch_user(self, id):
        return f'user{id}'

    def __get_user_collection(self, user_id: int) -> Collection:
        return self.db[self.__dispatch_user(user_id)]

    def insert_recipe(self, user_id: int, recipe: str) -> None:
        if not isinstance(recipe, str):
            raise TypeError('recipe must be a string')

        new_recipe = {
            'name': recipe,
            'details': '',
            'used': False,
        }
        user_collection = self.__get_user_collection(user_id)
        user_collection.insert_one(new_recipe)

    def list_user(self) -> list:
        return self.db.list_collection_names()

    def list_recipe(self, user_id: int) -> list:
        user_collection = self.__get_user_collection(user_id)
        projection = {
            '_id': False,
            'details': False,
        }
        cursor = user_collection.find(projection=projection)
        return [doc for doc in cursor]

    def list_unused_recipe_id(self, user_id: int) -> list:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'used': False,
        }
        projection = {
            '_id': True
        }
        cursor = user_collection.find(filter=filter, projection=projection)
        return [doc['_id'] for doc in cursor]

    def take_recipe(self, user_id: int, object_id: ObjectId) -> Optional[str]:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            '_id': object_id,
            'used': False,
        }
        update = {
            '$set': {'used': True}
        }
        document = user_collection.find_one_and_update(filter=filter,
                                                       update=update)
        try:
            recipe = document['name']
        except TypeError:
            recipe = None

        return recipe

    def is_empty_user(self, user_id: int) -> bool:
        user_collection = self.__get_user_collection(user_id)
        exist_doc = user_collection.find_one()
        return not bool(exist_doc)

    def tag_all_as_unused(self, user_id: int) -> None:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'used': True
        }
        update = {
            '$set': {'used': False}
        }
        user_collection.update_many(filter=filter, update=update)

    def random_recipe(self, user_id: int) -> str:
        if self.is_empty_user(user_id):
            raise IndexError('There is no recipes')
        recipes = self.list_unused_recipe_id(user_id)
        if recipes:
            random_recipe = self.take_recipe(user_id, choice(recipes))
        else:
            self.tag_all_as_unused(user_id)
            random_recipe = self.random_recipe(user_id)
        return random_recipe

    def change_details(self, user_id: int, recipe: str, details: str) -> None:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'name': recipe,
        }
        update = {
            '$set': {'details': details}
        }
        user_collection.update_one(filter=filter, update=update)

    def change_recipe_name(
        self, user_id: int, recipe: str, new_name: str
    ) -> None:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'name': recipe,
        }
        update = {
            '$set': {'name': new_name}
        }
        user_collection.update_one(filter=filter, update=update)

    def get_recipe_details(self, user_id: int, recipe: str) -> str:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'name': recipe,
        }
        projection = {
            '_id': False,
            'details': True,
        }
        document = user_collection.find_one(filter=filter,
                                            projection=projection)
        if document:
            details = document['details']
        else:
            details = None
        return details

    def delete_recipe(self, user_id: int, recipe: str) -> None:
        user_collection = self.__get_user_collection(user_id)
        filter = {
            'name': recipe,
        }
        user_collection.delete_one(filter=filter)


if __name__ == '__main__':
    db = MongoRecipe()
    # print(db.list_user())
    # print(db.create_user(15))
    print(db.list_user())
    # print(db.list_recipe(1))
    # print(db.insert_recipe(13, 'kartoshka'))
    # print(db.list_recipe(13))
    # unused_rec = db.list_unused_recipe_id(13)
    # print(unused_rec)
    # print(db.take_recipe(13, choice(unused_rec)))
    # print(db.list_unused_recipe_id(13))
    print(db.list_recipe(272502933))
    print(db.is_empty_user(272502933))
    u_r = db.list_unused_recipe_id(272502933)
    print(db.take_recipe(272502933, choice(u_r)))
    # print(db.take_recipe(272502933, ObjectId('60d7039b7732911c74cf7dfe')))
