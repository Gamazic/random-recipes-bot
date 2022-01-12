"""Кастомные исключения, генерируемые приложением"""


class UserHasNoRecipesError(Exception):
    """В базе данных отсутсвуют рецепты для пользователя"""
    pass


class UserHasNoSelectedRecipeError(Exception):
    """В базе данных отсутсвует конкретный рецепт для пользователя"""
    pass
