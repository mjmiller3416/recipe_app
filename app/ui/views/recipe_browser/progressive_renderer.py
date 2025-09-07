"""app/ui/views/recipe_browser/progressive_renderer.py

Progressive rendering of recipe cards to enhance perceived performance.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import weakref
from typing import List

from PySide6.QtCore import QTimer

from _dev_tools.debug_logger import DebugLogger
from app.core.models.recipe import Recipe

class ProgressiveRenderer:
    """Progressive recipe rendering to improve perceived performance."""

    def __init__(self, parent_view):
        self.parent_view = weakref.ref(parent_view)
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._render_next_batch)

        self.pending_recipes: List[Recipe] = []
        self.batch_size = 5  # Render 5 cards at a time
        self.render_delay = 10  # 10ms between batches

    def start_progressive_render(self, recipes: List[Recipe], batch_size: int = 5):
        """Start progressive rendering of recipe cards."""
        self.pending_recipes = recipes.copy()
        self.batch_size = batch_size

        DebugLogger.log(f"Starting progressive render of {len(recipes)} recipes", "debug")

        # Start rendering
        self.render_timer.start(self.render_delay)

    def _render_next_batch(self):
        """Render the next batch of recipe cards."""
        view = self.parent_view()
        if not view or not self.pending_recipes:
            self.render_timer.stop()
            return

        # Render next batch
        batch_count = min(self.batch_size, len(self.pending_recipes))
        current_batch = []

        for _ in range(batch_count):
            if self.pending_recipes:
                recipe = self.pending_recipes.pop(0)
                current_batch.append(recipe)

        # Render this batch
        view._render_recipe_batch(current_batch)

        # Continue if more recipes pending
        if self.pending_recipes:
            DebugLogger.log(f"Rendered batch of {len(current_batch)}, {len(self.pending_recipes)} remaining", "debug")
        else:
            self.render_timer.stop()
            view._on_progressive_render_complete()
            DebugLogger.log("Progressive rendering completed", "debug")

    def stop_rendering(self):
        """Stop progressive rendering."""
        self.render_timer.stop()
        self.pending_recipes.clear()
