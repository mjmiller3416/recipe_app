"""app/ui/pages/dashboard/dashboard.py

Placeholder class for the Dashboard screen.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from app.core.dev_tools import DebugLogger, StartupTimer


# ── Class Definition ────────────────────────────────────────────────────────────
class Dashboard(QWidget):
    """Placeholder class for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)

        DebugLogger.log("Initializing Dashboard page", "debug")

        # Initialize & Setup UI
        self.setObjectName("Dashboard")

        self.setObjectName("Dashboard")
        self.setMinimumSize(984, 818)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  

