import sys
from enum import Enum

from PySide6.QtCore import (
    QEasingCurve, QPoint, QPropertyAnimation, QRect, QSettings, QSize, Qt, QTimer, QUrl
)
from PySide6.QtGui import (
    QColor, QDesktopServices, QFont, QIcon, QPainter, QPen, QPixmap, QStandardItem,
    QStandardItemModel
)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem, QSpinBox, QStackedWidget,
    QTabWidget, QTextEdit, QTreeView, QVBoxLayout, QWidget
)

from app.style.icon import Icon, Type, Name
from app.style.theme_controller import Theme, Color, Mode
from app.ui.components.widgets import Button, ToolButton

class Name(Enum):
    """Mock Icon Names Enum."""
    DASHBOARD = "dashboard"
    DATA = "data"
    SETTINGS = "settings"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    EDIT = "edit"
    SAVE = "save"
    CLOSE = "close"
    WIFI = "wifi"
    BATTERY = "battery"
    HELP = "help"
    PYTHON = "python"


class Color(Enum):
    """Mock Theme Colors Enum."""
    BLUE = ("#3498db", "#2980b9")
    GREEN = ("#2ecc71", "#27ae60")
    PURPLE = ("#9b59b6", "#8e44ad")
    RED = ("#e74c3c", "#c0392b")
    ORANGE = ("#e67e22", "#d35400")

    def __init__(self, primary, secondary):
        self.primary = QColor(primary)
        self.secondary = QColor(secondary)


class Mode(Enum):
    """Mock Theme Modes Enum."""
    LIGHT = ("#f0f0f0", "#ffffff", "#333333", "#e0e0e0", "#c0c0c0")
    DARK = ("#2c3e50", "#34495e", "#ecf0f1", "#4a627a", "#5a738b")

    def __init__(self, bg, bg_2, text, border, disabled):
        self.bg = QColor(bg)
        self.bg_2 = QColor(bg_2)
        self.text = QColor(text)
        self.border = QColor(border)
        self.disabled = QColor(disabled)


class Theme:
    """
    Mock ThemeManager.
    Manages the application's color scheme and mode.
    """
    _instance = None
    themeChanged = []  # A simple list to act as a signal

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Theme, cls).__new__(cls)
            cls._instance.current_color = Color.BLUE
            cls._instance.current_mode = Mode.DARK
        return cls._instance

    @classmethod
    def color(cls):
        return cls.instance().current_color.primary

    @classmethod
    def color_secondary(cls):
        return cls.instance().current_color.secondary

    @classmethod
    def mode(cls):
        return cls.instance().current_mode

    @classmethod
    def instance(cls):
        return cls.__new__(cls)

    @classmethod
    def setTheme(cls, color: Color, mode: Mode):
        """Sets the new theme and notifies all listeners."""
        inst = cls.instance()
        inst.current_color = color
        inst.current_mode = mode
        cls.applyStylesheet()
        cls.emitThemeChanged()

    @classmethod
    def connect(cls, slot):
        """Connect a function to be called on theme change."""
        if slot not in cls.themeChanged:
            cls.themeChanged.append(slot)

    @classmethod
    def emitThemeChanged(cls):
        """Calls all connected slots."""
        for slot in cls.themeChanged:
            try:
                slot()
            except Exception as e:
                print(f"Error calling theme change slot: {e}")

    @classmethod
    def applyStylesheet(cls):
        """Generates and applies a global stylesheet."""
        color = cls.color()
        mode = cls.mode()
        style = f"""
            QMainWindow, QDialog {{
                background-color: {mode.bg.name()};
            }}
            QFrame#sidebar {{
                background-color: {mode.bg_2.name()};
                border-right: 1px solid {mode.border.name()};
            }}
            QFrame#content_frame {{
                background-color: {mode.bg.name()};
            }}
            QLabel, QCheckBox, QRadioButton {{
                color: {mode.text.name()};
                background-color: transparent;
            }}
            QLineEdit, QTextEdit, QSpinBox {{
                background-color: {mode.bg_2.name()};
                color: {mode.text.name()};
                border: 1px solid {mode.border.name()};
                border-radius: 4px;
                padding: 5px;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
                border-color: {color.name()};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {mode.border.name()};
                height: 4px;
                background: {mode.bg_2.name()};
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {color.name()};
                border: 1px solid {color.name()};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QProgressBar {{
                border: 1px solid {mode.border.name()};
                border-radius: 4px;
                text-align: center;
                color: {mode.text.name()};
            }}
            QProgressBar::chunk {{
                background-color: {color.name()};
                border-radius: 3px;
            }}
            QTreeView {{
                background-color: {mode.bg_2.name()};
                color: {mode.text.name()};
                border: 1px solid {mode.border.name()};
                border-radius: 4px;
            }}
            QTreeView::item:selected {{
                background-color: {color.name()};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {mode.bg_2.name()};
                color: {mode.text.name()};
                padding: 4px;
                border: 1px solid {mode.border.name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {mode.border.name()};
                border-top: none;
            }}
            QTabBar::tab {{
                background: {mode.bg.name()};
                color: {mode.text.name()};
                border: 1px solid {mode.border.name()};
                border-bottom: none;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {mode.bg_2.name()};
                border-bottom: 2px solid {color.name()};
            }}
            QStatusBar {{
                color: {mode.text.name()};
            }}
            QComboBox {{
                background-color: {mode.bg_2.name()};
                color: {mode.text.name()};
                border: 1px solid {mode.border.name()};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {mode.bg_2.name()};
                color: {mode.text.name()};
                selection-background-color: {color.name()};
                border: 1px solid {mode.border.name()};
            }}
        """
        app = QApplication.instance()
        if app:
            app.setStyleSheet(style)


