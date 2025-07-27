"""app/ui/components/recipe_card/recipe_card.py

Defines the RecipeCard class that acts as a dynamic container for different recipe states (empty, recipe, error).
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDialog, QFrame, QPushButton, QStackedWidget,
                               QVBoxLayout)

from app.core.database.db import create_session
from app.core.models.recipe import Recipe
from app.core.services.recipe_service import RecipeService
from app.ui.components.dialogs.full_recipe import FullRecipe
from dev_tools import DebugLogger, StartupTimer

from .constants import LayoutSize
from .frame_factory import FrameFactory


# ── Recipe Card ──────────────────────────────────────────────────────────────────────────────
class RecipeCard(QFrame):
    """A fixed-size placeholder that can display one of three states: empty, recipe, or error.

    The slot exposes three signals allowing parent views to respond to user interactions:
    - empty_clicked(): User clicked the '+ Add Meal' button.
    - card_clicked(recipe: Recipe): User clicked the populated card.
    - delete_clicked(recipe_id: int): (Reserved) Delete action, not yet wired.
    """

    # ── Signals ──────────────────────────────────────────────────────────────────────────────
    add_meal_clicked = Signal()
    card_clicked     = Signal(object) # recipe instance
    delete_clicked   = Signal(int)    # recipe_id
    recipe_selected  = Signal(int)    # recipe_id

    def __init__(self, size: LayoutSize, parent=None) -> None:
        """Initialize the RecipeCard with stacked empty, recipe, and error states."""
        super().__init__(parent, objectName="RecipeCard")

        self.setAttribute(Qt.WA_StyledBackground, True)
        self._size:   LayoutSize      = size
        self._recipe: Optional[Recipe] = None
        self._recipe_selection_dialog: Optional[QDialog] = None
        self._selection_mode: bool = False  # When True, prevents FullRecipe dialog from opening

        # ── Create Stacked Widget ──
        self._stack = QStackedWidget(self)

        # ── Create Layout ──
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self._stack) # add to layout

        # ── Build State Frames ──
        self._empty_state  = FrameFactory.make("empty",  size)
        self._recipe_state = None # created on demand
        self._error_state  = FrameFactory.make("error",  size)

        # ── Add Frames to Stack ──
        self._stack.addWidget(self._empty_state)   # index 0
        self._stack.addWidget(QFrame())            # placeholder for recipe (idx 1)
        self._stack.addWidget(self._error_state)   # index 2

        # ── Set Initial Frame ──
        self._stack.setCurrentIndex(0)
        self._wire_empty_button()

    # ── Public Methods ───────────────────────────────────────────────────────────────────────
    def set_recipe(self, recipe: Recipe | None) -> None:
        """Load or clear a recipe in this `RecipeCard`.
        Args:
            recipe (Recipe | None): The `Recipe` object to display.
                • `None` → revert to the empty state.
        """
        # ── Clear Slots ──
        if recipe is None:
            self._recipe = None
            self._stack.setCurrentIndex(0) # show empty page

            # optionally inform listeners we cleared the slot
            # self.recipe_selected.emit(-1)

            return

        # ── Build Recipe Card ──
        self._recipe = recipe
        try:
            new_frame = FrameFactory.make("recipe", self._size, recipe)
            self._swap_recipe_state(new_frame)        # replace old card
            self._stack.setCurrentIndex(1)            # show recipe page

            # wire click to card_clicked
            new_frame.mousePressEvent = self._emit_card_clicked

            # emit recipe ID
            rid = getattr(recipe, "id", getattr(recipe, "recipe_id", None))
            if rid is not None:
                self.recipe_selected.emit(rid)

        except Exception as exc:                      # catch render errors
            DebugLogger.log("RecipeCard failed to build card: {exc}", "error", exc=exc)
            self._stack.setCurrentIndex(2)            # show error page

    def set_selection_mode(self, selection_mode: bool) -> None:
        """Set whether this card is in selection mode.

        Args:
            selection_mode (bool): If True, clicking the card won't open FullRecipe dialog.
        """
        self._selection_mode = selection_mode

    def recipe(self) -> Recipe | None:
        """Return the currently displayed recipe (or None)."""
        return self._recipe

    # ── Private Methods ──────────────────────────────────────────────────────────────────────
    def _wire_empty_button(self) -> None:
        """
        Connect the '+ Add Meal' button inside the empty page
        to emit `empty_clicked`.
        """
        btn: QPushButton | None = self._empty_state.findChild(QPushButton, "AddMealButton")
        if btn:
            btn.clicked.connect(self._handle_add_meal_click)

    def _swap_recipe_state(self, new_frame: QFrame) -> None:
        """Replace the existing recipe page (index 1) with a fresh one."""
        # remove old frame (index 1) and delete it
        old = self._stack.widget(1)
        self._stack.removeWidget(old)
        old.deleteLater()

        new_frame.setObjectName("RecipeCard") # set object name
        new_frame.setAttribute(Qt.WA_StyledBackground, True) # styled background is enabled

        # add new frame (index 1) and set it as the current page
        self._stack.insertWidget(1, new_frame)
        self._recipe_page = new_frame

        # wire click to card_clicked
        new_frame.mousePressEvent = self._emit_card_clicked

    def _emit_card_clicked(self, event) -> None:
        """Emit the card_clicked signal and optionally open the recipe dialog."""
        if event.button() == Qt.LeftButton and self._recipe:
            self.card_clicked.emit(self._recipe)

            # open the recipe dialog
            if not self._selection_mode:  # Prevent opening in selection mode
                dlg = FullRecipe(self._recipe)
                dlg.exec()

    def _handle_add_meal_click(self):
        """
        Handle the click event for the 'Add Meal' button in the empty state by emitting a signal.
        """
        self.add_meal_clicked.emit()

    def _on_recipe_selection_finished(self, result: int) -> None:
        """Callback for when the recipe selection dialog is finished."""
        if self._recipe_selection_dialog is None:
            return

        if result == QDialog.Accepted:
            selected_recipe = self._recipe_selection_dialog.selected_recipe()
            if selected_recipe:
                self.set_recipe(selected_recipe)
            else:
                DebugLogger.log("No recipe selected in recipe selection dialog", "debug")
        else:
            DebugLogger.log("Recipe selection dialog cancelled by user", "debug")

        self._recipe_selection_dialog.deleteLater()
        self._recipe_selection_dialog = None
