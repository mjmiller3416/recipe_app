"""app/ui/components/recipe_card/frame_factory.py

Provides the FrameFactory class for generating fully-built QFrames based on widget states ('recipe', 'empty', or 'error').
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QFrame

from .builders.empty_state import EmptyState
from .builders.error_state import ErrorState
from .builders.recipe_state import RecipeCard
from .constants import LayoutSize


# ── Class Definition ────────────────────────────────────────────────────────────
class FrameFactory:
    """A thin façade that delegates to the correct StateBuilder.

    Example:
        frame = FrameFactory.make("recipe", LayoutSize.SMALL, my_recipe)
    """

    # ── Public Methods ──────────────────────────────────────────────────────────────
    @classmethod
    def make(
        cls,
        state: str,
        size: LayoutSize,
        recipe=None
    ) -> QFrame:
        """Build and return a fully constructed QFrame for a given widget state.

        Args:
            state (str): The widget state to build ('recipe', 'empty', or 'error').
            size (LayoutSize): Target card size (small, medium, or large).
            recipe (Recipe | None, optional): Required only for the 'recipe' state.

        Returns:
            QFrame: Fully styled, fixed-size frame ready to insert into a layout.

        Raises:
            ValueError: If `state` is not recognized or required parameters are missing.
        """
        match state:
            case "recipe":
                if recipe is None:
                    raise ValueError("Recipe must be provided for 'recipe' state")
                return RecipeCard(size, recipe).build()

            case "empty":
                return EmptyState(size).build()

            case "error":
                return ErrorState(size).build()

            case _:
                raise ValueError(f"Unknown state: {state!r}")
