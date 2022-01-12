from app.gui.markups import recipe_details_markup
from app.recipe_shema import RecipeWithId


def create_recipe_details_layout(recipe: RecipeWithId) -> dict:
    markup = recipe_details_markup(recipe)
    is_used_status_line = 'Использован \U0001F373' if recipe.is_used else '*Неиспользован*'
    details_text = 'Рецепт:\n' \
                   f'*{recipe.name}*\n' \
                   f'Статус: *{is_used_status_line}*'
    return dict(text=details_text, reply_markup=markup)


def create_recipes_list_layout(chat_id: int, db: Database) -> dict:
    # TODO: Можно избавится от этого метода и в колбеке вызывать show_recipes_list.
    # Для этого нужно удалять предыдущий layout с recipe_details.
    recipes = db.list_user_recipes(chat_id)
    if not recipes:
        return dict(text='Список рецептов пуст.')
    else:
        markup = recipes_list_inline_keyboard_markup(recipes)
        text = 'Список рецептов:'
        return dict(text=text, reply_markup=markup)
