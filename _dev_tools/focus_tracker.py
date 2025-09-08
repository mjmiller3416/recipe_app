"""app/core/utils/focus_tracker.py

FocusTracker class for tracking and logging focus changes in a PySide6 application.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QWidget
from _dev_tools import DebugLogger


# ── Focus Tracker ────────────────────────────────────────────────────────────────────────────
class FocusTracker(QObject):
    """Tracks and logs focus changes using the application's event system."""

    def __init__(self, parent: QWidget = None):
        """Initializes the FocusTracker and connects to the focusChanged signal.

        Args:
            parent (QWidget, optional): The parent widget for this tracker.
        """
        super().__init__(parent)
        QApplication.instance().focusChanged.connect(self._log_focus_change)

    def _log_focus_change(self, old: QWidget, now: QWidget):
        """Logs the details of the widget that has gained focus.

        Args:
            old (QWidget): The widget that lost focus.
            now (QWidget): The widget that gained focus.
        """
        if not now:
            DebugLogger.log("Focus lost (no widget currently focused).", "debug")
            return

        log_data = {
            f"class": now.__class__.__name__,
            f"object_name": now.objectName() or "⟨no objectName⟩",
            f"geometry": now.geometry().getRect(),
            f"focus_policy": now.focusPolicy(),
            f"has_focus": now.hasFocus(),
        }

        DebugLogger.log(
            (
                "🔍 Focused Widget Changed\n"
                "  🧩 Class: {class}\n"
                "  🔗 Object Name: {object_name}\n"
                "  📐 Geometry: {geometry}\n"
                "  🎯 Focus Policy: {focus_policy}\n"
                "  💡 Has Focus: {has_focus}"
            ),
            "debug",
            **log_data,
        )

        # also log parent hierarchy
        parent_chain = []
        current = now.parent()
        while current:
            parent_chain.append(f"{current.__class__.__name__} ({current.objectName() or 'no objectName'})")
            current = current.parent()

        if parent_chain:
            DebugLogger.log("  🪜 Parent Chain:\n    - " + "\n    - ".join(parent_chain), "debug")
