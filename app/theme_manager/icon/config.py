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
    """Enum for icon color variants."""
    DEFAULT = auto() # static color
    NAV = auto()
    TBAR = auto()
    TBTN = auto()

    @property
    def state_map(self) -> dict[State, str]:
        if self == Type.DEFAULT:
            return {
                State.DEFAULT: "icon_on_surface",
                State.HOVER: "icon_on_surface",
                State.CHECKED: "icon_on_surface",
                State.DISABLED: "icon_on_surface",
            }
        elif self == Type.TBTN:
            return {
                State.DEFAULT: "icon_primary",
                State.HOVER: "icon_primary",
                State.CHECKED: "icon_primary",
                State.DISABLED: "icon_on_primary",
            }
        elif self == Type.NAV:
            return {
                State.DEFAULT: "icon_primary",
                State.HOVER: "icon_primary",
                State.CHECKED: "icon_primary",
                State.DISABLED: "icon_on_surface",
            }
        elif self == Type.TBAR:
            return {
                State.DEFAULT: "icon_on_surface",
                State.HOVER: "icon_on_surface",
                State.CHECKED: "icon_on_surface",
                State.DISABLED: "icon_on_surface",
            }
        else:
            return {
                State.DEFAULT: "icon_on_surface",
                State.HOVER: "icon_on_surface",
                State.CHECKED: "icon_on_surface",
                State.DISABLED: "icon_on_surface",
            }

class IconSpec(NamedTuple):
    name: Path
    size: Size
    type: Type

class Name(Enum):
    """Enum for pre-configured application icons."""
    # ── Test Icons ──
    WIFI = IconSpec(Path.WIFI, Size.SMALL, Type.DEFAULT)
    BATTERY = IconSpec(Path.BATTERY, Size.SMALL, Type.DEFAULT)
    SIGNAL = IconSpec(Path.SIGNAL, Size.SMALL, Type.DEFAULT)
    USER = IconSpec(Path.USER, Size.SMALL, Type.DEFAULT)
    LIGHTBULB = IconSpec(Path.LIGHTBULB, Size.SMALL, Type.DEFAULT)

    # ── Title Bar Icons ──
    LOGO = IconSpec(Path.LOGO, Size.MEDIUM, Type.TBAR) # og. Qsize(30,30)
    MINIMIZE = IconSpec(Path.MINIMIZE, Size.SMALL, Type.TBAR)
    MAXIMIZE = IconSpec(Path.MAXIMIZE, Size.SMALL, Type.TBAR)
    RESTORE = IconSpec(Path.RESTORE, Size.SMALL, Type.TBAR)
    CLOSE = IconSpec(Path.CLOSE, Size.SMALL, Type.TBAR)
    TOGGLE_SIDEBAR = IconSpec(Path.TOGGLE_SIDEBAR, Size.MEDIUM, Type.TBAR)

    # ── Sidebar Icons ──
    DASHBOARD = IconSpec(Path.DASHBOARD, Size.LARGE, Type.NAV)
    MEAL_PLANNER = IconSpec(Path.MEAL_PLANNER, Size.LARGE, Type.NAV)
    VIEW_RECIPES = IconSpec(Path.VIEW_RECIPES, Size.LARGE, Type.NAV)
    SHOPPING_LIST = IconSpec(Path.SHOPPING_LIST, Size.LARGE, Type.NAV)
    ADD_RECIPES = IconSpec(Path.ADD_RECIPES, Size.LARGE, Type.NAV)
    SETTINGS = IconSpec(Path.SETTINGS, Size.LARGE, Type.NAV)
    EXIT = IconSpec(Path.EXIT, Size.LARGE, Type.NAV)

    # ── Add Recipe Page ──
    ADD_IMAGE = IconSpec(Path.ADD_IMAGE, Size.XXL, Type.NAV)

    # ── Meal Planner Page ──
    MEAL_PLANNER_ADD = IconSpec(Path.MEAL_PLANNER_ADD, Size.SMALL, Type.NAV)

    # ── Search ──
    SEARCH = IconSpec(Path.SEARCH, Size.SMALL, Type.NAV)
    CLEAR = IconSpec(Path.CLEAR, Size.SMALL, Type.NAV)

    # ── Upload Recipe Image ──
    UPLOAD_IMAGE = IconSpec(Path.UPLOAD_IMAGE, Size.SMALL, Type.NAV)

    # ── Ingredient Widget ──
    INGREDIENT_ADD = IconSpec(Path.INGREDIENT_ADD, Size.SMALL, Type.NAV)
    INGREDIENT_SUBTRACT = IconSpec(Path.INGREDIENT_SUBTRACT, Size.SMALL, Type.NAV)

    # ── Custom ComboBox ──
    COMBOBOX_ARROW = IconSpec(Path.COMBOBOX_ARROW, Size.SMALL, Type.NAV)

    # ── Empty State ──
    ADD_MEAL = IconSpec(Path.ADD_MEAL, Size.SMALL, Type.NAV)

    # ── Recipe Card ──
    TOTAL_TIME = IconSpec(Path.TOTAL_TIME, Size.SMALL, Type.NAV)
    SERVINGS = IconSpec(Path.SERVINGS, Size.SMALL, Type.NAV)
    FAVORITE = IconSpec(Path.FAVORITE, Size.SMALL, Type.NAV)
    UNFAVORITE = IconSpec(Path.UNFAVORITE, Size.SMALL, Type.NAV)
    MEAL_TYPE = IconSpec(Path.MEAL_TYPE, Size.SMALL, Type.NAV)
    DIET_PREF = IconSpec(Path.DIET_PREF, Size.SMALL, Type.NAV)

    # ── Recipe Dialog ──
    DIALOG_SERVINGS = IconSpec(Path.DIALOG_SERVINGS, Size.SMALL, Type.NAV)
    DIALOG_TOTAL_TIME = IconSpec(Path.DIALOG_TOTAL_TIME, Size.SMALL, Type.NAV)
    DIALOG_CATEGORY = IconSpec(Path.DIALOG_CATEGORY, Size.SMALL, Type.NAV)

    # ── Message Dialog ──
    MESSAGE_INFO = IconSpec(Path.MESSAGE_INFO, Size.XL, Type.NAV)
    MESSAGE_WARNING = IconSpec(Path.MESSAGE_WARNING, Size.XL, Type.NAV)
    MESSAGE_ERROR = IconSpec(Path.MESSAGE_ERROR, Size.XL, Type.NAV)
    MESSAGE_SUCCESS = IconSpec(Path.MESSAGE_SUCCESS, Size.XL, Type.NAV)

    @property
    def spec(self) -> IconSpec:
        return self.value
