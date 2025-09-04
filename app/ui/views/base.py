"""app/ui/views/base.py

Base classes for all views in the application.
"""


# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from app.ui.services.navigation.views import MainView
from app.ui.utils.layout_utils import setup_main_scroll_layout


# ── Scrollable View ─────────────────────────────────────────────────────────────────────────────────────────
class ScrollableView(MainView):
    """Base class for main views with scrollable content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_scroll_layout()
        self._build_ui()
        self._connect_signals()

    def _setup_scroll_layout(self):
        """Setup the standard scroll layout - same for all views."""
        self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
            setup_main_scroll_layout(self)

    def _build_ui(self):
        """Override in subclasses to build view-specific content."""
        raise NotImplementedError("Subclasses must implement _build_content")

    def _connect_signals(self):
        """Override in subclasses if signal connections are needed."""
        pass

    @property
    def content_layout(self):
        return self.scroll_layout
