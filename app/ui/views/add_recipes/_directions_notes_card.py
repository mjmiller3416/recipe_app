"""app/ui/views/add_recipes/_directions_notes_card.py

This module defines the DirectionsNotesCard class, which provides a card layout
with toggle buttons to switch between Directions and Notes text areas.
"""

# ── Imports ──
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QWidget
from app.style import Type
from app.ui.components.layout.card import Card
from app.ui.components.widgets.button import Button
from app.ui.utils import global_signals

# ── Constants ──
TAB_HEIGHT = 60 # Height of the toggle button tabs

class DirectionsNotesCard(Card):
    """Custom card with toggle between Directions and Notes content."""

    def __init__(self, parent=None):
        super().__init__(card_type="Default")
        self.setHeader("Directions & Notes")
        self.setMinimumHeight(600)  # set minimum height to ensure enough space for content

        # Create toggle buttons container
        self.toggle_container = QWidget()
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(10)

        # Create toggle b2uttons using custom Button class
        self.btn_directions = Button("Directions", Type.PRIMARY)
        self.btn_notes = Button("Notes", Type.SECONDARY)
        self.btn_directions.setFixedHeight(TAB_HEIGHT)
        self.btn_notes.setFixedHeight(TAB_HEIGHT)


        # Set object names for styling
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")

        # Add buttons to toggle layout
        toggle_layout.addWidget(self.btn_directions)
        toggle_layout.addWidget(self.btn_notes)

        # Create content areas
        self.te_directions = QTextEdit()
        self.te_directions.setObjectName("DirectionsTextEdit")
        self.te_directions.setPlaceholderText("Enter cooking directions here...")

        self.te_notes = QTextEdit()
        self.te_notes.setObjectName("NotesTextEdit")
        self.te_notes.setPlaceholderText("Add any additional notes here...")

        # Add components to card
        self.addWidget(self.toggle_container)
        self.addWidget(self.te_directions)
        self.addWidget(self.te_notes)

        # Initially show directions, hide notes
        self.te_notes.hide()

        # Connect signals
        self.btn_directions.clicked.connect(self.show_directions)
        self.btn_notes.clicked.connect(self.show_notes)

        # Setup auto-scroll signals for text edits
        self._setup_auto_scroll_signals()

    def show_directions(self):
        """Show directions content and update button states."""
        self.te_directions.show()
        self.te_notes.hide()
        self.btn_directions.setObjectName("ToggleButtonActive")
        self.btn_notes.setObjectName("ToggleButtonInactive")
        self._refresh_button_styles()

    def show_notes(self):
        """Show notes content and update button states."""
        self.te_directions.hide()
        self.te_notes.show()
        self.btn_directions.setObjectName("ToggleButtonInactive")
        self.btn_notes.setObjectName("ToggleButtonActive")
        self._refresh_button_styles()

    def _refresh_button_styles(self):
        """Force refresh of button styles after state change."""
        for btn in [self.btn_directions, self.btn_notes]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _setup_auto_scroll_signals(self):
        """Setup focus event handling for auto-scroll functionality."""
        # Install event filters on both text edits
        self.te_directions.installEventFilter(self)
        self.te_notes.installEventFilter(self)

    def eventFilter(self, watched, event):
        """Handle focus events for auto-scroll functionality."""
        from _dev_tools import DebugLogger

        if (watched in [self.te_directions, self.te_notes] and
            event.type() == QEvent.FocusIn):
            DebugLogger.log(f"[DirectionsNotesCard] Text edit focused, emitting scroll-to-bottom signal", "debug")
            global_signals.scroll_to_bottom_requested.emit()

        return super().eventFilter(watched, event)
