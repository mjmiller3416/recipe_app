"""database/models/saved_meal_state.py

SavedMealState model for storing the state of saved meals in the database.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from database.base_model import ModelBase

# ── Class Definition ────────────────────────────────────────────────────────────
class SavedMealState(ModelBase):
    meal_id: int