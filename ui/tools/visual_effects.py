"""ui.tools.visual_effects.py

Module to create visual effects for widgets.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

# ── Public Methods ──────────────────────────────────────────────────────────────
@staticmethod
def shadow_effect(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(80)  # exaggerated for testing
    shadow.setXOffset(20)
    shadow.setYOffset(20)
    shadow.setColor(QColor(255, 0, 0, 160))  # bright red shadow for visibility
    widget.setGraphicsEffect(shadow)