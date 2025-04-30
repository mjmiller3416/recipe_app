from typing import Optional, Any, Dict
from pydantic import Field, model_validator
from database.base_model import ModelBase

class Recipe(ModelBase):
    """
    Pydantic model for the `recipes` table.
    """
    recipe_name: str = Field(..., min_length=1, description="Name of the recipe")
    recipe_category: str = Field(..., min_length=1, description="Category of the recipe")
    total_time: Optional[int] = Field(None, ge=0, description="Total cook time in minutes")
    servings: Optional[int] = Field(None, ge=1, description="Number of servings")
    directions: Optional[str] = Field(None, description="Preparation instructions")
    image_path: Optional[str] = Field(None, description="Path to recipe image")

    @model_validator(mode="before")
    def strip_strings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # Trim whitespace on all string fields
        for field in ("recipe_name", "recipe_category", "directions", "image_path"):
            value = values.get(field)
            if isinstance(value, str):
                values[field] = value.strip()
        return values

    def formatted_time(self) -> str:
        """
        Returns a human-readable time display (e.g., '1h 30m').
        """
        if not self.total_time:
            return ""
        hrs, mins = divmod(self.total_time, 60)
        return f"{hrs}h {mins}m" if hrs else f"{mins}m"
