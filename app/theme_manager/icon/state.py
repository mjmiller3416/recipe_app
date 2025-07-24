"""app/theme_manager/icon/state.py

Module providing IconState for dynamic button icon effects.

IconState applies theme-aware icon variants (DEFAULT, HOVER, CHECKED,
and DISABLED) to QAbstractButton widgets and updates icons on hover and
toggle events.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from app.theme_manager.icon.factory import IconFactory
from PySide6.QtWidgets import QAbstractButton

from app.theme_manager.icon.config import Name, Size, Type, State  # updated from app_icon.py

# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class IconState:
    @staticmethod
    def recolor(
        button: QAbstractButton,
        icon_name: Name,
        size: Size,
        icon_type: Type
    ) -> None:
        """Apply dynamic icon recoloring for button states."""
        factory = IconFactory(icon_name, size, icon_type)

        button._icon_default = factory.icon_for_state(State.DEFAULT)
        button._icon_hover = factory.icon_for_state(State.HOVER)
        button._icon_checked = factory.icon_for_state(State.CHECKED)
        button._icon_disabled = factory.icon_for_state(State.DISABLED)

        button.setIcon(button._icon_default)
        button.setIconSize(size.value)

        # Event overrides
        original_enter = getattr(button, 'enterEvent', None)
        original_leave = getattr(button, 'leaveEvent', None)

        def enterEvent(event):
            if not button.isChecked():
                button.setIcon(button._icon_hover)
            if callable(original_enter):
                original_enter(event)

        def leaveEvent(event):
            if not button.isChecked():
                button.setIcon(button._icon_default)
            if callable(original_leave):
                original_leave(event)

        def updateCheckedState():
            icon = button._icon_checked if button.isChecked() else button._icon_default
            button.setIcon(icon)

        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        button.toggled.connect(updateCheckedState)
