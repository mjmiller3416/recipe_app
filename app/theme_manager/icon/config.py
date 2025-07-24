"""app/theme_manager/icon/config.py

Defines AppIcon enum and ICON_SPECS mapping for all application icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum, auto
from typing import NamedTuple

from PySide6.QtCore import QSize

from app.config.paths import AppPaths

# ── AppIcon Enum Definition ──────────────────────────────────────────────────────────────────
class Name(Enum):
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
        return {
            Type.DEFAULT: {
                State.DEFAULT: "icon_on_surface",
                State.HOVER: "icon_on_surface",
                State.CHECKED: "icon_on_surface",
                State.DISABLED: "icon_on_surface",
            },
            Type.TBTN: {
                State.DEFAULT: "icon_primary",
                State.HOVER: "icon_primary",
                State.CHECKED: "icon_primary",
                State.DISABLED: "icon_on_primary",
            },
            Type.NAV: {
                State.DEFAULT: "icon_primary",
                State.HOVER: "icon_primary",
                State.CHECKED: "icon_primary",
                State.DISABLED: "icon_on_surface",
            },
        }[self]

class IconSpec(NamedTuple):
    name: Name
    size: Size
    type: Type

class AppIcon(Enum):
    """Enum for pre-configured application icons."""
    # ── Title Bar Icons ──
    LOGO = IconSpec(Name.LOGO, Size.MEDIUM, Type.TBAR) # og. Qsize(30,30)
    MINIMIZE = IconSpec(Name.MINIMIZE, Size.SMALL, Type.TBAR)
    MAXIMIZE = IconSpec(Name.MAXIMIZE, Size.SMALL, Type.TBAR)
    RESTORE = IconSpec(Name.RESTORE, Size.SMALL, Type.TBAR)
    CLOSE = IconSpec(Name.CLOSE, Size.SMALL, Type.TBAR)
    TOGGLE_SIDEBAR = IconSpec(Name.TOGGLE_SIDEBAR, Size.MEDIUM, Type.TBAR)

    # ── Sidebar Icons ──
    DASHBOARD = IconSpec(Name.DASHBOARD, Size.LARGE, Type.NAV)
    MEAL_PLANNER = IconSpec(Name.MEAL_PLANNER, Size.LARGE, Type.NAV)
    VIEW_RECIPES = IconSpec(Name.VIEW_RECIPES, Size.LARGE, Type.NAV)
    SHOPPING_LIST = IconSpec(Name.SHOPPING_LIST, Size.LARGE, Type.NAV)
    ADD_RECIPES = IconSpec(Name.ADD_RECIPES, Size.LARGE, Type.NAV)
    SETTINGS = IconSpec(Name.SETTINGS, Size.LARGE, Type.NAV)
    EXIT = IconSpec(Name.EXIT, Size.LARGE, Type.NAV)

    # ── Add Recipe Page ──
    ADD_IMAGE = IconSpec(Name.ADD_IMAGE, Size.XXL, Type.NAV)

    # ── Meal Planner Page ──
    MEAL_PLANNER_ADD = IconSpec(Name.MEAL_PLANNER_ADD, Size.SMALL, Type.NAV)

    # ── Search ──
    SEARCH = IconSpec(Name.SEARCH, Size.SMALL, Type.NAV)
    CLEAR = IconSpec(Name.CLEAR, Size.SMALL, Type.NAV)

    # ── Upload Recipe Image ──
    UPLOAD_IMAGE = IconSpec(Name.UPLOAD_IMAGE, Size.SMALL, Type.NAV)

    # ── Ingredient Widget ──
    INGREDIENT_ADD = IconSpec(Name.INGREDIENT_ADD, Size.SMALL, Type.NAV)
    INGREDIENT_SUBTRACT = IconSpec(Name.INGREDIENT_SUBTRACT, Size.SMALL, Type.NAV)

    # ── Custom ComboBox ──
    COMBOBOX_ARROW = IconSpec(Name.COMBOBOX_ARROW, Size.SMALL, Type.NAV)

    # ── Empty State ──
    ADD_MEAL = IconSpec(Name.ADD_MEAL, Size.SMALL, Type.NAV)

    # ── Recipe Card ──
    TOTAL_TIME = IconSpec(Name.TOTAL_TIME, Size.SMALL, Type.NAV)
    SERVINGS = IconSpec(Name.SERVINGS, Size.SMALL, Type.NAV)
    FAVORITE = IconSpec(Name.FAVORITE, Size.SMALL, Type.NAV)
    UNFAVORITE = IconSpec(Name.UNFAVORITE, Size.SMALL, Type.NAV)
    MEAL_TYPE = IconSpec(Name.MEAL_TYPE, Size.SMALL, Type.NAV)
    DIET_PREF = IconSpec(Name.DIET_PREF, Size.SMALL, Type.NAV)

    # ── Recipe Dialog ──
    DIALOG_SERVINGS = IconSpec(Name.DIALOG_SERVINGS, Size.SMALL, Type.NAV)
    DIALOG_TOTAL_TIME = IconSpec(Name.DIALOG_TOTAL_TIME, Size.SMALL, Type.NAV)
    DIALOG_CATEGORY = IconSpec(Name.DIALOG_CATEGORY, Size.SMALL, Type.NAV)

    # ── Message Dialog ──
    MESSAGE_INFO = IconSpec(Name.MESSAGE_INFO, Size.XL, Type.NAV)
    MESSAGE_WARNING = IconSpec(Name.MESSAGE_WARNING, Size.XL, Type.NAV)
    MESSAGE_ERROR = IconSpec(Name.MESSAGE_ERROR, Size.XL, Type.NAV)
    MESSAGE_SUCCESS = IconSpec(Name.MESSAGE_SUCCESS, Size.XL, Type.NAV)

    @property
    def spec(self) -> IconSpec:
        return self.value
