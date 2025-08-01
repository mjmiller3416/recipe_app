"""app/theme_manager/icon/config.py

Defines Name enum and icon specifications for all application icons.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from enum import Enum, auto
from typing import NamedTuple

from PySide6.QtCore import QSize

from app.config.paths import AppPaths


class Path(Enum):
    """Enum for application icons."""
    ADD             = "add"
    ADD_RECIPES     = "add_recipes"
    BATTERY         = "battery"
    CATEGORY        = "category"
    CROSS           = "cross"
    DASHBOARD       = "dashboard"
    DIET_PREF       = "diet_pref"
    ANGLE_DOWN      = "angle_down"
    EDIT            = "edit"
    ERROR           = "error"
    EXIT            = "exit"
    HEART           = "heart"
    HEART_FILLED    = "heart_filled"
    INFO            = "info"
    LIGHTBULB       = "lightbulb"
    LOGO            = "logo"
    MAXIMIZE        = "maximize"
    MEAL_PLANNER    = "meal_planner"
    MEAL_TYPE       = "meal_type"
    MENU            = "menu"
    MINIMIZE        = "minimize"
    RESTORE         = "restore"
    REFRESH         = "refresh"
    SAVE            = "save"
    SEARCH          = "search"
    SERVINGS        = "servings"
    SETTINGS        = "settings"
    SHOPPING_LIST   = "shopping_list"
    SIGNAL          = "signal"
    SUCCESS         = "success"
    SUBTRACT        = "subtract"
    TOTAL_TIME      = "total_time"
    USER            = "user"
    VIEW_RECIPES    = "view_recipes"
    WARNING         = "warning"
    WIFI            = "wifi"

    @property
    def path(self):
        return AppPaths.ICONS_DIR / f"{self.value}.svg"

class Size(Enum):
    """Enum for common icon sizes used in the application."""
    SMALL  = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE  = QSize(36, 36)
    XL     = QSize(50, 50)
    XXL    = QSize(100, 100)

    @classmethod
    def custom(cls, width: int, height: int) -> QSize:
        return QSize(width, height)

class State(Enum):
    DEFAULT  = auto()
    HOVER    = auto()
    CHECKED  = auto()
    DISABLED = auto()

    def __str__(self):
        return self.name  # allows dict.get(str(state), ...) if needed

class Type(Enum):
    """Enum for button types that define icon colors for different states."""
    DEFAULT   = "default"
    PRIMARY   = "primary"
    SECONDARY = "secondary"
    TITLEBAR  = "titlebar"

    @property
    def state_map(self) -> dict[State, str]:
        """Returns the color palette role for each button state."""
        if self == Type.DEFAULT:
            return {
                State.DEFAULT: "surface_variant",
                State.HOVER: "on_surface_variant",
                State.CHECKED: "surface_bright",
                State.DISABLED: "surface_dim",
            }
        elif self == Type.PRIMARY:
            return {
                State.DEFAULT: "primary",
                State.HOVER: "on_primary",
                State.CHECKED: "primary_container",
                State.DISABLED: "on_primary_container",
            }
        elif self == Type.SECONDARY:
            return {
                State.DEFAULT: "primary",
                State.HOVER: "tertiary",
                State.CHECKED: "tertiary",
                State.DISABLED: "on_secondary_container",
            }
        elif self == Type.TITLEBAR:
            return {
                State.DEFAULT: "secondary",
                State.HOVER: "secondary",
                State.CHECKED: "primary",
                State.DISABLED: "secondary",
            }

class IconSpec(NamedTuple):
    name: Path
    size: Size

class Name(Enum):
    """Enum for pre-configured application icons."""

    # ── Small Icons ─────────────────────────────
    ADD             = IconSpec(Path.ADD, Size.SMALL)
    BATTERY         = IconSpec(Path.BATTERY, Size.SMALL)
    CATEGORY        = IconSpec(Path.CATEGORY, Size.SMALL)
    CROSS           = IconSpec(Path.CROSS, Size.SMALL)
    DIET_PREF       = IconSpec(Path.DIET_PREF, Size.SMALL)
    ANGLE_DOWN      = IconSpec(Path.ANGLE_DOWN, Size.SMALL)
    EDIT            = IconSpec(Path.EDIT, Size.SMALL)
    HEART           = IconSpec(Path.HEART, Size.SMALL)
    HEART_FILLED    = IconSpec(Path.HEART_FILLED, Size.SMALL)
    LIGHTBULB       = IconSpec(Path.LIGHTBULB, Size.SMALL)
    MAXIMIZE        = IconSpec(Path.MAXIMIZE, Size.SMALL)
    MEAL_TYPE       = IconSpec(Path.MEAL_TYPE, Size.SMALL)
    MINIMIZE        = IconSpec(Path.MINIMIZE, Size.SMALL)
    REFRESH         = IconSpec(Path.REFRESH, Size.SMALL)
    RESTORE         = IconSpec(Path.RESTORE, Size.SMALL)
    SAVE            = IconSpec(Path.SAVE, Size.SMALL)
    SEARCH          = IconSpec(Path.SEARCH, Size.SMALL)
    SERVINGS        = IconSpec(Path.SERVINGS, Size.SMALL)
    SIGNAL          = IconSpec(Path.SIGNAL, Size.SMALL)
    SUBTRACT        = IconSpec(Path.SUBTRACT, Size.SMALL)
    TOTAL_TIME      = IconSpec(Path.TOTAL_TIME, Size.SMALL)
    USER            = IconSpec(Path.USER, Size.SMALL)
    WIFI            = IconSpec(Path.WIFI, Size.SMALL)

    # ── Medium Icons ────────────────────────────
    LOGO            = IconSpec(Path.LOGO, Size.MEDIUM)
    MENU            = IconSpec(Path.MENU, Size.MEDIUM)

    # ── Large Icons ─────────────────────────────
    ADD_RECIPES     = IconSpec(Path.ADD_RECIPES, Size.LARGE)
    DASHBOARD       = IconSpec(Path.DASHBOARD, Size.LARGE)
    MEAL_PLANNER    = IconSpec(Path.MEAL_PLANNER, Size.LARGE)
    VIEW_RECIPES    = IconSpec(Path.VIEW_RECIPES, Size.LARGE)
    SHOPPING_LIST   = IconSpec(Path.SHOPPING_LIST, Size.LARGE)
    SETTINGS        = IconSpec(Path.SETTINGS, Size.LARGE)
    EXIT            = IconSpec(Path.EXIT, Size.LARGE)


    # ── XL Icons ────────────────────────────────
    INFO            = IconSpec(Path.INFO, Size.XL)
    WARNING         = IconSpec(Path.WARNING, Size.XL)
    ERROR           = IconSpec(Path.ERROR, Size.XL)
    SUCCESS         = IconSpec(Path.SUCCESS, Size.XL)

    @property
    def spec(self) -> IconSpec:
        return self.value
