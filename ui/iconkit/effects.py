"""ui/iconkit/effects.py

Provides the ApplyHoverEffects class for dynamically changing button icons on hover and toggle events.
"""

from PySide6.QtCore import QSize
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QAbstractButton

from .themed_icon import ThemedIcon


# ── Class Definition ────────────────────────────────────────────────────────────
class ApplyHoverEffects:
    @staticmethod
    def recolor(
        button: QAbstractButton,
        file_name: str,
        size: QSize,
        variant: str
    ):
        """Apply dynamic icon recoloring for HOVER/checked states."""
        # Load all icon states
        icon_default = ThemedIcon(file_name, size, variant).icon()
        icon_hover = ThemedIcon(file_name, size, variant).icon_for_state("HOVER")
        icon_checked = ThemedIcon(file_name, size, variant).icon_for_state("CHECKED")

        # Apply default icon and size
        button.setIcon(icon_default)
        button.setIconSize(size)

        # Store icons for use in events
        button._icon_default = icon_default
        button._icon_hover = icon_hover
        button._icon_checked = icon_checked

        # Event overrides
        def enterEvent(event):
            if not button.isChecked():
                button.setIcon(button._icon_hover)

        def leaveEvent(event):
            if not button.isChecked():
                button.setIcon(button._icon_default)

        def updateCheckedState():
            icon = button._icon_checked if button.isChecked() else button._icon_default
            button.setIcon(icon)

        # Patch events
        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent
        button.toggled.connect(updateCheckedState)