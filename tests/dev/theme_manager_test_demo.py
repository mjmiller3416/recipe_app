import sys
from collections import namedtuple
from enum import Enum, auto

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QIcon, QPainter,
                           QPainterPath, QPixmap, QPalette)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QVBoxLayout, QWidget, QGraphicsDropShadowEffect,
    QGraphicsBlurEffect, QGraphicsOpacityEffect
)

from app.config import ERROR_COLOR
from app.theme_manager.icon import Icon, Type, Name
from app.theme_manager.theme import Color, Mode, Theme
from app.ui.components.widgets import Button, ToolButton

# ── Shadow Effect Enum ───────────────────────────────────────────────────────────────────────
ShadowStyle = namedtuple("ShadowStyle", "color blur_radius offset_x offset_y")

class Shadow(Enum):
    """
    Predefined shadow styles for elevation effects.

    - ELEVATION_0: No shadow, flat appearance.
    - ELEVATION_1: Subtle shadow for resting cards.
    - ELEVATION_3: More pronounced shadow for hover/active states.
    - ELEVATION_6: Stronger shadow for floating cards.
    - ELEVATION_12: Heaviest shadow for dialogs/modals.
    """
    ELEVATION_0 = ShadowStyle(QColor(0, 0, 0, 0), 0.0, 0.0, 0.0)
    ELEVATION_1 = ShadowStyle(QColor(0, 0, 0, 40), 8.0, 0.0, 2.0)
    ELEVATION_3 = ShadowStyle(QColor(0, 0, 0, 60), 12.0, 0.0, 4.0)
    ELEVATION_6 = ShadowStyle(QColor(0, 0, 0, 80), 16.0, 0.0, 6.0)
    ELEVATION_12 = ShadowStyle(QColor(0, 0, 0, 100), 24.0, 0.0, 8.0)


# ── Glow Effect Enum ─────────────────────────────────────────────────────────────────────────
GlowStyle = namedtuple("GlowStyle", "color blur_radius")

class Glow(Enum):
    CYAN = GlowStyle(QColor(0, 255, 255, 200), 60.0)
    PINK = GlowStyle(QColor(255, 0, 255, 220), 50.0)
    GOLD = GlowStyle(QColor(255, 215, 0, 180), 40.0)
    ERROR = GlowStyle(QColor(255, 0, 0, 150), 30.0)
    PRIMARY = GlowStyle(QColor(100, 149, 237, 180), 45.0)  # Cornflower Blue-ish


# ── Widget Effects ───────────────────────────────────────────────────────────────────────────
class Effects:
    """
    A collection of QGraphicsEffect class methods to apply visual effects to QWidgets.
    """

    @classmethod
    def apply_shadow(
        cls,
        widget: QWidget,
        shadow: Shadow = Shadow.ELEVATION_1,
    ) -> None:
        """
        Applies a QGraphicsDropShadowEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color of the shadow. Default is semi-transparent black.
            blur_radius (float): The blur radius of the shadow.
            offset_x (float): The horizontal offset of the shadow.
            offset_y (float): The vertical offset of the shadow.
        """
        _color = shadow.value.color
        _blur_radius = shadow.value.blur_radius
        _offset_x = shadow.value.offset_x
        _offset_y = shadow.value.offset_y

        shadow_effect = QGraphicsDropShadowEffect(widget)
        shadow_effect.setColor(_color)
        shadow_effect.setBlurRadius(_blur_radius)
        shadow_effect.setOffset(_offset_x, _offset_y)
        widget.setGraphicsEffect(shadow_effect)
        print(f"Applied Drop Shadow to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def apply_blur(cls, widget: QWidget, blur_radius: float = 10.0):
        """
        Applies a QGraphicsBlurEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            blur_radius (float): The blur radius of the effect.
        """
        blur_effect = QGraphicsBlurEffect(widget)
        blur_effect.setBlurRadius(blur_radius)
        widget.setGraphicsEffect(blur_effect)
        widget.update()
        print(f"Applied Blur to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def apply_glow(
        cls,
        widget: QWidget,
        glow: Glow = Glow.PRIMARY,
    ) -> None:
        """
        Applies a "glow" effect to the given widget using QGraphicsDropShadowEffect.

        A glow is a shadow with zero offset, making it radiate from the center.

        Args:
            widget (QWidget): The widget to apply the effect to.
            color (QColor): The color of the glow.
            blur_radius (float): The blur radius of the glow.
        """
        _color = glow.value.color
        _blur_radius = glow.value.blur_radius

        glow_effect = QGraphicsDropShadowEffect(widget)
        glow_effect.setColor(_color)
        glow_effect.setBlurRadius(_blur_radius)

        # set offset to zero to create a centered glow
        glow_effect.setOffset(0, 0)

        widget.setGraphicsEffect(glow_effect)

    @classmethod
    def apply_opacity(cls, widget: QWidget, opacity: float = 0.5):
        """
        Applies a QGraphicsOpacityEffect to the given widget.

        Args:
            widget (QWidget): The widget to apply the effect to.
            opacity (float): Opacity level
                (0.0 for fully transparent, 1.0 for fully opaque).
        """
        opacity_effect = QGraphicsOpacityEffect(widget)
        opacity_effect.setOpacity(opacity)
        widget.setGraphicsEffect(opacity_effect)
        widget.update()
        print(f"Applied Opacity to "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )

    @classmethod
    def clear_effect(cls, widget: QWidget):
        """
        Clears any QGraphicsEffect applied to the given widget.

        Args:
            widget (QWidget): The widget to clear the effect from.
        """
        widget.setGraphicsEffect(None)
        widget.update()
        print(f"Cleared effect from "
              f"{widget.objectName() if widget.objectName() else widget.__class__.__name__}"
        )
# Custom widget for the plant illustrations to get rounded corners
class ImageLabel(QLabel):
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(pixmap_path))
        self.setScaledContents(False) # Let's handle scaling manually if needed
        self.setAlignment(Qt.AlignCenter)

