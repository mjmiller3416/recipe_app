# ── Imports ─────────────────────────────────────────────────────────────────────
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RecipeIngredient:
    ingredient_id:   Optional[int]           # can be None for new rows
    ingredient_name: str
    ingredient_category: str
    quantity:        float
    unit:            str

    # convenience
    def __str__(self) -> str:
        q = f"{self.quantity:g} " if self.quantity else ""
        u = f"{self.unit} "        if self.unit else ""
        return f"{q}{u}{self.ingredient_name}".strip()

@dataclass
class Recipe:
    id:             Optional[int]
    recipe_name:    str
    recipe_category:str
    total_time:     int
    servings:       int
    directions:     str
    image_path:     Optional[str] = None
    ingredients:    List[RecipeIngredient] = field(default_factory=list)

    # module helpers
    def has_image(self) -> bool:
        return bool(self.image_path)

    def formatted_total_time(self) -> str:
        return f"{self.total_time} min"

    def formatted_servings(self) -> str:
        return str(self.servings)
