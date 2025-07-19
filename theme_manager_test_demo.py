import sys
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QFrame, QLabel, QComboBox, QToolBar,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from app.theme_manager.theme import Theme
from app.theme_manager.config import Color, Mode

class ColorWidget(QFrame):
    """A custom widget to display a color with its name."""
    def __init__(
            self,
            frame_type: str,
            label_type: str,
            text: str,
            parent: Optional[QWidget] = None
    ) -> QFrame:
        super().__init__(parent)
        self.setProperty("type", frame_type)
        self.setMinimumSize(100, 60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        label = QLabel(text, self)
        label.setProperty("type", label_type)
        label.setWordWrap(True)

        layout.addWidget(label)

class ThemeTesterWindow(QMainWindow):
    """The main window for the theme testing application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Manager Color Tester")
        self.setGeometry(100, 100, 1400, 900)


        self.setup_ui()
        self.setup_toolbar()

        # Connect to the theme manager's signal to update window background
        self.update_window_style()


    def setup_ui(self):
        """Create and arrange all the widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setProperty("type", "background")

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Top Row: Primary, Secondary, Tertiary, Error ---
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(15)
        main_layout.addLayout(top_row_layout)

        color_groups = [
            ("Primary", "primary"), ("Secondary", "secondary"),
            ("Tertiary", "tertiary"), ("Error", "error")
        ]

        for group_name, group_prefix in color_groups:
            group_layout = QVBoxLayout()
            group_layout.setSpacing(10)
            group_layout.addWidget(ColorWidget(group_prefix, f"on_{group_prefix}", group_name))
            group_layout.addWidget(ColorWidget(f"on_{group_prefix}", group_prefix, f"On {group_name}"))
            group_layout.addWidget(ColorWidget(f"{group_prefix}_container", f"on_{group_prefix}_container", f"{group_name} Container"))
            group_layout.addWidget(ColorWidget(f"on_{group_prefix}_container", f"{group_prefix}_container", f"On {group_name} Container"))
            top_row_layout.addLayout(group_layout)

        # --- Middle Row: Surfaces and Inverse ---
        middle_row_layout = QHBoxLayout()
        middle_row_layout.setSpacing(15)
        main_layout.addLayout(middle_row_layout)

        # Surface group
        surface_group = QWidget()
        surface_layout = QVBoxLayout(surface_group)
        surface_layout.setSpacing(10)
        surface_layout.setContentsMargins(0,0,0,0)

        surf_row1 = QHBoxLayout()
        surf_row1.addWidget(ColorWidget("surface_dim", "on_surface", "Surface Dim"))
        surf_row1.addWidget(ColorWidget("surface", "on_surface", "Surface"))
        surf_row1.addWidget(ColorWidget("surface_bright", "on_surface", "Surface Bright"))
        surface_layout.addLayout(surf_row1)

        surf_row2 = QHBoxLayout()
        surf_row2.addWidget(ColorWidget("surface_container_lowest", "on_surface", "Surf. C. Lowest"))
        surf_row2.addWidget(ColorWidget("surface_container_low", "on_surface", "Surf. C. Low"))
        surf_row2.addWidget(ColorWidget("surface_container", "on_surface", "Surf. Container"))
        surf_row2.addWidget(ColorWidget("surface_container_high", "on_surface", "Surf. C. High"))
        surf_row2.addWidget(ColorWidget("surface_container_highest", "on_surface", "Surf. C. Highest"))
        surface_layout.addLayout(surf_row2)

        middle_row_layout.addWidget(surface_group, 3) # 3/4 of the space

        # Inverse group
        inverse_group = QWidget()
        inverse_layout = QVBoxLayout(inverse_group)
        inverse_layout.setSpacing(10)
        inverse_layout.setContentsMargins(0,0,0,0)
        inverse_layout.addWidget(ColorWidget("inverse_surface", "inverse_on_surface", "Inverse Surface"))
        inverse_layout.addWidget(ColorWidget("inverse_on_surface", "inverse_surface", "Inverse On Surface"))
        inverse_layout.addWidget(ColorWidget("inverse_primary", "on_primary", "Inverse Primary")) # Text on inverse primary is on_primary
        middle_row_layout.addWidget(inverse_group, 1) # 1/4 of the space


        # --- Bottom Row: Utility Colors ---
        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setSpacing(15)
        main_layout.addLayout(bottom_row_layout)

        bottom_row_layout.addWidget(ColorWidget("on_surface", "surface", "On Surface"))
        bottom_row_layout.addWidget(ColorWidget("on_surface_variant", "surface_variant", "On Surface Var."))
        bottom_row_layout.addWidget(ColorWidget("outline", "on_surface", "Outline"))
        bottom_row_layout.addWidget(ColorWidget("outline_variant", "on_surface", "Outline Variant"))
        bottom_row_layout.addWidget(ColorWidget("scrim", "on_surface", "Scrim"))
        bottom_row_layout.addWidget(ColorWidget("shadow", "on_surface", "Shadow"))

        main_layout.addStretch()


    def setup_toolbar(self):
        """Create the toolbar with theme controls."""
        toolbar = QToolBar("Theme Controls")
        self.addToolBar(toolbar)

        # Theme mode toggle button
        self.toggle_theme_action = QAction("Toggle Light/Dark Mode", self)
        self.toggle_theme_action.triggered.connect(Theme.toggle_theme_mode)
        toolbar.addAction(self.toggle_theme_action)

        toolbar.addSeparator()

        # Color selection dropdown
        toolbar.addWidget(QLabel("  Theme Color: "))
        self.color_combo = QComboBox()
        for color_enum in Color:
            # Use the enum's built-in .name and format it for display
            display_text = color_enum.name.replace('_', ' ').title()
            self.color_combo.addItem(display_text, color_enum)

        # Set the current item based on the formatted name
        current_theme_color = Theme.get_current_theme_color()
        initial_text = current_theme_color.name.replace('_', ' ').title()
        self.color_combo.setCurrentText(initial_text)

        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        toolbar.addWidget(self.color_combo)

    def on_color_changed(self, text: str):
        """Handle theme color change from the combobox."""
        selected_color = self.color_combo.currentData()
        if selected_color:
            Theme.set_theme_color(selected_color)

    def update_window_style(self):
        """Forces a style update on the main window to apply background color."""
        self.style().unpolish(self)
        self.style().polish(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Theme.set_theme(Color.YELLOW, Mode.LIGHT)  # Initialize with default theme
    # Create and show the main window
    window = ThemeTesterWindow()
    window.show()

    sys.exit(app.exec())