# A simple rounded color block to act as a placeholder for plant images
class PlantImagePlaceholder(QWidget):
    def __init__(self, color, radius, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.radius = radius
        self.setMinimumSize(100, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        painter.fillPath(path, self.color)

class PlantAppUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plant Care App")
        self.setGeometry(100, 100, 400, 850) # Set a mobile-like dimension

        # --- Load Custom Font ---
        # In a real app, ensure the font file is in the same directory or provide a full path
        # For this example, we'll fall back to a common font if the custom one isn't found.
        font_id = QFontDatabase.addApplicationFont("PlayfairDisplay-Regular.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.title_font = QFont(font_family, 36, QFont.Bold)
        else:
            print("Warning: Playfair Display font not found. Using default.")
            self.title_font = QFont("Serif", 36, QFont.Bold)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Create Screens ---
        self.main_screen = self._create_main_screen()
        self.detail_screen = self._create_detail_screen() # Placeholder for the second screen

        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.detail_screen)

    def _create_main_screen(self):
        """Creates the main 'Today' screen widget."""
        main_widget = QWidget()
        main_widget.setObjectName("MainScreen")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Top Status Bar ---
        status_bar_layout = QHBoxLayout()
        time_label = QLabel("10:40")
        time_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        status_bar_layout.addWidget(time_label)
        status_bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # In a real app, these would be icons
        status_bar_layout.addWidget(Icon(Name.WIFI))
        status_bar_layout.addWidget(Icon(Name.SIGNAL))
        status_bar_layout.addWidget(Icon(Name.BATTERY))
        main_layout.addLayout(status_bar_layout)

        # --- Header: Today + Profile Icon ---
        header_layout = QHBoxLayout()
        today_label = QLabel("Today")
        today_label.setObjectName("TitleLabel")
        today_label.setFont(self.title_font)
        header_layout.addWidget(today_label)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # Placeholder for profile icon
        profile_icon = ToolButton(Type.PRIMARY)
        profile_icon.setIconFromName(Name.USER)

        profile_icon.setFixedSize(40, 40)
        header_layout.addWidget(profile_icon)
        main_layout.addLayout(header_layout)

        # --- Theme Controls ---
        theme_controls_layout = QHBoxLayout()

        # Color selector
        color_label = QLabel("Color:")
        self.color_combo = QComboBox()
        for color in Color:
            self.color_combo.addItem(color.name.title(), color)
        self.color_combo.setCurrentText("Green")

        # Mode toggle
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        for mode in Mode:
            self.mode_combo.addItem(mode.value.title(), mode)
        self.mode_combo.setCurrentText("Dark")

        # Connect for immediate updates
        self.color_combo.currentIndexChanged.connect(self._apply_theme)
        self.mode_combo.currentIndexChanged.connect(self._apply_theme)

        theme_controls_layout.addWidget(color_label)
        theme_controls_layout.addWidget(self.color_combo)
        theme_controls_layout.addWidget(mode_label)
        theme_controls_layout.addWidget(self.mode_combo)
        theme_controls_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        main_layout.addLayout(theme_controls_layout)

        # --- Info Box ---
        info_frame = QFrame()
        info_frame.setContentsMargins(4, 4, 4, 4)
        info_frame.setObjectName("InfoFrame")
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QHBoxLayout(info_frame)

        # Placeholder for lightbulb icon
        bulb_icon = Icon(Name.LIGHTBULB)
        info_layout.addWidget(bulb_icon)
        info_text = QLabel("During the winter your plants slow down and need less water.")
        info_text.setWordWrap(False)
        info_text.setStyleSheet("background-color: transparent; color: #f0eade;")
        info_layout.addWidget(info_text)
        main_layout.addWidget(info_frame)

        # --- Plant Cards ---
        color_map = Theme.get_current_color_map()

        living_card = self._create_plant_card("Living Room", ["Water hoya australis", "Feed monstera siltepecana"], color_map.get("primary", ERROR_COLOR))
        Effects.apply_shadow(living_card, Shadow.ELEVATION_6)
        main_layout.addWidget(living_card)

        kitchen_card = self._create_plant_card("Kitchen", ["Water pilea peperomioides", "Water hoya australis"], color_map.get("secondary", ERROR_COLOR))
        Effects.apply_shadow(kitchen_card, Shadow.ELEVATION_6)
        main_layout.addWidget(kitchen_card)

        bedroom_card = self._create_plant_card("Bedroom", ["Feed monstera siltepecana", "Water philodendron brandi"], color_map.get("tertiary", ERROR_COLOR))
        Effects.apply_shadow(bedroom_card, Shadow.ELEVATION_6)
        main_layout.addWidget(bedroom_card)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        #--- Bottom Navigation Bar ---
        button = Button("Add Plant")
        button.setIconFromName(Name.ADD)
        main_layout.addWidget(button)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(40)

        for icon_name in [Name.DASHBOARD, Name.MEAL_PLANNER, Name.VIEW_RECIPES, Name.SHOPPING_LIST, Name.SETTINGS]:
            btn = ToolButton(Type.TOOL)
            btn.setIconFromName(icon_name)
            btn.setButtonSize(40, 40)
            nav_layout.addWidget(btn)
        main_layout.addLayout(nav_layout)

        return main_widget

    def _create_plant_card(self, room_name, tasks, image_color):
        """Helper function to create a plant card widget."""
        card_frame = QFrame()
        card_frame.setContentsMargins(10, 10, 10, 10)
        card_frame.setObjectName("CardFrame")
        card_frame.setFrameShape(QFrame.StyledPanel)
        card_layout = QHBoxLayout(card_frame)
        card_layout.setSpacing(15)

        # Left side: Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(15)
        room_label = QLabel(room_name)
        room_label.setObjectName("HeaderLabel")
        text_layout.addWidget(room_label)

        for task_text in tasks:
            task_layout = QHBoxLayout()
            checkbox = QCheckBox()
            checkbox.setChecked(True) # Match screenshot
            task_label = QLabel(task_text)
            task_layout.addWidget(checkbox)
            task_layout.addWidget(task_label)
            task_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            text_layout.addLayout(task_layout)

        text_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        card_layout.addLayout(text_layout, 2) # Give text more stretch factor

        # Right side: Image placeholder
        image_placeholder = PlantImagePlaceholder(image_color, 20)
        card_layout.addWidget(image_placeholder, 1) # Give image less stretch factor

        return card_frame

    def _create_detail_screen(self):
        """Creates the detail screen (currently a placeholder)."""
        detail_widget = QWidget()
        detail_widget.setObjectName("DetailScreen")
        layout = QVBoxLayout(detail_widget)
        label = QLabel("Detail Screen (Placeholder)")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 24))
        layout.addWidget(label)
        return detail_widget

    def _apply_theme(self):
        """Apply the selected theme color and mode dynamically."""
        selected_color = self.color_combo.currentData()
        selected_mode = self.mode_combo.currentData()
        if selected_color and selected_mode:
            Theme.setTheme(selected_color, selected_mode)
            # The theme system will automatically update stylesheets and emit signals
            # Icons and other themed elements will refresh automatically


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Note: For the custom font to work, you need a "PlayfairDisplay-Regular.ttf" file
    # in the same directory as the script. You can download it from Google Fonts.
    Theme.setTheme(Color.RED, Mode.DARK)
    window = PlantAppUI()
    window.show()
    sys.exit(app.exec())
