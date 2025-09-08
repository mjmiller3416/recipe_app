"""app/ui/views/base.py

Base classes for all views in the application.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


from app.ui.utils.layout_utils import setup_main_scroll_layout

# ── Scrollable Navigation View ──────────────────────────────────────────────────────────────────────────────
class ScrollableNavView(QWidget):
    """Base class for main views with scrollable content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("BaseView")
        self._setup_scroll_layout()

    def _setup_scroll_layout(self):
        """Setup the standard scroll layout - same for all views."""
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

    def _build_ui(self):
        """Override in subclasses to build view-specific content."""
        raise NotImplementedError("Subclasses must implement _build_content")

    def _connect_view_model_signals(self):
        """Override in subclasses if ViewModel signal connections are needed."""
        pass

    def _connect_signals(self):
        """Override in subclasses if signal connections are needed."""
        raise NotImplementedError("Subclasses must implement _connect_signals")

    def setContentLayout(self, layout):
        """Replace the default scroll layout with a custom layout (e.g., FlowLayout)."""
        # Remove the old layout if it exists
        if self.scroll_content.layout():
            QWidget.setLayout(self.scroll_content, None)

        # Set the new layout directly on scroll_content
        self.scroll_content.setLayout(layout)
        self.scroll_layout = layout

    @property
    def content_layout(self):
        return self.scroll_layout
