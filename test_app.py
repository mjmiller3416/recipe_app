import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout, QWidget)

# Assuming ct_tool_button is in a location Python can import
# You may need to adjust this import path based on your project structure
from app.ui.widgets.ct_tool_button import CTToolButton


class NavButton(QPushButton):
    """
    A composite navigation button, inheriting from QPushButton to ensure
    compatibility with QButtonGroup and other Qt mechanisms.

    It uses a custom layout to place a CTToolButton icon and a QLabel, providing
    fine-grained control over spacing and appearance while behaving like a
    standard button.
    """
    # The clicked and toggled signals are inherited from QPushButton

    def __init__(
        self,
        text: str,
        file_path: Path,
        icon_variant: str | dict,
        # --- Optional Parameters ---
        icon_size: QSize = QSize(22, 22),
        height: int = 40,
        width: int | None = None,
        spacing: int = 15,
        checkable: bool = True,
        parent=None
    ):
        """
        Initializes the NavButton instance.

        Args:
            text (str): The text to display on the button's label.
            file_path (Path): The file path for the icon SVG.
            icon_variant (str | dict): The theme variant for the CTToolButton icon.
            icon_size (QSize, optional): The size for the icon. Defaults to QSize(22, 22).
            height (int, optional): The fixed height of the widget. Defaults to 40.
            width (int | None, optional): The fixed width of the widget. If None, width is flexible. Defaults to None.
            spacing (int, optional): The space in pixels between the icon and the label. Defaults to 15.
            checkable (bool, optional): Whether the button can be checked. Defaults to True.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__("", parent) # Set own text to empty

        self.setCheckable(checkable)

        # ─── Internal Widgets ───────────
        # These widgets are for display purposes inside our custom layout.
        self._icon = CTToolButton(
            file_path=file_path,
            icon_size=icon_size,
            variant=icon_variant,
            checkable=checkable,
            hover_effects=True,
        )
        self._icon.setStyleSheet("border: none; background-color: transparent;")
        self._icon.setFocusPolicy(Qt.NoFocus)
        self._icon.setAttribute(Qt.WA_TransparentForMouseEvents) # Clicks pass through to the parent QPushButton

        self._label = QLabel(text)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # --- Link States ---
        # When the main button is toggled, also toggle the internal icon
        self.toggled.connect(self._icon.setChecked)
        if self.isChecked():
            self._icon.setChecked(True)

        # ─── Layout ───────────
        # We assign a custom layout to this QPushButton to arrange our internal widgets.
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 10, 0)
        self._layout.setSpacing(spacing)
        self._layout.addWidget(self._icon)
        self._layout.addWidget(self._label)
        self._layout.addStretch()

        # ─── Sizing ───────────
        self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)

    def setText(self, text: str) -> None:
        """Sets the text of the internal label."""
        self._label.setText(text)

    def text(self) -> str:
        """Returns the text of the internal label."""
        return self._label.text()

# The example usage code does not need to change, as it was already correct.
# It will now work as expected with the corrected NavButton class.
if __name__ == '__main__':
    # ─── Example Usage ───────────
    app = QApplication(sys.argv)

    # --- Example Theme Palettes (for demonstration) ---
    NAV_ICON_VARIANT = {
        "DEFAULT": "#e92300",
        "HOVER": "#bd93f9",
        "CHECKED": "#ff79c6",
    }
    
    # --- Example Stylesheet (QSS) ---
    # The NavButton, as a QPushButton, responds to :checked and :hover
    STYLESHEET = """
        /* Target NavButton by its class name */
        NavButton {
            background-color: transparent;
            border: none;
            border-radius: 5px;
            text-align: left; /* Important for layout */
        }
        NavButton:hover {
            background-color: #44475a;
        }
        NavButton:checked {
            background-color: #3a3d4d;
        }
        
        /* The internal QLabel is styled directly */
        NavButton QLabel {
            color: #f8f8f2;
            font-size: 14px;
            font-weight: bold;
        }
        NavButton:hover QLabel {
            color: #bd93f9;
        }
        NavButton:checked QLabel {
            color: #ff79c6;
        }
    """

    # --- Main Window Setup ---
    window = QWidget()
    window.setWindowTitle("NavButton Corrected Example")
    window.setStyleSheet(STYLESHEET)
    
    main_layout = QVBoxLayout(window)

    # --- Create NavButton instances ---
    # NOTE: You need a valid SVG file path for the icons to appear.
    icon_path = Path("./assets/icons/home.svg") # <--- CHANGE THIS PATH
    if not icon_path.exists():
         print(f"Warning: Icon path not found at '{icon_path}'. Please update the path in the example.")
         icon_path.parent.mkdir(exist_ok=True)
         with open(icon_path, 'w') as f: # Create a dummy SVG
             f.write('<svg width="24" height="24" viewBox="0 0 24 24"></svg>')

    button1 = NavButton("Home", icon_path, NAV_ICON_VARIANT)
    button2 = NavButton("Dashboard", icon_path, NAV_ICON_VARIANT)
    button3 = NavButton("Settings", icon_path, NAV_ICON_VARIANT)
    button4 = NavButton("Account", icon_path, NAV_ICON_VARIANT)
    
    # --- Use QButtonGroup for exclusive selection ---
    # THIS WILL NOW WORK CORRECTLY
    nav_button_group = QButtonGroup(window)
    nav_button_group.setExclusive(True)
    nav_button_group.addButton(button1)
    nav_button_group.addButton(button2)
    nav_button_group.addButton(button3)
    nav_button_group.addButton(button4)
    
    # Set Home button as checked by default after adding to group
    button1.setChecked(True)

    # --- Add buttons to layout ---
    main_layout.addWidget(button1)
    main_layout.addWidget(button2)
    main_layout.addWidget(button3)
    main_layout.addWidget(button4)
    main_layout.addStretch()

    window.show()
    sys.exit(app.exec())