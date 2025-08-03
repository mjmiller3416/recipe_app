"""app/ui/pages/dashboard/dashboard.py

Placeholder class for the Dashboard screen.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from dev_tools import DebugLogger, StartupTimer
from app.ui.components.layout.card import Card
from app.ui.components.inputs import SmartLineEdit


# ── Class Definition ────────────────────────────────────────────────────────────
class Dashboard(QWidget):
    """Placeholder class for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)

        DebugLogger.log("Initializing Dashboard page", "debug")

        # Initialize & Setup UI
        self.setObjectName("Dashboard")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Example Card
        card = Card(header="Dashboard Overview", subheader="Summary of key metrics")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setSpacing(36)
        summary_label = QLabel("This is a placeholder for dashboard content.")
        summary_label.setProperty("font", "Body")
        summary_label.setWordWrap(True)
        card.content_area.addWidget(summary_label)
        self.layout.addWidget(card)

        # Add stretch to push content to top
        self.layout.addStretch()



