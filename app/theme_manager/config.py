
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
    
    # Widget-specific stylesheets
    COMBOBOX = AppPaths.QSS_DIR / "combobox.qss"
    RECIPE_CARD = AppPaths.QSS_DIR / "components" / "recipe_card.qss"
    SEARCH_BAR = AppPaths.QSS_DIR / "components" / "search_bar.qss"
    DIALOG_WINDOW = AppPaths.QSS_DIR / "components" / "dialog_window.qss"
    UPLOAD_IMAGE = AppPaths.QSS_DIR / "components" / "upload_image.qss"
    INGREDIENT_WIDGET = AppPaths.QSS_DIR / "components" / "ingredient_widget.qss"
    WIDGET_FRAME = AppPaths.QSS_DIR / "components" / "widget_frame.qss"
    EMPTY_STATE_FRAME = AppPaths.QSS_DIR / "components" / "empty_state_frame.qss"
    RECIPE_DIALOG = AppPaths.QSS_DIR / "components" / "recipe_dialog.qss"