class Icon(QWidget):
    """Mock Icon Widget."""
    _icons = {}  # Cache for generated pixmaps

    def __init__(self, name: Name, parent=None):
        super().__init__(parent)
        self.name = name
        self.color = Theme.color()
        self._icon_size = QSize(24, 24)
        self.setFixedSize(self._icon_size)
        Theme.connect(self.onThemeChanged)

    def setIconSize(self, width: int, height: int):
        self._icon_size = QSize(width, height)
        self.setFixedSize(self._icon_size)
        self.update()

    def onThemeChanged(self):
        self.color = Theme.color()
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pixmap = self._get_pixmap(self.name, self.color, self._icon_size)
        painter.drawPixmap(self.rect(), pixmap)

    @classmethod
    def _get_pixmap(cls, name: Name, color: QColor, size: QSize):
        cache_key = (name.value, color.name(), size.width(), size.height())
        if cache_key in cls._icons:
            return cls._icons[cache_key]

        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(color, 2))
        painter.setBrush(Qt.NoBrush)

        w, h = size.width(), size.height()
        m = min(w, h) * 0.1  # margin

        if name == Name.DASHBOARD:
            painter.drawRect(int(m), int(m), int(w/2 - m*1.5), int(h/2 - m*1.5))
            painter.drawRect(int(w/2 + m*0.5), int(m), int(w/2 - m*1.5), int(h/2 - m*1.5))
            painter.drawRect(int(m), int(h/2 + m*0.5), int(w/2 - m*1.5), int(h - (h/2 + m*1.5)))
            painter.drawRect(int(w/2 + m*0.5), int(h/2 + m*0.5), int(w/2 - m*1.5), int(h - (h/2 + m*1.5)))
        elif name == Name.DATA:
            painter.drawLine(int(m), int(h-m), int(w/4), int(h/2))
            painter.drawLine(int(w/4), int(h/2), int(w/2), int(h*0.75))
            painter.drawLine(int(w/2), int(h*0.75), int(w*0.75), int(h/4))
            painter.drawLine(int(w*0.75), int(h/4), int(w-m), int(h/2))
        elif name == Name.SETTINGS:
            # Simple gear icon
            painter.drawEllipse(QPoint(w/2, h/2), int(w/4), int(h/4))
            for i in range(8):
                painter.save()
                painter.translate(w/2, h/2)
                painter.rotate(i * 45)
                painter.drawRect(int(w/4), -2, int(w/8), 4)
                painter.restore()
        elif name == Name.WIFI:
            for i in range(3):
                size_factor = 1 - (i * 0.3)
                rect = QRect(int(w/2 - (w*0.4*size_factor)), int(h/2 - (h*0.4*size_factor)), int(w*0.8*size_factor), int(h*0.8*size_factor))
                painter.drawArc(rect, 225 * 16, 90 * 16)
        elif name == Name.BATTERY:
            painter.drawRoundedRect(int(m), int(h*0.25), int(w-m*3), int(h*0.5), 2, 2)
            painter.drawRect(int(w-m*2), int(h*0.4), 2, int(h*0.2))
            painter.setBrush(color)
            painter.drawRect(int(m*2), int(h*0.3), int((w-m*5)*0.8), int(h*0.4)) # 80% full
        elif name == Name.PYTHON:
            # Simplified Python logo
            painter.setBrush(QColor("#306998"))
            painter.drawRect(int(m), int(h*0.5), int(w*0.45), int(h*0.45))
            painter.setBrush(QColor("#FFD43B"))
            painter.drawRect(int(w*0.55 - m), int(m), int(w*0.45), int(h*0.45))
        else: # Default icon
            painter.drawEllipse(QPoint(w/2, h/2), int(w/2-m), int(h/2-m))
            painter.drawText(QRect(0,0,w,h), Qt.AlignCenter, "?")

        painter.end()
        cls._icons[cache_key] = pixmap
        return pixmap


