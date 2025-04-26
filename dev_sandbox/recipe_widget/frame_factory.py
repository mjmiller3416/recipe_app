# recipe_cards/frame_factory.py
# ────────────────────────────────────────────────────────────────────────────────

"""
FrameFactory
============
Single responsibility: **return a fully-built `QFrame`** for a given
widget *state* (“recipe”, “empty”, or “error”) and *size*.

External code never sees the builders directly; they stay private to
the recipe_cards package.
"""

#🔸Third-party
from PySide6.QtWidgets import QFrame

#🔸Local Imports
from .builders.empty_state_builder import EmptyStateBuilder
from .builders.error_state_builder import ErrorStateBuilder
from .builders.recipe_card_builder import RecipeCardBuilder
from .constants import LayoutSize

# ────────────────────────────────────────────────────────────────────────────────


class FrameFactory:
    """
    A thin façade that delegates to the correct *StateBuilder*.

    Usage
    -----
        frame = FrameFactory.make("recipe", LayoutSize.SMALL, my_recipe)
    """

    # ── public ──────────────────────────────────────────────────────────────────────
    @classmethod
    def make(
        cls,
        state: str,
        size: LayoutSize,
        recipe=None,   # Recipe | None – kept untyped to avoid circular import
    ) -> QFrame:
        """
        Parameters
        ----------
        state : {'recipe', 'empty', 'error'}
            Which visual state to build.
        size : LayoutSize
            Target card size (SMALL / MEDIUM / LARGE).
        recipe : Recipe | None, optional
            Required only for the 'recipe' state.

        Returns
        -------
        QFrame
            Fully styled, fixed-size frame ready to insert into a layout.

        Raises
        ------
        ValueError
            If `state` is not recognised or required params are missing.
        """
        match state:
            case "recipe":
                if recipe is None:
                    raise ValueError("Recipe must be provided for 'recipe' state")
                return RecipeCardBuilder(size, recipe).build()

            case "empty":
                return EmptyStateBuilder(size).build()

            case "error":
                return ErrorStateBuilder(size).build()

            case _:
                raise ValueError(f"Unknown state: {state!r}")
