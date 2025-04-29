"""core/helpers/icon_helpers/effects.py

Provides the ApplyHoverEffects class for dynamically changing button icons on hover and toggle events.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from functools import partial

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractButton


# ── Class Definition ────────────────────────────────────────────────────────────
class ApplyHoverEffects:
    """Provides static methods to wire dynamic hover and toggle icon effects onto buttons.

    Allows swapping between default, hover, and checked icons based on user interaction.
    """

    @staticmethod
    def apply(
        button: QAbstractButton,
        default_icon: QIcon,
        hover_icon:   QIcon,
        checked_icon: QIcon,
    ) -> None:
        """Apply dynamic icon effects to a QAbstractButton.

        Args:
            button (QAbstractButton): The button to which effects are applied.
            default_icon (QIcon): Icon displayed normally.
            hover_icon (QIcon): Icon displayed when the mouse hovers over the button.
            checked_icon (QIcon): Icon displayed when the button is checked.

        Returns:
            None
        """
        button.setMouseTracking(True)

        # ── Wire Hover Events ──
        def on_enter(e, b=button, ic=hover_icon):
            if not b.isChecked(): b.setIcon(ic)
        def on_leave(e, b=button, ic=default_icon):
            if not b.isChecked(): b.setIcon(ic)
        button.enterEvent = partial(on_enter)
        button.leaveEvent = partial(on_leave)

        # ── Wire Toggle Events ──
        button.toggled.connect(lambda chk, b=button, d=default_icon, c=checked_icon:
                               b.setIcon(c if chk else d))