class Type(Enum):
    """Mock Button Types Enum."""
    DEFAULT = 0
    PRIMARY = 1
    SECONDARY = 2
    TOOL = 3


class Button(QPushButton):
    """Mock Custom Button Widget."""
    def __init__(self, btn_type: Type, text: str = "", parent=None):
        super().__init__(text, parent)
        self.btn_type = btn_type
        self.icon_widget = None
        self.icon_name = None
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(35)
        Theme.connect(self.onThemeChanged)
        self.onThemeChanged() # Initial style set

    def setIcon(self, name: Name):
        # In a real button, you'd manage layout properly.
        # Here we just store it for styling.
        self.icon_name = name
        # A real implementation would add the icon widget to a layout.

    def onThemeChanged(self):
        mode = Theme.mode()
        color = Theme.color()
        color_secondary = Theme.color_secondary()

        style = f"""
            QPushButton {{
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                border: 1px solid transparent;
            }}
        """
        if self.btn_type == Type.PRIMARY:
            style += f"""
                QPushButton {{
                    background-color: {color.name()};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: {color_secondary.name()};
                }}
                QPushButton:pressed {{
                    background-color: {color.name()};
                }}
            """
        elif self.btn_type == Type.SECONDARY:
            style += f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color.name()};
                    border: 1px solid {color.name()};
                }}
                QPushButton:hover {{
                    background-color: {color.lighter(150).name()};
                }}
                QPushButton:pressed {{
                    background-color: {color.lighter(130).name()};
                }}
            """
        else: # DEFAULT
            style += f"""
                QPushButton {{
                    background-color: {mode.bg_2.name()};
                    color: {mode.text.name()};
                    border: 1px solid {mode.border.name()};
                }}
                QPushButton:hover {{
                    background-color: {mode.border.name()};
                }}
                QPushButton:pressed {{
                    background-color: {mode.bg_2.name()};
                }}
            """
        self.setStyleSheet(style)


class ToolButton(QPushButton):
    """Mock Custom ToolButton Widget."""
    def __init__(self, btn_type: Type, parent=None):
        super().__init__("", parent)
        self.btn_type = btn_type
        self.icon_widget = None
        self.icon_name = None
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(32, 32)
        Theme.connect(self.onThemeChanged)
        self.onThemeChanged()

    def setIcon(self, name: Name):
        if not self.icon_widget:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            self.icon_widget = Icon(name)
            self.icon_widget.setIconSize(18, 18)
            layout.addWidget(self.icon_widget, 0, Qt.AlignCenter)
        self.icon_name = name
        self.icon_widget.name = name
        self.icon_widget.onThemeChanged()

    def onThemeChanged(self):
        mode = Theme.mode()
        color = Theme.color()
        style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {mode.border.name()};
            }}
            QPushButton:pressed {{
                background-color: {mode.bg_2.name()};
            }}
        """
        self.setStyleSheet(style)
        if self.icon_widget:
            self.icon_widget.onThemeChanged()


# --- CUSTOM WIDGETS ---

