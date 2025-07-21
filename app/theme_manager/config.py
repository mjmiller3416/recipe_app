
from enum import Enum

from app.config.paths.app_paths import AppPaths

class Color(Enum):
    INDIGO      = "#3F51B5"
    BLUE        = "#2196F3"
    TEAL        = "#009688"
    GREEN       = "#63A002"
    YELLOW      = "#FFDE3F"
    ORANGE      = "#FF9800"
    RED         = "#F44336"
    PINK        = "#E91E63"
    PURPLE      = "#9C27B0"
    DEEP_PURPLE = "#673AB7"
    BROWN       = "#795548"
    GRAY        = "#607D8B"

class Mode(Enum):
    LIGHT = "light"
    DARK = "dark"

class Qss(Enum):
    BASE = AppPaths.BASE_STYLE
    TEST = AppPaths.QSS_DIR / "test.qss"
    CARD = AppPaths.QSS_DIR / "card.qss"

    # TODO: add per-widget stylesheets here
    # EXAMPLE: WIDGET_NAME = AppPaths.STYLE / "widget_name.qss"
