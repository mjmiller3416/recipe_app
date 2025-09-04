"""app/ui/pages/dashboard/dashboard.py

Placeholder class for the Dashboard screen.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout

from _dev_tools import DebugLogger
from app.style.icon.config import Name, Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.managers.navigation.views import MainView

# ── Dashboard ────────────────────────────────────────────────────────────────────────────────
class Dashboard(MainView):
    """Placeholder class for the Dashboard screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        DebugLogger.log("Initializing Dashboard page", "info")
        self.setObjectName("Dashboard")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Example Card
        card = Card(card_type="Primary")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.expandWidth(False)
        card.setHeader("Dashboard Overview")
        card.setSubHeader("This is a placeholder for dashboard content.")
        summary_label = QLabel("This is a placeholder for dashboard content.")
        summary_label.setProperty("font", "Body")
        summary_label.setWordWrap(True)
        card.addWidget(summary_label)
        self.layout.addWidget(card)


        # add test button with icon
        self.btn = Button(
            label = "Test Button",
            type  = Type.PRIMARY
        )
        self.btn.setIcon(Name.SEARCH)
        self.btn.setIconSize(20, 20)
        self.btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.layout.addWidget(self.btn)

        # Add stretch to push content to top
        self.layout.addStretch()



