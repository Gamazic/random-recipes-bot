import pytest


@pytest.fixture
def user_id():
    return 'TEST_USER'


@pytest.fixture
def recipe_name():
    return 'TEST_RECIPE_NAME'


@pytest.fixture
def db():
    from app import db
    return db


async def test_db_func(db, user_id, recipe_name):
    """
    So far, a temporary unified test function.
    The only one because pytest and my db code are difficult
    to make friends without crutches.
    """
    # test_does_user_have_recipes
    user_have_recipes = await db.does_user_have_recipes(user_id)
    assert user_have_recipes is False

    # test_add_recipe_by_name
    await db.add_recipe_by_name(user_id, recipe_name)
    recipe_name_filter = {'name': recipe_name}
    collection = db._dispatch_user_id(user_id)
    recipe_with_same_name = await collection.find_one(filter=recipe_name_filter)
    assert recipe_with_same_name is not None

    # test_does_user_have_used_recipes
    user_have_used_recipes = await db.does_user_have_used_recipes(user_id)
    assert user_have_used_recipes is False

    # test_list_user_recipes
    user_recipes = await db.list_user_recipes(user_id)
    assert len(user_recipes) == 1
    recipe = user_recipes[0]
    assert recipe.name == recipe_name

    # test_find_recipe_by_id
    finded_recipe = await db.find_recipe_by_id(user_id, recipe.id)
    assert finded_recipe == recipe

    # test_take_recipe_by_id
    taken_recipe = await db.take_recipe_by_id(user_id, recipe.id)
    assert taken_recipe.is_used is True
    finded_recipe = await db.find_recipe_by_id(user_id, recipe.id)
    assert finded_recipe.is_used is True

    # test_unuse_recipe_by_id
    await db.unuse_recipe_by_id(user_id, recipe.id)
    finded_recipe = await db.find_recipe_by_id(user_id, recipe.id)
    assert finded_recipe.is_used is False

    # test_take_random_recipe
    recipe_name2 = recipe_name + '2'
    await db.add_recipe_by_name(user_id, recipe_name2)

    random_recipe1 = await db.take_random_recipe(user_id)
    assert random_recipe1.is_used is True
    recipes_with_one_used = await db.list_user_recipes(user_id)
    number_of_used = sum(cur_recipe.is_used for cur_recipe in recipes_with_one_used)
    assert number_of_used == 1

    random_recipe2 = await db.take_random_recipe(user_id)
    assert random_recipe2.is_used is True
    recipes_with_two_used = await db.list_user_recipes(user_id)
    number_of_used = sum(cur_recipe.is_used for cur_recipe in recipes_with_two_used)
    assert number_of_used == 2

    # test_unuse_all_recipes
    await db.unuse_all_recipes(user_id)
    not_used_recipes = await db.list_user_recipes(user_id)
    number_of_used = sum(cur_recipe.is_used for cur_recipe in not_used_recipes)
    assert number_of_used == 0

    # test_remove_recipe_by_id
    random_recipe = await db.take_random_recipe(user_id)
    await db.remove_recipe_by_id(user_id, random_recipe.id)
    user_recipes = await db.list_user_recipes(user_id)
    assert len(user_recipes) == 1

    random_recipe = await db.take_random_recipe(user_id)
    await db.remove_recipe_by_id(user_id, random_recipe.id)
    user_recipes = await db.list_user_recipes(user_id)
    assert len(user_recipes) == 0
