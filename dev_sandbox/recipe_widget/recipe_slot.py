# recipe_widget/recipe_slot.py
# ────────────────────────────────────────────────────────────────────────────────
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QPushButton, QStackedWidget, QVBoxLayout

from core.modules.recipe_module import Recipe

from .constants import LayoutSize
from .frame_factory import FrameFactory

# ────────────────────────────────────────────────────────────────────────────────


class RecipeSlot(QFrame):
    """
    A *fixed-size placeholder* that can display one of three **states**

    * Empty   – big “+” button
    * Recipe  – image, title, meta
    * Error   – red message (when builder blows up)

    It exposes **three generic signals** so parent views decide what to do:

    empty_clicked()                – user clicked the + button
    card_clicked(recipe: Recipe)   – user clicked the populated card
    delete_clicked(recipe_id: int) – (reserved) delete action, not wired yet
    """

    empty_clicked  = Signal()
    card_clicked   = Signal(object)   # Recipe instance
    delete_clicked = Signal(int)

    def __init__(self, size: LayoutSize, parent=None) -> None:
        super().__init__(parent, objectName="RecipeSlot")

        self._size:   LayoutSize      = size
        self._recipe: Optional[Recipe] = None

        # initialize stacked widget
        self._stack = QStackedWidget(self)

        # create layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._stack)

        # build state frames
        self._empty_state  = FrameFactory.make("empty",  size)
        self._recipe_state = None        # created on demand
        self._error_state  = FrameFactory.make("error",  size)

        # add frame to stack
        self._stack.addWidget(self._empty_state)   # index 0
        self._stack.addWidget(QFrame())           # placeholder for recipe (idx 1)
        self._stack.addWidget(self._error_state)   # index 2

        # set initial visible frame
        self._stack.setCurrentIndex(0)
        self._wire_empty_button()

    # ── public ──────────────────────────────────────────────────────────────────────
    def set_recipe(self, recipe: Recipe | None) -> None:
        """
        Load a recipe (or None to clear).  Rebuilds the Recipe page but
        keeps Empty & Error pages intact.
        """
        if recipe is None:
            self._recipe = None
            self._stack.setCurrentIndex(0)
            return

        self._recipe = recipe
        try:
            new_frame = FrameFactory.make("recipe", self._size, recipe)
            self._swap_recipe_state(new_frame)
            self._stack.setCurrentIndex(1)
        except Exception as exc:        # pragma: no cover
            print("RecipeSlot error:", exc)
            self._stack.setCurrentIndex(2)

    def recipe(self) -> Recipe | None:
        """Return the currently displayed recipe (or None)."""
        return self._recipe

    # ── private ─────────────────────────────────────────────────────────────────────
    def _wire_empty_button(self) -> None:
        """
        Connect the '+ Add Meal' button inside the empty page
        to emit `empty_clicked`.
        """
        btn: QPushButton | None = self._empty_state.findChild(QPushButton, "AddMealButton")
        if btn:
            btn.clicked.connect(self.empty_clicked.emit)

    # --------------------------------------------------------------------------------
    def _swap_recipe_state(self, new_frame: QFrame) -> None:
        """Replace the existing recipe page (index 1) with a fresh one."""
        old = self._stack.widget(1)
        self._stack.removeWidget(old)
        old.deleteLater()

        # state name for QSS styling
        new_frame.setObjectName("RecipeStateFrame")

        self._stack.insertWidget(1, new_frame)
        self._recipe_page = new_frame

        # wire click to card_clicked
        new_frame.mousePressEvent = self._emit_card_clicked  # type: ignore

    # --------------------------------------------------------------------------------
    def _emit_card_clicked(self, event) -> None:  # Qt passes QMouseEvent
        if event.button() == Qt.LeftButton and self._recipe:
            self.card_clicked.emit(self._recipe)
