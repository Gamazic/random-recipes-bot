from aiogram.types import ParseMode

from app.keyboards.markups import recipe_details_markup
from app.recipe_shema import RecipeWithId
from app.data.messages_text import (IS_USED_RECIPE_DETAILS_MESSAGE,
                                    IS_UNUSED_RECIPE_DETAILS_MESSAGE,
                                    SINGLE_SHOWN_RECIPE_MESSAGE)


def create_recipe_details_layout(recipe: RecipeWithId) -> dict:
    """Create recipe details keyboard markup, text for message.

    Args:
        recipe (RecipeWithId): recipe.

    Returns:
        dict: actually kwargs for methods like
              `bot.send_message`, `message.answer`, `bot.edit_message_text` and etc.
    """
    markup = recipe_details_markup(recipe)
    is_used_status_line = IS_USED_RECIPE_DETAILS_MESSAGE if recipe.is_used else IS_UNUSED_RECIPE_DETAILS_MESSAGE
    details_text = f'{SINGLE_SHOWN_RECIPE_MESSAGE}' \
                   f'*{recipe.name}*\n' \
                   f'{is_used_status_line}'
    return dict(text=details_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
