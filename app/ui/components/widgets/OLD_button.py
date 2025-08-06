"""app/ui/components/widgets/button.py

A theme-aware QPushButton and QToolButton with dynamic, stateful icons.

⚠️ Legacy Version. This class has been moved to app/ui/components/widgets/button.py
and will be removed from this location in future releases ⚠️
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy, QToolButton, QLabel, QHBoxLayout

from app.appearance.icon.config import Name, Type
from app.appearance.icon.mixin import IconMixin
from app.appearance.theme import Theme
from app.appearance.config import Qss


# ── Button ───────────────────────────────────────────────────────────────────────────────────
class Button(QPushButton, IconMixin):
    def __init__(
        self,
        label: str = "",
        type: Type = Type.DEFAULT,
        parent=None
    ):
        """
        A theme-aware QPushButton with dynamic, stateful icons.

        Args:
            type (Type): The button type (e.g., default, primary, etc.).
            label (str): Optional text label.
            parent: Optional QWidget parent.
        """
        super().__init__(label, parent)

        self._button_type = type
        self._button_size: QSize | None = None
        self._custom_icon_size: QSize | None = None

        # Enable layout compatibility by default
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def setButtonSize(self, width: int, height: int):
        """
        Lock the button to a specific size.
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
        """
        self._button_size = QSize(width, height)
        self.updateGeometry()

    def setAutoSize(self, enabled: bool = True):
        """
        Enable or disable auto-sizing behavior.
        Args:
            enabled (bool): If True, button will resize based on icon + label
        """
        if enabled:
            self._button_size = None
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.updateGeometry()

    def setCustomIconSize(self, width: int, height: int):
        """
        Set the icon size.
        Args:
            width (int): Icon width
            height (int): Icon height
        """
        size = QSize(width, height)
        self._custom_icon_size = size
        self.setIconSize(size)

        self.updateGeometry()
        self.adjustSize()

    def setButtonCheckable(self, checkable: bool):
        """
        Enable or disable checkable behavior.
        Args:
            checkable (bool): True if checkable
        """
        self.setCheckable(checkable)
        if checkable and not hasattr(self, '_icon_toggle_connected'):
            self.toggled.connect(self._update_icon)
            self._icon_toggle_connected = True

    def setIcon(self, icon_name: Name):
        """
        Set the icon using a Name enum.
        Args:
            icon_name (Name): The icon to assign
        """
        self.setIconFromName(icon_name)

    def sizeHint(self) -> QSize:
        # If manual override exists, use it
        if self._button_size:
            return self._button_size

        # Base size Qt would normally use
        base = super().sizeHint()

        icon_size = self.iconSize()
        icon_w = icon_size.width()
        icon_h = icon_size.height()

        spacing = 6 if self.text().strip() else 0
        text_w = self.fontMetrics().horizontalAdvance(self.text())

        # Estimate height: max of icon or font height + padding
        text_h = self.fontMetrics().height()
        height = max(base.height(), icon_h, text_h + 12)

        # Estimate width: icon + spacing + text + side padding
        width = icon_w + spacing + text_w + 16

        return QSize(width, height)

    def enterEvent(self, event: QEvent) -> None:
        IconMixin.enterEvent(self, event)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        IconMixin.leaveEvent(self, event)
        super().leaveEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        IconMixin.changeEvent(self, event)
        super().changeEvent(event)

# ── Tool Button ──────────────────────────────────────────────────────────────────────────────
class ToolButton(QToolButton, IconMixin):
    """
    A theme-aware QToolButton with dynamic, stateful icons.

    Primarily used for icon-only buttons
    """
    def __init__(
        self,
        type: Type = Type.DEFAULT,
        parent=None
    ):
        """
        A theme-aware QToolButton with dynamic, stateful icons.

        Args:
            type (Type): The button type (e.g., default, primary, etc.).
            parent: QWidget parent.
        """
        super().__init__(parent)

        # store button type for icon setup
        self._button_type = type

        # store sizes for access
        self._button_size = None
        self._custom_icon_size = None

    def setButtonSize(self, width: int, height: int):
        """
        Set the button size.

        Args:
            width (int): Button width in pixels
            height (int): Button height in pixels
        """
        size = QSize(width, height)
        self._button_size = size
        self.setFixedSize(size)

    def setCustomIconSize(self, width: int, height: int):
        """
        Set the icon size.

        Args:
            width (int): Icon width in pixels
            height (int): Icon height in pixels
        """
        size = QSize(width, height)
        self._custom_icon_size = size
        self.setIconSize(size)

    def setButtonCheckable(self, checkable: bool):
        """
        Set whether the button is checkable.

        Args:
            checkable (bool): True if button should be checkable, False otherwise.
        """
        self.setCheckable(checkable)

        # connect toggled signal to update icon state when checked/unchecked
        if checkable:
            # Only connect if not already connected to avoid duplicates
            if not hasattr(self, '_icon_toggle_connected'):
                self.toggled.connect(self._update_icon)
                self._icon_toggle_connected = True

    def setIcon(self, icon_name: Name):
        """
        Set the icon for this button.

        Args:
            icon_name (Name): The Name enum member specifying the icon.
        """
        self.setIconFromName(icon_name)

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter events for hover icon state."""
        IconMixin.enterEvent(self, event)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave events to restore default icon state."""
        IconMixin.leaveEvent(self, event)
        super().leaveEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        """Handle change events for enabled/disabled icon state."""
        IconMixin.changeEvent(self, event)
        super().changeEvent(event)

# ── Navigation Button ────────────────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    """
    A composite navigation button that synchronizes its hover and checked
    state with its child icon and label.

    Primary usage is for sidebar navigation where the button contains an icon and text label.
    """

    # TODO:
    def __init__(
        self,
        text: str,
        name: Name,
        height: int = 40,
        width: int | None = None,
        spacing: int = 10,
        checkable: bool = True,
        parent=None
    ):
        super().__init__("", parent)
        self.setObjectName("NavButton")

        self.setCheckable(checkable)

        # Register for component-specific styling
        Theme.register_widget(self, Qss.NAV_BUTTON)

        # ── Internal Widgets ──
        self._icon = ToolButton(Type.SECONDARY)
        self._icon.setIcon(name)
        self._icon.setButtonCheckable(checkable)
        self._icon.setFocusPolicy(Qt.NoFocus)

        self._label = QLabel(text)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # link state changes to update visuals
        self.toggled.connect(self._update_visuals)
        self._update_visuals()

        # ─── Layout & Sizing ───────────
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(40, 0, 10, 0)
        self._layout.setSpacing(spacing)
        self._layout.addWidget(self._icon)
        self._layout.addWidget(self._label)
        self._layout.addStretch()
        self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)

    def _update_visuals(self) -> None:
        """Helper to synchronize the internal icon state and set label style property."""
        # sync the internal ToolButton's checked state with our state
        self._icon.setChecked(self.isChecked())

        # set appropriate label state for styling
        if self.isChecked():
            self._label.setProperty("state", "CHECKED")
        elif self.underMouse():
            self._label.setProperty("state", "HOVER")
        else:
            self._label.setProperty("state", "DEFAULT")

        self.style().unpolish(self._label)
        self.style().polish(self._label)

    # ─── Public Methods & Overrides ──────────────────────────────────────────
    def setChecked(self, checked: bool) -> None:
        """Override setChecked to force a style update."""
        super().setChecked(checked)

        self.style().unpolish(self)
        self.style().polish(self)

    def enterEvent(self, event):
        """Override enterEvent to update icon and force style update."""
        super().enterEvent(event)
        self._update_visuals()

        # Manually trigger icon hover state
        self._icon.enterEvent(event)

        self.style().polish(self)

    def leaveEvent(self, event):
        """Override leaveEvent to update icon and force style update."""
        super().leaveEvent(event)
        self._update_visuals()

        # Manually trigger icon leave state
        self._icon.leaveEvent(event)

        self.style().polish(self)

    def setText(self, text: str) -> None:
        """Sets the text of the internal label."""
        self._label.setText(text)

    def text(self) -> str:
        """Returns the text of the internal label."""
        return self._label.text()
