"""app/ui/views/recipe_browser/recipe_browser.py

Recipe browser view rendered with QListView + model/delegate for performance.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListView,
    QMenu,
    QMessageBox,
)

from _dev_tools import DebugLogger
from app.core import RecipeFilterDTO
from app.core.services import RecipeService
from app.ui.components.composite.recipe_card import LARGE_SIZE, LayoutSize, MEDIUM_SIZE, SMALL_SIZE
from app.ui.views.base import BaseView
from ._filter_bar import FilterBar
from .delegate import RecipeCardDelegate
from .models import RecipeFilterProxyModel, RecipeListModel


CARD_SIZE_BY_LAYOUT = {
    LayoutSize.SMALL: SMALL_SIZE,
    LayoutSize.MEDIUM: MEDIUM_SIZE,
    LayoutSize.LARGE: LARGE_SIZE,
}


class RecipeBrowser(BaseView):
    """Recipe browser view with filtering and sorting.

    Legacy note: this view previously built one QWidget per card inside a flow
    layout. It now uses a QListView with a model/delegate for faster redraws.
    """

    recipe_card_clicked = Signal(object)  # recipe object
    recipe_selected = Signal(int)  # recipe ID

    def __init__(
        self,
        parent=None,
        card_size: LayoutSize = LayoutSize.MEDIUM,
        selection_mode: bool = False,
        navigation_service=None,
    ):
        super().__init__(parent)
        self.setObjectName("RecipeBrowser")
        self.card_size = card_size
        self._selection_mode = selection_mode
        self.navigation_service = navigation_service
        self.recipe_service = RecipeService()
        self.recipes_loaded = False
        self._card_dimensions = CARD_SIZE_BY_LAYOUT.get(self.card_size, MEDIUM_SIZE)

        self._list_model = RecipeListModel(
            favorite_handler=self._persist_favorite,
            image_size=QSize(self._card_dimensions.width(), self._card_dimensions.width()),
        )
        self._proxy_model = RecipeFilterProxyModel()
        self._proxy_model.setSourceModel(self._list_model)

        self._build_ui()
        self._load_recipes()

    # Public API ----------------------------------------------------------
    @property
    def selection_mode(self):
        """Get the current selection mode."""
        return self._selection_mode

    @selection_mode.setter
    def selection_mode(self, value: bool):
        """Toggle selection mode (used by MealPlanner recipe picking)."""
        self._selection_mode = bool(value)

    def refresh(self):
        """Refresh the recipe display."""
        self.recipes_loaded = False
        self._load_recipes()

    # UI Construction -----------------------------------------------------
    def _build_ui(self):
        """Build the filter bar and the list view."""
        self._create_filter_bar()
        self._create_list_view()

    def _create_filter_bar(self):
        self.filter_bar = FilterBar(self)
        self.content_layout.addWidget(self.filter_bar)
        self.filter_bar.filters_changed.connect(self._apply_filters)

    def _create_list_view(self):
        self._list_view = QListView(self)
        self._list_view.setObjectName("RecipeListView")
        self._list_view.setViewMode(QListView.IconMode)
        self._list_view.setResizeMode(QListView.Adjust)
        self._list_view.setMovement(QListView.Static)
        self._list_view.setWrapping(True)
        self._list_view.setSpacing(16)
        self._list_view.setUniformItemSizes(True)
        self._list_view.setMouseTracking(True)
        self._list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list_view.setSelectionRectVisible(False)
        self._list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._list_view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list_view.customContextMenuRequested.connect(self._show_context_menu)
        self._list_view.clicked.connect(self._handle_card_clicked)
        self._list_view.setStyleSheet(
            "QListView { background: transparent; border: none; padding: 6px; }"
            "QListView::item { background: transparent; }"
        )

        delegate = RecipeCardDelegate(self._list_view, card_size=self._card_dimensions)
        self._list_view.setItemDelegate(delegate)
        self._list_view.setGridSize(delegate.sizeHint() + QSize(8, 12))
        self._list_view.setModel(self._proxy_model)

        self.content_layout.addWidget(self._list_view)

    # Data Loading --------------------------------------------------------
    def _load_recipes(self):
        """Load recipes with default filter (unfiltered, sorted by name)."""
        default_filter_dto = RecipeFilterDTO(
            recipe_category=None,
            sort_by="recipe_name",
            sort_order="asc",
            favorites_only=False,
        )
        self._fetch_and_bind_recipes(default_filter_dto)
        self._apply_filters()

    def _fetch_and_bind_recipes(self, filter_dto: RecipeFilterDTO):
        """Fetch from service and push into the model."""
        recipes = self.recipe_service.list_filtered(filter_dto)
        self._list_model.load_recipes(recipes)
        self.recipes_loaded = True

    # Filtering / Sorting -------------------------------------------------
    def _apply_filters(self):
        """Update proxy filters based on the filter bar state."""
        filter_state = self.filter_bar.getFilterState()
        self._proxy_model.set_category_filter(filter_state["category"])
        self._proxy_model.set_sort_mode(filter_state["sort"])
        self._proxy_model.set_favorites_only(filter_state["favorites_only"])
        self._proxy_model.sort(0)

    # Interaction ---------------------------------------------------------
    def _handle_card_clicked(self, proxy_index):
        """Handle list view clicks, forwarding to navigation or selection."""
        if not proxy_index.isValid():
            return

        source_index = self._proxy_model.mapToSource(proxy_index)
        recipe = self._list_model.get_recipe(source_index)
        if recipe is None:
            return

        if self._selection_mode and getattr(recipe, "id", None) is not None:
            self.recipe_selected.emit(recipe.id)
            return

        if self.navigation_service:
            self.navigation_service.show_full_recipe(recipe)
        else:
            self.recipe_card_clicked.emit(recipe)

    def _show_context_menu(self, point: QPoint):
        """Context menu for edit/favorite/delete on a recipe card."""
        index = self._list_view.indexAt(point)
        if not index.isValid():
            return

        source_index = self._proxy_model.mapToSource(index)
        recipe = self._list_model.get_recipe(source_index)
        if recipe is None:
            return

        menu = QMenu(self)
        act_edit = menu.addAction("Edit Recipe")
        fav_label = "Remove from Favorites" if getattr(recipe, "is_favorite", False) else "Add to Favorites"
        act_fav = menu.addAction(fav_label)
        act_delete = menu.addAction("Delete Recipe")

        chosen = menu.exec(self._list_view.viewport().mapToGlobal(point))
        if chosen == act_edit:
            self._handle_edit_request(recipe)
        elif chosen == act_fav:
            self._toggle_favorite_from_context(source_index, recipe)
        elif chosen == act_delete and getattr(recipe, "id", None):
            self._handle_delete_request(recipe.id)

    def _toggle_favorite_from_context(self, source_index, recipe):
        current = bool(getattr(recipe, "is_favorite", False))
        self._list_model.setData(source_index, not current, RecipeListModel.FAVORITE_ROLE)

    def _handle_edit_request(self, recipe):
        """Handle edit requests from a recipe card context menu."""
        if self.navigation_service and getattr(recipe, "id", None):
            self.navigation_service.start_edit_recipe(recipe.id)
        else:
            # Fallback: emit card clicked to allow external handling
            self.recipe_card_clicked.emit(recipe)

    def _handle_delete_request(self, recipe_id: int):
        """Handle recipe deletion with confirmation and refresh."""
        reply = QMessageBox.question(
            self,
            "Delete Recipe",
            "Are you sure you want to delete this recipe?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            service = RecipeService()
            if service.delete_recipe(recipe_id):
                self.refresh()
                from app.ui.components.widgets import show_toast

                show_toast(self, "Recipe deleted.", success=True, duration=2000, offset_right=40)
        except Exception as exc:
            DebugLogger.log(f"Failed to delete recipe {recipe_id}: {exc}", "error")

    # Persistence helpers -------------------------------------------------
    def _persist_favorite(self, recipe, new_value: bool):
        """Persist favorite toggle and return the updated recipe."""
        if not getattr(recipe, "id", None):
            return None
        try:
            updated = self.recipe_service.toggle_favorite(recipe.id)
            return updated
        except Exception as exc:
            DebugLogger.log(f"Failed to persist favorite toggle: {exc}", "error")
            return None
