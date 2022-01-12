from aiogram.types import ParseMode

from app.gui.markups import recipe_details_markup
from app.recipe_shema import RecipeWithId


def create_recipe_details_layout(recipe: RecipeWithId) -> dict:
    markup = recipe_details_markup(recipe)
    is_used_status_line = 'Использован \U0001F373' if recipe.is_used else '*Неиспользован*'
    details_text = 'Рецепт:\n' \
                   f'*{recipe.name}*\n' \
                   f'Статус: *{is_used_status_line}*'
    return dict(text=details_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