class CircularProgressBar(QWidget):
    """A custom-drawn circular progress bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150)
        self._value = 0
        self.progress_color = Theme.color()
        self.bg_color = Theme.mode().border
        self.text_color = Theme.mode().text
        Theme.connect(self.onThemeChanged)

    def setValue(self, value: int):
        self._value = max(0, min(100, value))
        self.update()

    def value(self):
        return self._value

    def onThemeChanged(self):
        """Update colors from the theme and repaint."""
        self.progress_color = Theme.color()
        self.bg_color = Theme.mode().border
        self.text_color = Theme.mode().text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(5, 5, -5, -5)
        span_angle = int(self._value * 3.6 * 16) # 360 degrees * 16

        # Background circle
        pen = QPen(self.bg_color, 10, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress arc
        pen.setColor(self.progress_color)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -span_angle)

        # Text
        pen.setColor(self.text_color)
        painter.setPen(pen)
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self._value}%")


# --- PAGES ---

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Dashboard Overview")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Grid for stats
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Stat Card 1
        card1 = QFrame()
        card1.setObjectName("stat_card")
        card1_layout = QVBoxLayout(card1)
        card1_layout.addWidget(QLabel("Active Projects"))
        stat1 = QLabel("12")
        stat1.setStyleSheet("font-size: 28px; font-weight: bold;")
        card1_layout.addWidget(stat1)
        grid_layout.addWidget(card1, 0, 0)

        # Stat Card 2
        card2 = QFrame()
        card2.setObjectName("stat_card")
        card2_layout = QVBoxLayout(card2)
        card2_layout.addWidget(QLabel("Tasks Completed"))
        stat2 = QLabel("157")
        stat2.setStyleSheet("font-size: 28px; font-weight: bold;")
        card2_layout.addWidget(stat2)
        grid_layout.addWidget(card2, 0, 1)

        # Stat Card 3
        card3 = QFrame()
        card3.setObjectName("stat_card")
        card3_layout = QVBoxLayout(card3)
        card3_layout.addWidget(QLabel("Team Members"))
        stat3 = QLabel("8")
        stat3.setStyleSheet("font-size: 28px; font-weight: bold;")
        card3_layout.addWidget(stat3)
        grid_layout.addWidget(card3, 0, 2)

        layout.addLayout(grid_layout)

        # Custom Widget and Standard Widgets Section
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Left side: Custom Widget
        custom_widget_group = QFrame()
        custom_widget_layout = QVBoxLayout(custom_widget_group)
        custom_widget_layout.addWidget(QLabel("Live Server Load (Custom Widget)"))
        self.circular_progress = CircularProgressBar()
        custom_widget_layout.addWidget(self.circular_progress, 0, Qt.AlignCenter)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.circular_progress.setValue)
        self.slider.setValue(75)
        custom_widget_layout.addWidget(self.slider)
        h_layout.addWidget(custom_widget_group)

        # Right side: Standard Widgets
        standard_widgets_group = QFrame()
        standard_widgets_layout = QVBoxLayout(standard_widgets_group)
        standard_widgets_layout.addWidget(QLabel("Standard Controls"))
        standard_widgets_layout.addWidget(QCheckBox("Enable Feature X"))
        standard_widgets_layout.addWidget(QCheckBox("Enable Feature Y (Checked)").apply(lambda x: x.setChecked(True)))
        standard_widgets_layout.addWidget(QRadioButton("Option A"))
        standard_widgets_layout.addWidget(QRadioButton("Option B"))
        standard_widgets_layout.addWidget(QProgressBar().apply(lambda x: x.setValue(40)))
        standard_widgets_layout.addStretch()
        h_layout.addWidget(standard_widgets_group)

        layout.addLayout(h_layout)
        layout.addStretch()

        self.onThemeChanged()
        Theme.connect(self.onThemeChanged)

    def onThemeChanged(self):
        mode = Theme.mode()
        style = f"""
            QFrame#stat_card {{
                background-color: {mode.bg_2.name()};
                border-radius: 8px;
                padding: 15px;
            }}
        """
        self.setStyleSheet(style)


class DataViewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_layout = QHBoxLayout()
        title = QLabel("Data Explorer")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        edit_btn = ToolButton(Type.TOOL)
        edit_btn.setIcon(Name.EDIT)
        save_btn = ToolButton(Type.TOOL)
        save_btn.setIcon(Name.SAVE)
        title_layout.addWidget(edit_btn)
        title_layout.addWidget(save_btn)
        layout.addLayout(title_layout)

        # Tab Widget for different views
        tab_widget = QTabWidget()

        # Tab 1: Tree View
        tree_view_tab = QWidget()
        tree_layout = QVBoxLayout(tree_view_tab)

        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(False)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Name', 'Type', 'Size'])

        root_item = model.invisibleRootItem()

        # Populate tree view with sample data
        project1 = QStandardItem("Project Alpha")
        project1.appendRow([QStandardItem("config.yml"), QStandardItem("YAML"), QStandardItem("1.2 KB")])
        src_folder = QStandardItem("src")
        src_folder.appendRow([QStandardItem("main.py"), QStandardItem("Python Script"), QStandardItem("15 KB")])
        src_folder.appendRow([QStandardItem("utils.py"), QStandardItem("Python Script"), QStandardItem("8 KB")])
        project1.appendRow(src_folder)
        root_item.appendRow(project1)

        project2 = QStandardItem("Project Beta")
        project2.appendRow([QStandardItem("index.html"), QStandardItem("HTML"), QStandardItem("4 KB")])
        assets_folder = QStandardItem("assets")
        assets_folder.appendRow([QStandardItem("logo.svg"), QStandardItem("SVG Image"), QStandardItem("22 KB")])
        assets_folder.appendRow([QStandardItem("style.css"), QStandardItem("Stylesheet"), QStandardItem("11 KB")])
        project2.appendRow(assets_folder)
        root_item.appendRow(project2)

        self.tree_view.setModel(model)
        self.tree_view.expandAll()
        tree_layout.addWidget(self.tree_view)
        tab_widget.addTab(tree_view_tab, "File System")

        # Tab 2: Text Editor
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        text_edit = QTextEdit()
        text_edit.setPlainText("This is a sample text editor to test theme styles.\n\n"
                               "You can type here to see how the text and background colors look.")
        editor_layout.addWidget(text_edit)
        tab_widget.addTab(editor_tab, "Notes")

        layout.addWidget(tab_widget)


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("MyCompany", "ThemeTesterApp")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # --- Theme Settings ---
        theme_title = QLabel("Theme Customization")
        theme_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(theme_title)

        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Theme Mode:"))
        self.mode_combo = QComboBox()
        for mode in Mode:
            self.mode_combo.addItem(mode.name.capitalize(), mode)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Color Selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Primary Color:"))
        self.color_combo = QComboBox()
        for color in Color:
            pixmap = QPixmap(20, 20)
            pixmap.fill(color.primary)
            self.color_combo.addItem(QIcon(pixmap), color.name.capitalize(), color)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        # --- Interactive Controls ---
        controls_title = QLabel("Interactive Controls")
        controls_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(controls_title)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(Button(Type.DEFAULT, "Default"))
        button_layout.addWidget(Button(Type.SECONDARY, "Secondary"))
        button_layout.addWidget(Button(Type.PRIMARY, "Primary"))
        layout.addLayout(button_layout)

        # Dialog Launcher
        dialog_btn = Button(Type.DEFAULT, "Test Dialog")
        dialog_btn.setIcon(Name.INFO)
        dialog_btn.clicked.connect(self.show_test_dialog)
        layout.addWidget(dialog_btn)

        # --- Other Settings ---
        other_title = QLabel("Other Settings")
        other_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(other_title)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(QLabel("Username:"), 0, 0)
        form_layout.addWidget(QLineEdit("testuser"), 0, 1)
        form_layout.addWidget(QLabel("Email:"), 1, 0)
        form_layout.addWidget(QLineEdit("test@example.com"), 1, 1)
        form_layout.addWidget(QLabel("Age:"), 2, 0)
        form_layout.addWidget(QSpinBox(), 2, 1)
        layout.addLayout(form_layout)

        layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # --- Connections and Initial State ---
        self.mode_combo.currentIndexChanged.connect(self.apply_theme_changes)
        self.color_combo.currentIndexChanged.connect(self.apply_theme_changes)
        self.load_settings()

    def apply_theme_changes(self):
        """Updates the application theme and saves the selection."""
        selected_color = self.color_combo.currentData()
        selected_mode = self.mode_combo.currentData()

        if selected_color and selected_mode:
            try:
                Theme.setTheme(selected_color, selected_mode)
                # Save the new settings
                self.settings.setValue("theme_color", selected_color.name)
                self.settings.setValue("theme_mode", selected_mode.name)
            except Exception as e:
                print(f"Error applying theme: {e}")

    def load_settings(self):
        """Loads theme from QSettings and updates the UI."""
        color_name = self.settings.value("theme_color", Color.GREEN.name)
        mode_name = self.settings.value("theme_mode", Mode.DARK.name)

        color_index = self.color_combo.findData(Color[color_name])
        mode_index = self.mode_combo.findData(Mode[mode_name])

        # Block signals to prevent apply_theme_changes from firing prematurely
        self.color_combo.blockSignals(True)
        self.mode_combo.blockSignals(True)

        if color_index != -1: self.color_combo.setCurrentIndex(color_index)
        if mode_index != -1: self.mode_combo.setCurrentIndex(mode_index)

        self.color_combo.blockSignals(False)
        self.mode_combo.blockSignals(False)

    def show_test_dialog(self):
        """Shows a themed QMessageBox."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Themed Dialog")
        dialog.setText("This is a test dialog to check theme inheritance.")
        dialog.setInformativeText("All colors and styles should match the main application window.")
        dialog.setIconPixmap(Icon._get_pixmap(Name.INFO, Theme.color(), QSize(64,64)))
        dialog.addButton(Button(Type.PRIMARY, "OK"), QMessageBox.AcceptRole)
        dialog.addButton(Button(Type.DEFAULT, "Cancel"), QMessageBox.RejectRole)

        # The stylesheet is applied globally, so it should be themed automatically.
        dialog.exec()

