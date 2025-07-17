
from enum import Enum

from app.config.paths.app_paths import AppPaths

class Color(Enum):
    INDIGO = "#3F51B5"
    BLUE = "#2196F3"
    TEAL = "#009688"
    GREEN = "#4CAF50"
    YELLOW = "#FFEB3B"
    ORANGE = "#FF9800"
    RED = "#F44336"
    PINK = "#E91E63"
    PURPLE = "#9C27B0"
    DEEP_PURPLE = "#673AB7"
    BROWN = "#795548"
    GRAY = "#607D8B"

class Mode(Enum):
    LIGHT = "light"
    DARK = "dark"

class Qss(Enum):
    BASE = AppPaths.BASE_STYLE

    # TODO: add per-widget stylesheets here
    # EXAMPLE: WIDGET_NAME = AppPaths.STYLE / "widget_name.qss"
