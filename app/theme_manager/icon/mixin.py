"""app/theme_manager/icon/mixin.py

This module provides a mixin for QAbstractButton widgets to handle themed icons
with state management.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon

from app.theme_manager.icon.config import Name, State
from app.theme_manager.icon.factory import IconFactory
from app.theme_manager.icon.loader import IconLoader

# ── Icon Mixin ───────────────────────────────────────────────────────────────────────────────
class IconMixin:
    """A mixin to provide theme-aware, stateful icon logic to QAbstractButton widgets."""
    def init_icon(self, icon_enum: Name):
        """Initializes the icon states, caches them, and registers for theme updates."""
        self._icon_enum = icon_enum
        self._icon_spec = icon_enum.spec
        self._icons: dict[State, QIcon] = {}

        self.setIconSize(self._icon_spec.size.value)
        if self.isCheckable():
            self.toggled.connect(self._update_icon)

        IconLoader.register(self)

    def refresh_theme(self, palette: dict) -> None:
        """Called by IconLoader. Regenerates all icon states and applies the correct one."""
        factory = IconFactory(self._icon_enum)
        self._icons = {
            State.DEFAULT: factory.icon_for_state(State.DEFAULT),
            State.HOVER: factory.icon_for_state(State.HOVER),
            State.CHECKED: factory.icon_for_state(State.CHECKED),
            State.DISABLED: factory.icon_for_state(State.DISABLED)
        }
        self._update_icon()

    def _update_icon(self) -> None:
        """Applies the correct icon from the cache based on the button's current state."""
        if not self.isEnabled():
            self.setIcon(self._icons.get(State.DISABLED))
        elif self.isChecked():
            self.setIcon(self._icons.get(State.CHECKED))
        else:
            self.setIcon(self._icons.get(State.DEFAULT))

    def enterEvent(self, event: QEvent) -> None:
        if self.isEnabled() and not self.isChecked():
            self.setIcon(self._icons.get(State.HOVER))
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        if self.isEnabled() and not self.isChecked():
            self._update_icon()
        super().leaveEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.EnabledChange:
            self._update_icon()
        super().changeEvent(event)
