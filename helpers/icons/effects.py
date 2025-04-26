# core/helpers/icons/effects.py
#🔸Standard Library
from functools import partial

from PySide6.QtGui import QIcon
#🔸Third-party
from PySide6.QtWidgets import QAbstractButton

# ────────────────────────────────────────────────────────────────────────────────


class ApplyHoverEffects:
    """Wire up enter/leave/toggle to swap among three QIcons."""
    @staticmethod
    def apply(
        button: QAbstractButton,
        default_icon: QIcon,
        hover_icon:   QIcon,
        checked_icon: QIcon,
    ) -> None:
        button.setMouseTracking(True)

        def on_enter(e, b=button, ic=hover_icon):
            if not b.isChecked(): b.setIcon(ic)
        def on_leave(e, b=button, ic=default_icon):
            if not b.isChecked(): b.setIcon(ic)
        button.enterEvent = partial(on_enter)
        button.leaveEvent = partial(on_leave)
        button.toggled.connect(lambda chk, b=button, d=default_icon, c=checked_icon:
                               b.setIcon(c if chk else d))