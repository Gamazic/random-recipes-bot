from bson import json_util
from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """
    Recipe. Consists of the name and usage flag fields.
    """
    name: str
    is_used: bool = False


class RecipeWithId(Recipe):
    """
    Recipe with MongoDB index ID.
    """
    id: ObjectId = Field(alias='_id')

    class Config:
        arbitrary_types_allowed = True
        json_dumps = json_util.dumps
        json_loads = json_util.loads
