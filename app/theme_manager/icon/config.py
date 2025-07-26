"""app/theme_manager/icon/config.py

Defines AppIcon enum and ICON_SPECS mapping for all application icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum, auto
from typing import NamedTuple

from PySide6.QtCore import QSize

from app.config.paths import AppPaths


# ── AppIcon Enum Definition ──────────────────────────────────────────────────────────────────
class Path(Enum):
    """Enum for application icons."""
    WIFI = "wifi"
    BATTERY = "battery"
    SIGNAL = "signal"
    USER = "user"
    LIGHTBULB = "lightbulb"

    # ── Title Bar Icons ──
    LOGO = "logo"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    CLOSE = "close"
    TOGGLE_SIDEBAR = "toggle_sidebar"

    # ── Sidebar Icons ──
    DASHBOARD = "dashboard"
    MEAL_PLANNER = "meal_planner"
    VIEW_RECIPES = "view_recipes"
    SHOPPING_LIST = "shopping_list"
    ADD_RECIPES = "add_recipes"
    SETTINGS = "settings"
    EXIT = "exit"

    EDIT = "edit"

    # ── Add Recipe Page ──
    ADD_IMAGE = "add_image"

    # ── Meal Planner Page ──
    MEAL_PLANNER_ADD = "meal_planner_add"

    # ── Search ──
    SEARCH = "search"
    CLEAR = "clear"

    # ── Upload Recipe Image ──
    UPLOAD_IMAGE = "upload_image"

    # ── Ingredient Widget ──
    INGREDIENT_ADD = "ingredient_add"
    INGREDIENT_SUBTRACT = "ingredient_subtract"

    # ── Custom ComboBox ──
    COMBOBOX_ARROW = "combobox_arrow"

    # ── Empty State ──
    ADD_MEAL = "add_meal"

    # ── Recipe Card ──
    TOTAL_TIME = "total_time"
    SERVINGS = "servings"
    FAVORITE = "favorite"
    UNFAVORITE = "unfavorite"
    MEAL_TYPE = "meal_type"
    DIET_PREF = "diet_pref"

    # ── Recipe Dialog ──
    DIALOG_SERVINGS = "dialog_servings"
    DIALOG_TOTAL_TIME = "dialog_total_time"
    DIALOG_CATEGORY = "dialog_category"

    # ── Message Dialog ──
    MESSAGE_INFO = "message_info"
    MESSAGE_WARNING = "message_warning"
    MESSAGE_ERROR = "message_error"
    MESSAGE_SUCCESS = "message_success"

    @property
    def path(self):
        return AppPaths.ICONS_DIR / f"{self.value}.svg"

class Size(Enum):
    """Enum for common icon sizes used in the application."""
    SMALL = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE = QSize(36, 36)
    XL = QSize(50, 50)
    XXL = QSize(100, 100)

    @classmethod
    def custom(cls, width: int, height: int) -> QSize:
        return QSize(width, height)

class State(Enum):
    DEFAULT = auto()
    HOVER = auto()
    CHECKED = auto()
    DISABLED = auto()

    def __str__(self):
        return self.name  # allows dict.get(str(state), ...) if needed

class Type(Enum):
    """Enum for button types that define icon colors for different states."""
    DEFAULT   = "default"
    PRIMARY   = "primary"
    SECONDARY = "secondary"
    TOOL      = "tool"

    @property
    def state_map(self) -> dict[State, str]:
        """Returns the color palette role for each button state."""
        if self == Type.DEFAULT:
            return {
                State.DEFAULT: "icon_surface_variant",
                State.HOVER: "icon_on_surface_variant",
                State.CHECKED: "icon_surface_bright",
                State.DISABLED: "icon_surface_dim",
            }
        elif self == Type.PRIMARY:
            return {
                State.DEFAULT: "icon_primary",
                State.HOVER: "icon_on_primary",
                State.CHECKED: "icon_primary_container",
                State.DISABLED: "icon_on_primary_container",
            }
        elif self == Type.SECONDARY:
            return {
                State.DEFAULT: "icon_secondary",
                State.HOVER: "icon_on_secondary",
                State.CHECKED: "icon_secondary_container",
                State.DISABLED: "icon_on_secondary_container",
            }
        elif self == Type.TOOL:
            return {
                State.DEFAULT: "icon_tertiary",
                State.HOVER: "icon_on_tertiary",
                State.CHECKED: "icon_tertiary_container",
                State.DISABLED: "icon_on_tertiary_container",
            }

class IconSpec(NamedTuple):
    name: Path
    size: Size

class Name(Enum):
    """Enum for pre-configured application icons."""
    # ── Test Icons ──
    WIFI = IconSpec(Path.WIFI, Size.SMALL)
    BATTERY = IconSpec(Path.BATTERY, Size.SMALL)
    SIGNAL = IconSpec(Path.SIGNAL, Size.SMALL)
    USER = IconSpec(Path.USER, Size.SMALL)
    LIGHTBULB = IconSpec(Path.LIGHTBULB, Size.SMALL)

    # ── Title Bar Icons ──
    LOGO = IconSpec(Path.LOGO, Size.MEDIUM) # og. Qsize(30,30)
    MINIMIZE = IconSpec(Path.MINIMIZE, Size.SMALL)
    MAXIMIZE = IconSpec(Path.MAXIMIZE, Size.SMALL)
    RESTORE = IconSpec(Path.RESTORE, Size.SMALL)
    CLOSE = IconSpec(Path.CLOSE, Size.SMALL)
    TOGGLE_SIDEBAR = IconSpec(Path.TOGGLE_SIDEBAR, Size.MEDIUM)

    # ── Sidebar Icons ──
    DASHBOARD = IconSpec(Path.DASHBOARD, Size.LARGE)
    MEAL_PLANNER = IconSpec(Path.MEAL_PLANNER, Size.LARGE)
    VIEW_RECIPES = IconSpec(Path.VIEW_RECIPES, Size.LARGE)
    SHOPPING_LIST = IconSpec(Path.SHOPPING_LIST, Size.LARGE)
    ADD_RECIPES = IconSpec(Path.ADD_RECIPES, Size.LARGE)
    SETTINGS = IconSpec(Path.SETTINGS, Size.LARGE)
    EXIT = IconSpec(Path.EXIT, Size.LARGE)
    EDIT = IconSpec(Path.EDIT, Size.SMALL)

    # ── Add Recipe Page ──
    ADD_IMAGE = IconSpec(Path.ADD_IMAGE, Size.XXL)

    # ── Meal Planner Page ──
    MEAL_PLANNER_ADD = IconSpec(Path.MEAL_PLANNER_ADD, Size.SMALL)

    # ── Search ──
    SEARCH = IconSpec(Path.SEARCH, Size.SMALL)
    CLEAR = IconSpec(Path.CLEAR, Size.SMALL)

    # ── Upload Recipe Image ──
    UPLOAD_IMAGE = IconSpec(Path.UPLOAD_IMAGE, Size.SMALL)

    # ── Ingredient Widget ──
    INGREDIENT_ADD = IconSpec(Path.INGREDIENT_ADD, Size.SMALL)
    INGREDIENT_SUBTRACT = IconSpec(Path.INGREDIENT_SUBTRACT, Size.SMALL)

    # ── Custom ComboBox ──
    COMBOBOX_ARROW = IconSpec(Path.COMBOBOX_ARROW, Size.SMALL)

    # ── Empty State ──
    ADD_MEAL = IconSpec(Path.ADD_MEAL, Size.SMALL)

    # ── Recipe Card ──
    TOTAL_TIME = IconSpec(Path.TOTAL_TIME, Size.SMALL)
    SERVINGS = IconSpec(Path.SERVINGS, Size.SMALL)
    FAVORITE = IconSpec(Path.FAVORITE, Size.SMALL)
    UNFAVORITE = IconSpec(Path.UNFAVORITE, Size.SMALL)
    MEAL_TYPE = IconSpec(Path.MEAL_TYPE, Size.SMALL)
    DIET_PREF = IconSpec(Path.DIET_PREF, Size.SMALL)

    # ── Recipe Dialog ──
    DIALOG_SERVINGS = IconSpec(Path.DIALOG_SERVINGS, Size.SMALL)
    DIALOG_TOTAL_TIME = IconSpec(Path.DIALOG_TOTAL_TIME, Size.SMALL)
    DIALOG_CATEGORY = IconSpec(Path.DIALOG_CATEGORY, Size.SMALL)

    # ── Message Dialog ──
    MESSAGE_INFO = IconSpec(Path.MESSAGE_INFO, Size.XL)
    MESSAGE_WARNING = IconSpec(Path.MESSAGE_WARNING, Size.XL)
    MESSAGE_ERROR = IconSpec(Path.MESSAGE_ERROR, Size.XL)
    MESSAGE_SUCCESS = IconSpec(Path.MESSAGE_SUCCESS, Size.XL)

    @property
    def spec(self) -> IconSpec:
        return self.value
