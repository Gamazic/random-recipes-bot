class UserHasNoRecipesError(Exception):
    """There is no recipes of user in DB"""
    pass


class UserHasNoSelectedRecipeError(Exception):
    """There is no selected recipe of user in DB"""
    pass
