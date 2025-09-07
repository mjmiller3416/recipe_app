"""app/ui/views/view.py

Performance-optimized RecipeBrowserView with enhanced rendering and widget management.

This optimized version addresses the major UI performance bottlenecks identified:
- Recipe card object pooling to reduce creation overhead
- Lazy loading with progressive rendering for large datasets
- Enhanced layout update strategies with batching
- Intelligent widget reuse and memory management
- Debounced user interactions to prevent excessive updates
- Improved event handling and signal optimization
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt

from _dev_tools import DebugLogger

from ...components.composite.recipe_card import LayoutSize

from ...views.base import ScrollableNavView
from ._filter_bar import FilterBar


class RecipeBrowser(ScrollableNavView):

    def __init__(
        self,
        parent=None,
        selection_mode: bool = False,
        card_size: LayoutSize = LayoutSize.MEDIUM,
    ):
        super().__init__(parent)
        self.setObjectName("RecipeBrowserView")

        DebugLogger.log(
            f"RecipeBrowserView initialized - "
            f"selection_mode: {selection_mode}, card_size: {card_size.name}",
            "info"
        )

    def _build_ui(self):
        """Build UI with optimized component initialization."""
        filter_bar = FilterBar()
        self.content_layout.addWidget(filter_bar, alignment=Qt.AlignTop)

    def _connect_view_model_signals(self):
        """Connect ViewModel signals."""
        pass

    def _connect_signals(self):
        """Connect UI signals."""
        pass