# --- MAIN WINDOW ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Theme Tester")
        self.setMinimumSize(900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(10)

        app_title_layout = QHBoxLayout()
        app_icon = Icon(Name.PYTHON)
        app_icon.setIconSize(32,32)
        app_title_layout.addWidget(app_icon)
        app_title = QLabel("Theme App")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        app_title_layout.addWidget(app_title)
        self.sidebar_layout.addLayout(app_title_layout)

        self.sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Navigation Buttons
        self.nav_buttons = {}
        self.add_nav_button("dashboard", Name.DASHBOARD, "Dashboard")
        self.add_nav_button("data_view", Name.DATA, "Data View")
        self.add_nav_button("settings", Name.SETTINGS, "Settings")

        self.sidebar_layout.addStretch()

        help_button = Button(Type.DEFAULT, "Help & Info")
        help_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.qt.io")))
        self.sidebar_layout.addWidget(help_button)

        self.main_layout.addWidget(self.sidebar)

        # --- Content Area ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        # Add pages
        self.dashboard_page = DashboardPage()
        self.data_view_page = DataViewPage()
        self.settings_page = SettingsPage()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.data_view_page)
        self.stacked_widget.addWidget(self.settings_page)

        self.main_layout.addWidget(self.content_frame)

        # --- Status Bar ---
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.status_bar.addPermanentWidget(Icon(Name.WIFI))
        self.status_bar.addPermanentWidget(Icon(Name.BATTERY))

        # --- Animation ---
        self.fade_animation = QPropertyAnimation(self.content_frame, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # --- Initial State ---
        self.nav_buttons["dashboard"].click()
        Theme.connect(self.update_status_bar)

    def add_nav_button(self, name, icon_name, text):
        button = Button(Type.DEFAULT, text)
        button.setIcon(icon_name) # This is a mock, but shows intent
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.clicked.connect(lambda: self.switch_page(name))
        self.sidebar_layout.addWidget(button)
        self.nav_buttons[name] = button

    def switch_page(self, name):
        page_map = {
            "dashboard": 0,
            "data_view": 1,
            "settings": 2
        }
        index = page_map.get(name)
        if index is not None and self.stacked_widget.currentIndex() != index:
            self.stacked_widget.setCurrentIndex(index)
            self.status_label.setText(f"{name.replace('_', ' ').title()} Page Loaded")
            self.fade_animation.start()

    def update_status_bar(self):
        """Just an example of a component reacting to theme change."""
        self.status_label.setText("Theme updated!")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))

# --- Monkey-patching QWidget for easier setup ---
def apply(self, func):
    func(self)
    return self
QWidget.apply = apply

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load saved theme or set a default before creating the window
    settings = QSettings("MyCompany", "ThemeTesterApp")
    color_name = settings.value("theme_color", Color.GREEN.name)
    mode_name = settings.value("theme_mode", Mode.DARK.name)

    try:
        initial_color = Color[color_name]
        initial_mode = Mode[mode_name]
    except KeyError:
        # Handle cases where saved settings are invalid
        print("Invalid theme settings found, resetting to default.")
        initial_color = Color.GREEN
        initial_mode = Mode.DARK
        settings.setValue("theme_color", initial_color.name)
        settings.setValue("theme_mode", initial_mode.name)

    Theme.setTheme(initial_color, initial_mode)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
