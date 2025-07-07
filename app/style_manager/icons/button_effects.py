"""Module providing ButtonEffects for dynamic button icon effects.

ButtonEffects applies theme-aware icon variants (DEFAULT, HOVER, CHECKED,
and DISABLED) to QAbstractButton widgets and updates icons on hover and
toggle events.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from pathlib import Path
from app.style_manager.icons.icon_factory import IconFactory
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractButton



# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class ButtonEffects:
    @staticmethod
    def recolor(
        button: QAbstractButton,
        icon_path: Path,
        size: QSize,
        variant: str
    ) -> None:
        """Apply dynamic icon recoloring for button states."""
        # Load all icon states
        factory = IconFactory(icon_path, size, variant)
        icon_default = factory.icon()
        icon_hover = factory.icon_for_state("HOVER")
        icon_checked = factory.icon_for_state("CHECKED")
        icon_disabled = factory.icon_for_state("DISABLED")

        # Apply default icon and size
        button.setIcon(icon_default)
        button.setIconSize(size)

        # Store icons for use in events
        button._icon_default = icon_default
        button._icon_hover = icon_hover
        button._icon_checked = icon_checked
        button._icon_disabled = icon_disabled

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

        # Patch events
        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        button.toggled.connect(updateCheckedState)
