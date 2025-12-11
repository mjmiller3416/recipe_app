"""Models and proxy filters for the recipe browser grid.

This replaces the legacy widget-per-card approach with a lightweight
QAbstractListModel + QSortFilterProxyModel stack to back the delegate-based
recipe grid.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Sequence

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSortFilterProxyModel, QSize
from PySide6.QtGui import QPixmap

from _dev_tools import DebugLogger
from app.core.utils.image_utils import (
    img_cache_get,
    img_cache_get_key,
    img_cache_set,
    img_get_placeholder,
    img_qt_load_safe,
    img_resize_to_size,
    img_validate_path,
)


@dataclass
class RecipeRecord:
    """Lightweight view record for a recipe item."""

    recipe: object
    pixmap: QPixmap


class RecipeListModel(QAbstractListModel):
    """Qt model representing the recipes shown in the browser grid."""

    TITLE_ROLE = Qt.UserRole + 1
    IMAGE_ROLE = Qt.UserRole + 2
    SERVINGS_ROLE = Qt.UserRole + 3
    TIME_ROLE = Qt.UserRole + 4
    FAVORITE_ROLE = Qt.UserRole + 5
    ID_ROLE = Qt.UserRole + 6
    CATEGORY_ROLE = Qt.UserRole + 7
    CREATED_ROLE = Qt.UserRole + 8
    SORT_TIME_ROLE = Qt.UserRole + 9
    SORT_SERVINGS_ROLE = Qt.UserRole + 10
    RECIPE_ROLE = Qt.UserRole + 11

    def __init__(
        self,
        favorite_handler: Optional[Callable[[object, bool], Optional[object]]] = None,
        image_size: QSize | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._recipes: list[RecipeRecord] = []
        self._favorite_handler = favorite_handler
        self._image_size = image_size or QSize(260, 260)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._recipes)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._recipes)):
            return None

        record = self._recipes[index.row()]
        recipe = record.recipe

        if role in (Qt.DisplayRole, self.TITLE_ROLE):
            return getattr(recipe, "recipe_name", "")
        if role == self.IMAGE_ROLE:
            return record.pixmap
        if role == self.SERVINGS_ROLE:
            if hasattr(recipe, "formatted_servings"):
                return recipe.formatted_servings()
            servings = getattr(recipe, "servings", None)
            return str(servings) if servings is not None else ""
        if role == self.TIME_ROLE:
            if hasattr(recipe, "formatted_time"):
                return recipe.formatted_time()
            total_time = getattr(recipe, "total_time", None)
            if total_time is None:
                return ""
            hours, minutes = divmod(int(total_time), 60)
            return f"{hours}h {minutes}m" if hours else f"{minutes}m"
        if role == self.FAVORITE_ROLE:
            return bool(getattr(recipe, "is_favorite", False))
        if role == self.ID_ROLE:
            return getattr(recipe, "id", None)
        if role == self.CATEGORY_ROLE:
            return getattr(recipe, "recipe_category", None)
        if role == self.CREATED_ROLE:
            return getattr(recipe, "created_at", None)
        if role == self.SORT_TIME_ROLE:
            return getattr(recipe, "total_time", None) or 0
        if role == self.SORT_SERVINGS_ROLE:
            return getattr(recipe, "servings", None) or 0
        if role == self.RECIPE_ROLE:
            return recipe
        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:  # noqa: N802
        if role != self.FAVORITE_ROLE or not index.isValid():
            return False

        record = self._recipes[index.row()]
        recipe = record.recipe
        old_value = bool(getattr(recipe, "is_favorite", False))
        new_value = bool(value)

        if old_value == new_value:
            return False

        try:
            recipe.is_favorite = new_value
            if self._favorite_handler:
                updated = self._favorite_handler(recipe, new_value)
                if updated is not None:
                    recipe = updated
                    recipe.is_favorite = getattr(updated, "is_favorite", new_value)
                    self._recipes[index.row()] = RecipeRecord(updated, record.pixmap)
                    new_value = recipe.is_favorite
        except Exception as exc:  # pragma: no cover - defensive logging
            DebugLogger.log(f"Failed to toggle favorite via model: {exc}", "error")
            recipe.is_favorite = old_value
            return False

        self.dataChanged.emit(index, index, [self.FAVORITE_ROLE])
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        default_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if not index.isValid():
            return default_flags
        return default_flags | Qt.ItemIsEditable

    def roleNames(self) -> dict[int, bytes]:  # noqa: N802
        return {
            self.TITLE_ROLE: b"title",
            self.IMAGE_ROLE: b"image",
            self.SERVINGS_ROLE: b"servings",
            self.TIME_ROLE: b"time",
            self.FAVORITE_ROLE: b"favorite",
            self.ID_ROLE: b"id",
            self.CATEGORY_ROLE: b"category",
            self.CREATED_ROLE: b"created_at",
            self.SORT_TIME_ROLE: b"total_time",
            self.SORT_SERVINGS_ROLE: b"servings_value",
            self.RECIPE_ROLE: b"recipe",
        }

    def load_recipes(self, recipes: Sequence[object]) -> None:
        """Load a new set of recipes into the model."""
        records: list[RecipeRecord] = []
        for recipe in recipes:
            pixmap = self._load_pixmap_for_recipe(recipe)
            records.append(RecipeRecord(recipe=recipe, pixmap=pixmap))

        self.beginResetModel()
        self._recipes = records
        self.endResetModel()

    def get_recipe(self, index: QModelIndex) -> Optional[object]:
        """Return the backing recipe object for the given index."""
        if not index.isValid() or not (0 <= index.row() < len(self._recipes)):
            return None
        return self._recipes[index.row()].recipe

    def _load_pixmap_for_recipe(self, recipe: object) -> QPixmap:
        """Pre-load and cache a scaled pixmap for a recipe image."""
        path = getattr(recipe, "reference_image_path", None)
        cache_key = img_cache_get_key(path or "placeholder", size=self._image_size)
        cached = img_cache_get(cache_key)
        if cached:
            return cached

        if path and img_validate_path(path):
            pixmap = img_qt_load_safe(path)
        else:
            pixmap = img_get_placeholder(self._image_size)

        scaled = img_resize_to_size(pixmap, self._image_size)
        img_cache_set(cache_key, scaled)
        return scaled


class RecipeFilterProxyModel(QSortFilterProxyModel):
    """Proxy model handling recipe filtering and sorting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDynamicSortFilter(True)
        self._category_filter: Optional[str] = None
        self._favorites_only: bool = False
        self._sort_mode: str = "A-Z"

    def set_category_filter(self, category: Optional[str]) -> None:
        normalized = None if category in (None, "", "All", "Filter") else category
        if self._category_filter == normalized:
            return
        self._category_filter = normalized
        self.invalidateFilter()

    def set_favorites_only(self, enabled: bool) -> None:
        if self._favorites_only == bool(enabled):
            return
        self._favorites_only = bool(enabled)
        self.invalidateFilter()

    def set_sort_mode(self, mode: str) -> None:
        if not mode:
            mode = "A-Z"
        if self._sort_mode == mode:
            return
        self._sort_mode = mode
        self.invalidate()
        self.sort(0)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        model: RecipeListModel = self.sourceModel()  # type: ignore[assignment]
        if not model:
            return False

        index = model.index(source_row, 0, source_parent)
        recipe = model.get_recipe(index)
        if recipe is None:
            return False

        if self._favorites_only and not getattr(recipe, "is_favorite", False):
            return False

        if self._category_filter:
            return getattr(recipe, "recipe_category", None) == self._category_filter

        return True

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa: N802
        model: RecipeListModel = self.sourceModel()  # type: ignore[assignment]
        if not model:
            return False

        left_recipe = model.get_recipe(left)
        right_recipe = model.get_recipe(right)
        if left_recipe is None or right_recipe is None:
            return False

        mode = self._sort_mode or "A-Z"
        descending = mode in ("Z-A", "Newest", "Longest Time", "Most Servings")

        left_value = self._sort_value(left_recipe, mode)
        right_value = self._sort_value(right_recipe, mode)

        if descending:
            return left_value > right_value
        return left_value < right_value

    def _sort_value(self, recipe: object, mode: str):
        """Return the key used for sorting based on mode."""
        name = getattr(recipe, "recipe_name", "") or ""
        created = getattr(recipe, "created_at", None)
        total_time = getattr(recipe, "total_time", None)
        servings = getattr(recipe, "servings", None)

        if isinstance(total_time, str):
            try:
                total_time = int(total_time)
            except ValueError:
                total_time = 0

        if isinstance(servings, str):
            try:
                servings = int(servings)
            except ValueError:
                servings = 0

        if mode in ("Z-A", "A-Z"):
            return name.lower()
        if mode in ("Newest", "Oldest"):
            if isinstance(created, str):
                try:
                    return datetime.fromisoformat(created)
                except ValueError:
                    return datetime.min
            return created or datetime.min
        if mode in ("Shortest Time", "Longest Time"):
            return total_time or 0
        if mode in ("Most Servings", "Fewest Servings"):
            return servings or 0
        return name.lower()
