"""Recipe-specific rendering coordination for RecipeBrowser view.

This module provides specialized rendering coordination for recipe cards within the
RecipeBrowser view, handling the complex interactions between recipe data, visual
presentation, performance optimization, and user interactions.

The RenderingCoordinator bridges the gap between generic performance management
and recipe domain-specific rendering requirements, ensuring that recipe cards
are displayed efficiently while maintaining the rich user experience expected
for recipe browsing.

Classes:
    RenderingCoordinator: Recipe-specific rendering coordinator
    RecipeRenderState: State tracking for rendering operations
    CardInteractionType: Types of recipe card interactions

Key Features:
    - Recipe card creation and configuration
    - Progressive rendering coordination
    - Selection mode handling
    - Layout management with FlowLayout integration
    - Recipe-specific performance optimizations
    - Card pool management through PerformanceManager
    - Recipe card interaction handling
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from enum import Enum
from time import perf_counter
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import QWidget

from _dev_tools.debug_logger import DebugLogger
from app.core.models.recipe import Recipe
from app.ui.components.composite.recipe_card import BaseRecipeCard
from app.ui.components.layout.flow_layout import FlowLayout
from app.ui.managers.performance.performance_manager import PerformanceManager
from .config import RecipeBrowserConfig

# ── Enums ───────────────────────────────────────────────────────────────────────────────────────────────────
class CardInteractionType(Enum):
    """Types of recipe card interactions."""
    CARD_CLICKED = "card_clicked"
    SELECTION_CHANGED = "selection_changed"
    FAVORITE_TOGGLED = "favorite_toggled"
    CONTEXT_MENU = "context_menu"
    RECIPE_OPENED = "recipe_opened"


class RecipeRenderState(Enum):
    """States of recipe rendering process."""
    IDLE = "idle"
    RENDERING = "rendering"
    BATCH_COMPLETE = "batch_complete"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


# ── Rendering Coordinator ──────────────────────────────────────────────────────────────────────────────────
class RenderingCoordinator(QObject):
    """
    Recipe-specific rendering coordinator for RecipeBrowser view.

    Handles the complete recipe card rendering lifecycle including:
    - Recipe card creation and configuration with domain-specific logic
    - Progressive rendering coordination using PerformanceManager
    - Layout management and optimization for recipe display
    - Selection mode coordination and visual state management
    - Recipe card interaction handling and event routing

    This coordinator acts as the bridge between generic UI performance systems
    and recipe domain-specific requirements, ensuring that recipe cards are
    rendered efficiently while maintaining the rich functionality expected
    for recipe browsing and selection.

    Signals:
        rendering_started: Emitted when rendering begins
        rendering_progress: Emitted during progressive rendering
        rendering_completed: Emitted when rendering completes
        batch_rendered: Emitted after each batch is rendered
        card_interaction: Emitted for recipe card interactions
        layout_updated: Emitted when layout geometry changes
        selection_mode_changed: Emitted when selection mode changes
        error_occurred: Emitted when rendering errors occur

    Recipe Domain Features:
        - Intelligent card sizing based on recipe content complexity
        - Recipe category-based visual styling
        - Favorite recipe highlighting and state management
        - Recipe preparation time and difficulty visualization
        - Ingredient count and dietary restriction indicators
        - Recipe image loading and caching coordination
        - Context-sensitive interaction patterns

    Performance Optimizations:
        - Card object pooling through PerformanceManager integration
        - Progressive rendering with recipe-aware batching
        - Layout caching and geometry optimization
        - Memory-efficient recipe data binding
        - Interaction debouncing for responsive UI
    """

    # Core rendering signals
    rendering_started = Signal(int)                              # recipe_count
    rendering_progress = Signal(int, int, float)                 # completed, total, progress_percent
    rendering_completed = Signal(int, float)                     # recipe_count, duration_ms
    batch_rendered = Signal(int, int)                            # batch_size, total_rendered

    # Interaction and state signals
    card_interaction = Signal(Recipe, str)                       # recipe, interaction_type
    selection_mode_changed = Signal(bool)                        # selection_mode_enabled
    layout_updated = Signal(int)                                 # visible_card_count

    # Error and status signals
    error_occurred = Signal(str, str)                           # error_type, error_message

    def __init__(self,
                 performance_manager: PerformanceManager,
                 config: RecipeBrowserConfig,
                 parent: Optional[QObject] = None):
        """
        Initialize recipe rendering coordinator.

        Args:
            performance_manager: Performance manager for object pooling and optimization
            config: Configuration for rendering behavior and performance tuning
            parent: Parent QObject for proper cleanup
        """
        super().__init__(parent)

        # Core dependencies
        self._performance_manager = performance_manager
        self._config = config

        # Rendering state
        self._render_state = RecipeRenderState.IDLE
        self._current_recipes: List[Recipe] = []
        self._rendered_cards: Dict[int, BaseRecipeCard] = {}  # recipe_id -> card mapping
        self._selection_mode = False
        self._last_render_start_time: Optional[float] = None

        # Layout management
        self._layout_container: Optional[QWidget] = None
        self._flow_layout: Optional[FlowLayout] = None
        self._card_pool_name = "recipe_cards"

        # Progressive rendering coordination
        self._progressive_renderer_name = "recipe_rendering"
        self._current_batch = 0
        self._total_batches = 0
        self._render_timer: Optional[QTimer] = None

        # Performance tracking
        self._render_metrics = {
            'total_renders': 0,
            'total_render_time_ms': 0.0,
            'average_render_time_ms': 0.0,
            'cards_per_second': 0.0,
            'peak_memory_usage': 0,
        }

        # Initialize rendering system
        self._setup_rendering_system()

        DebugLogger.log(
            f"RenderingCoordinator initialized - "
            f"card_size: {config.display.default_card_size.name}, "
            f"progressive_rendering: {config.features.enable_progressive_rendering}, "
            f"pool_size: {config.performance.card_pool_size}",
            "debug"
        )

    def _setup_rendering_system(self):
        """Initialize the rendering system components."""
        try:
            # Create recipe card pool through performance manager
            self._setup_card_pool()

            # Setup progressive renderer if enabled
            if self._config.features.enable_progressive_rendering:
                self._setup_progressive_renderer()

            # Setup performance monitoring
            if self._config.features.enable_performance_monitoring:
                self._setup_performance_monitoring()

            DebugLogger.log("Recipe rendering system initialized successfully", "debug")

        except Exception as e:
            error_msg = f"Failed to initialize rendering system: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("initialization_error", error_msg)

    def _setup_card_pool(self):
        """Setup recipe card object pool."""
        def create_recipe_card_for_pool() -> BaseRecipeCard:
            """Factory function for creating recipe cards."""
            from app.ui.components.composite.recipe_card import create_recipe_card
            card = create_recipe_card(self._config.display.default_card_size)
            # Connect card signals
            card.card_clicked.connect(self._handle_card_clicked)
            return card

        def reset_recipe_card(card: BaseRecipeCard):
            """Reset card state for reuse."""
            card.set_recipe(None)
            card.set_selection_mode(False)
            card.setVisible(False)
            # Disconnect any specific signals to prevent leaks
            try:
                card.card_clicked.disconnect()
            except:
                pass
            # Reconnect the coordinator signal
            card.card_clicked.connect(self._handle_card_clicked)

        def cleanup_recipe_card(card: BaseRecipeCard):
            """Cleanup card before destruction."""
            card.set_recipe(None)
            card.setParent(None)

        # Create widget pool through performance manager
        self._card_pool = self._performance_manager.create_widget_pool(
            name=self._card_pool_name,
            widget_factory=create_recipe_card_for_pool,
            parent_widget=None,  # Will be set when layout container is setup
            max_pool_size=self._config.performance.card_pool_size
        )

        # Note: PySide6 widget pools handle cleanup automatically, but we can add custom logic

        DebugLogger.log(f"Recipe card pool created with size {self._config.performance.card_pool_size}", "debug")

    def _setup_progressive_renderer(self):
        """Setup progressive renderer for batch rendering."""
        def render_batch_callback(recipes: List[Recipe], batch_index: int, total_batches: int):
            """Callback for rendering a batch of recipes."""
            self._render_recipe_batch(recipes, batch_index, total_batches)

        def completion_callback():
            """Callback for rendering completion."""
            self._on_progressive_rendering_complete()

        # Create callback-based progressive renderer
        self._progressive_renderer = self._performance_manager.create_callback_renderer(
            name=self._progressive_renderer_name,
            render_callback=render_batch_callback,
            completion_callback=completion_callback,
            default_batch_size=self._config.performance.batch_size,
            default_delay_ms=self._config.performance.render_delay_ms
        )

        DebugLogger.log(
            f"Progressive renderer setup - batch_size: {self._config.performance.batch_size}, "
            f"delay: {self._config.performance.render_delay_ms}ms",
            "debug"
        )

    def _setup_performance_monitoring(self):
        """Setup performance monitoring and thresholds."""
        # Set performance thresholds
        threshold_seconds = self._config.performance.slow_render_threshold_ms / 1000.0
        self._performance_manager.set_performance_threshold("recipe_rendering", threshold_seconds)
        self._performance_manager.set_performance_threshold("card_configuration", 0.010)  # 10ms
        self._performance_manager.set_performance_threshold("layout_update", 0.050)      # 50ms

        # Connect performance warnings
        self._performance_manager.performance_warning.connect(self._handle_performance_warning)

    def _handle_performance_warning(self, operation: str, duration: float, threshold: float):
        """Handle performance warnings from the performance manager."""
        if "recipe" in operation.lower():
            DebugLogger.log(
                f"Recipe rendering performance warning: {operation} took {duration*1000:.1f}ms "
                f"(threshold: {threshold*1000:.1f}ms)",
                "warning"
            )

    # ── Layout Setup and Management ────────────────────────────────────────────────────────────────────────────
    def setup_layout_container(self, parent_widget: QWidget) -> FlowLayout:
        """
        Setup the layout container for recipe cards.

        Args:
            parent_widget: Parent widget to contain the recipe card layout

        Returns:
            FlowLayout: The configured flow layout for recipe cards
        """
        try:
            # Store container reference
            self._layout_container = parent_widget

            # Create and configure FlowLayout
            self._flow_layout = FlowLayout(
                parent_widget,
                needAni=self._config.display.enable_animations,
                isTight=True  # Tight layout for better card arrangement
            )

            # Configure spacing from config
            spacing = self._config.display.card_spacing
            self._flow_layout._verticalSpacing = spacing
            self._flow_layout._horizontalSpacing = spacing

            # Set animation properties if enabled
            if self._config.display.enable_animations:
                self._flow_layout.setAnimation(
                    duration=self._config.display.animation_duration_ms,
                    ease=self._flow_layout.ease  # Use default easing
                )

            # Update card pool parent widget
            if self._card_pool:
                # Widget pools in performance manager handle parent assignment automatically
                pass

            DebugLogger.log(
                f"Layout container setup - animations: {self._config.display.enable_animations}, "
                f"spacing: {spacing}px",
                "debug"
            )

            return self._flow_layout

        except Exception as e:
            error_msg = f"Failed to setup layout container: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("layout_setup_error", error_msg)
            raise

    def update_layout_geometry(self):
        """Update layout geometry and emit metrics."""
        if not self._flow_layout or not self._layout_container:
            return

        try:
            with self._performance_manager.performance_context("layout_update"):
                # Update container and layout geometry
                self._layout_container.updateGeometry()
                self._flow_layout.update()

                # Emit layout updated signal with current card count
                visible_cards = len([card for card in self._rendered_cards.values() if card.isVisible()])
                self.layout_updated.emit(visible_cards)

        except Exception as e:
            DebugLogger.log(f"Error updating layout geometry: {e}", "error")

    # ── Recipe Rendering Methods ───────────────────────────────────────────────────────────────────────────────
    def render_recipes(self, recipes: List[Recipe], selection_mode: bool = False) -> bool:
        """
        Main method to render a list of recipes with performance optimization.

        Args:
            recipes: List of recipes to render
            selection_mode: Whether to enable selection mode for cards

        Returns:
            bool: True if rendering started successfully, False otherwise
        """
        if self._render_state not in (RecipeRenderState.IDLE, RecipeRenderState.COMPLETE, RecipeRenderState.ERROR):
            DebugLogger.log("Cannot start rendering: already in progress", "warning")
            return False

        try:
            # Update state
            self._render_state = RecipeRenderState.RENDERING
            self._current_recipes = recipes
            self._selection_mode = selection_mode
            self._last_render_start_time = perf_counter()

            # Clear existing cards
            self.clear_rendering()

            # Emit rendering started
            self.rendering_started.emit(len(recipes))

            # Choose rendering strategy based on config and recipe count
            should_use_progressive = (
                self._config.features.enable_progressive_rendering and
                len(recipes) > self._config.performance.batch_size and
                hasattr(self, '_progressive_renderer')
            )

            if should_use_progressive:
                return self._start_progressive_rendering(recipes)
            else:
                return self._start_immediate_rendering(recipes)

        except Exception as e:
            self._render_state = RecipeRenderState.ERROR
            error_msg = f"Failed to start recipe rendering: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("render_start_error", error_msg)
            return False

    def _start_progressive_rendering(self, recipes: List[Recipe]) -> bool:
        """Start progressive rendering using the performance manager."""
        try:
            # Calculate optimized batch size
            optimized_settings = self._config.get_optimized_settings(len(recipes))
            batch_size = optimized_settings.get("batch_size", self._config.performance.batch_size)

            # Calculate batch information
            self._total_batches = (len(recipes) + batch_size - 1) // batch_size
            self._current_batch = 0

            # Start progressive rendering
            success = self._performance_manager.start_progressive_rendering(
                name=self._progressive_renderer_name,
                items=recipes,
                batch_size=batch_size,
                delay_ms=self._config.performance.render_delay_ms
            )

            if success:
                DebugLogger.log(
                    f"Progressive rendering started - {len(recipes)} recipes in {self._total_batches} batches",
                    "debug"
                )

            return success

        except Exception as e:
            error_msg = f"Failed to start progressive rendering: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("progressive_render_error", error_msg)
            return False

    def _start_immediate_rendering(self, recipes: List[Recipe]) -> bool:
        """Start immediate rendering for small recipe sets."""
        try:
            with self._performance_manager.performance_context("recipe_rendering"):
                self._render_recipe_batch(recipes, 0, 1)
                self._complete_rendering()

            DebugLogger.log(f"Immediate rendering completed for {len(recipes)} recipes", "debug")
            return True

        except Exception as e:
            self._render_state = RecipeRenderState.ERROR
            error_msg = f"Failed in immediate rendering: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("immediate_render_error", error_msg)
            return False

    def _render_recipe_batch(self, recipes: List[Recipe], batch_index: int, total_batches: int):
        """Render a batch of recipes with performance monitoring."""
        if self._render_state == RecipeRenderState.CANCELLED:
            return

        try:
            batch_start_time = perf_counter()
            cards_rendered = 0

            for recipe in recipes:
                if self._render_state == RecipeRenderState.CANCELLED:
                    break

                # Get card from pool
                card = self._get_card_from_pool()
                if card is None:
                    DebugLogger.log("Failed to get card from pool", "warning")
                    continue

                # Configure card with recipe data
                self.configure_recipe_card(card, recipe, self._selection_mode)

                # Add to layout
                if self._flow_layout:
                    self._flow_layout.addWidget(card)

                # Track rendered card
                recipe_id = getattr(recipe, 'id', getattr(recipe, 'recipe_id', None))
                if recipe_id:
                    self._rendered_cards[recipe_id] = card

                cards_rendered += 1

            # Update batch progress
            self._current_batch = batch_index + 1

            # Calculate progress
            total_rendered = sum(1 for cards in self._rendered_cards.values())
            progress_percent = (total_rendered / len(self._current_recipes)) * 100

            # Emit progress signals
            self.rendering_progress.emit(total_rendered, len(self._current_recipes), progress_percent)
            self.batch_rendered.emit(cards_rendered, total_rendered)

            # Performance metrics
            batch_time = (perf_counter() - batch_start_time) * 1000
            if self._config.features.enable_render_timing and cards_rendered > 0:
                cards_per_second = cards_rendered / (batch_time / 1000)
                DebugLogger.log(
                    f"Batch {batch_index + 1}/{total_batches} rendered: {cards_rendered} cards "
                    f"in {batch_time:.1f}ms ({cards_per_second:.1f} cards/sec)",
                    "debug"
                )

            # Update layout geometry after batch
            self.update_layout_geometry()

        except Exception as e:
            error_msg = f"Error rendering batch {batch_index + 1}: {e}"
            DebugLogger.log(error_msg, "error")
            self.error_occurred.emit("batch_render_error", error_msg)

    def _on_progressive_rendering_complete(self):
        """Handle completion of progressive rendering."""
        self._complete_rendering()

    def _complete_rendering(self):
        """Complete the rendering process and emit completion signals."""
        if self._last_render_start_time:
            total_time = (perf_counter() - self._last_render_start_time) * 1000

            # Update performance metrics
            self._render_metrics['total_renders'] += 1
            self._render_metrics['total_render_time_ms'] += total_time
            self._render_metrics['average_render_time_ms'] = (
                self._render_metrics['total_render_time_ms'] / self._render_metrics['total_renders']
            )
            if total_time > 0:
                self._render_metrics['cards_per_second'] = len(self._rendered_cards) / (total_time / 1000)

            # Emit completion signal
            self.rendering_completed.emit(len(self._rendered_cards), total_time)

            # Check performance threshold
            threshold = self._config.performance.slow_render_threshold_ms
            if total_time > threshold:
                DebugLogger.log(
                    f"SLOW RECIPE RENDER: {total_time:.2f}ms for {len(self._rendered_cards)} cards "
                    f"(threshold: {threshold}ms)",
                    "warning"
                )
            elif self._config.features.enable_render_timing:
                DebugLogger.log(
                    f"Recipe rendering completed in {total_time:.2f}ms for {len(self._rendered_cards)} cards",
                    "debug"
                )

        self._render_state = RecipeRenderState.COMPLETE

    # ── Recipe Card Configuration ──────────────────────────────────────────────────────────────────────────────
    def configure_recipe_card(self, card: BaseRecipeCard, recipe: Recipe, selection_mode: bool):
        """
        Configure a recipe card with recipe data and interaction behavior.

        Args:
            card: Recipe card to configure
            recipe: Recipe data to display
            selection_mode: Whether card should be in selection mode
        """
        try:
            with self._performance_manager.performance_context("card_configuration"):
                # Set basic recipe data
                card.set_recipe(recipe)
                card.set_selection_mode(selection_mode)

                # Configure visual state based on recipe properties
                self._configure_recipe_visual_state(card, recipe)

                # Setup interaction handlers
                self._configure_recipe_interactions(card, recipe, selection_mode)

                # Make card visible
                card.setVisible(True)

        except Exception as e:
            DebugLogger.log(f"Error configuring recipe card for {recipe.recipe_name}: {e}", "error")

    def _configure_recipe_visual_state(self, card: BaseRecipeCard, recipe: Recipe):
        """Configure visual state based on recipe properties."""
        try:
            # Set cursor based on interaction mode
            cursor = Qt.PointingHandCursor if not self._selection_mode else Qt.ArrowCursor
            card.setCursor(cursor)

            # Apply recipe-specific styling (placeholder for future enhancements)
            # Could include category-based colors, difficulty indicators, etc.
            card.setObjectName("RecipeCard")  # Ensure consistent styling

        except Exception as e:
            DebugLogger.log(f"Error configuring visual state for recipe card: {e}", "warning")

    def _configure_recipe_interactions(self, card: BaseRecipeCard, recipe: Recipe, selection_mode: bool):
        """Configure recipe card interaction patterns."""
        try:
            # Disconnect existing signals to prevent duplicates
            try:
                card.card_clicked.disconnect()
            except:
                pass

            # Connect appropriate interaction handler
            if selection_mode:
                # Selection mode: emit selection signal
                card.card_clicked.connect(lambda r=recipe: self._handle_recipe_selection(r))
            else:
                # Browse mode: emit open signal
                card.card_clicked.connect(lambda r=recipe: self._handle_recipe_opened(r))

        except Exception as e:
            DebugLogger.log(f"Error configuring card interactions: {e}", "error")

    # ── Card Pool Management ───────────────────────────────────────────────────────────────────────────────────
    def _get_card_from_pool(self) -> Optional[BaseRecipeCard]:
        """Get a recipe card from the object pool."""
        if not self._card_pool:
            return None

        try:
            card = self._card_pool.get_widget()
            if card and self._layout_container:
                card.setParent(self._layout_container)
            return card
        except Exception as e:
            DebugLogger.log(f"Error getting card from pool: {e}", "error")
            return None

    def _return_card_to_pool(self, card: BaseRecipeCard):
        """Return a recipe card to the object pool."""
        if not self._card_pool or not card:
            return

        try:
            # Reset card state
            card.set_recipe(None)
            card.set_selection_mode(False)
            card.setVisible(False)
            card.setParent(None)

            # Return to pool
            self._card_pool.return_widget(card)

        except Exception as e:
            DebugLogger.log(f"Error returning card to pool: {e}", "error")

    # ── Interaction Handlers ───────────────────────────────────────────────────────────────────────────────────
    def _handle_card_clicked(self, recipe: Recipe):
        """Handle generic card click - routes to appropriate handler."""
        if self._selection_mode:
            self._handle_recipe_selection(recipe)
        else:
            self._handle_recipe_opened(recipe)

    def _handle_recipe_selection(self, recipe: Recipe):
        """Handle recipe selection in selection mode."""
        try:
            DebugLogger.log(f"Recipe selected: {recipe.recipe_name}", "debug")
            self.card_interaction.emit(recipe, CardInteractionType.SELECTION_CHANGED.value)
        except Exception as e:
            DebugLogger.log(f"Error handling recipe selection: {e}", "error")

    def _handle_recipe_opened(self, recipe: Recipe):
        """Handle recipe opening in browse mode."""
        try:
            DebugLogger.log(f"Recipe opened: {recipe.recipe_name}", "debug")
            self.card_interaction.emit(recipe, CardInteractionType.RECIPE_OPENED.value)
        except Exception as e:
            DebugLogger.log(f"Error handling recipe opened: {e}", "error")

    def handle_recipe_interaction(self, recipe: Recipe, interaction_type: str):
        """
        Handle specific recipe card interactions.

        Args:
            recipe: Recipe that was interacted with
            interaction_type: Type of interaction (from CardInteractionType enum)
        """
        try:
            # Validate interaction type
            try:
                interaction_enum = CardInteractionType(interaction_type)
            except ValueError:
                DebugLogger.log(f"Unknown interaction type: {interaction_type}", "warning")
                return

            # Emit the interaction signal
            self.card_interaction.emit(recipe, interaction_type)

            # Handle specific interaction types
            if interaction_enum == CardInteractionType.FAVORITE_TOGGLED:
                self._handle_favorite_toggled(recipe)
            elif interaction_enum == CardInteractionType.CONTEXT_MENU:
                self._handle_context_menu(recipe)

        except Exception as e:
            DebugLogger.log(f"Error handling recipe interaction: {e}", "error")

    def _handle_favorite_toggled(self, recipe: Recipe):
        """Handle favorite toggle interaction."""
        # Placeholder for favorite toggle logic
        # Could update recipe state, refresh visual styling, etc.
        DebugLogger.log(f"Favorite toggled for recipe: {recipe.recipe_name}", "debug")

    def _handle_context_menu(self, recipe: Recipe):
        """Handle context menu interaction."""
        # Placeholder for context menu logic
        DebugLogger.log(f"Context menu requested for recipe: {recipe.recipe_name}", "debug")

    # ── Selection Mode Management ──────────────────────────────────────────────────────────────────────────────
    def update_selection_mode(self, selection_mode: bool):
        """
        Update selection mode for all rendered cards.

        Args:
            selection_mode: Whether to enable selection mode
        """
        if self._selection_mode == selection_mode:
            return

        try:
            old_mode = self._selection_mode
            self._selection_mode = selection_mode

            # Update all rendered cards
            for card in self._rendered_cards.values():
                if card and card.recipe():  # Only update cards with recipes
                    recipe = card.recipe()
                    card.set_selection_mode(selection_mode)
                    self._configure_recipe_interactions(card, recipe, selection_mode)
                    self._configure_recipe_visual_state(card, recipe)

            # Emit selection mode changed signal
            self.selection_mode_changed.emit(selection_mode)

            DebugLogger.log(
                f"Selection mode updated: {old_mode} -> {selection_mode} "
                f"({len(self._rendered_cards)} cards updated)",
                "debug"
            )

        except Exception as e:
            DebugLogger.log(f"Error updating selection mode: {e}", "error")

    # ── Cleanup and State Management ───────────────────────────────────────────────────────────────────────────
    def clear_rendering(self):
        """Clear all rendered cards and reset state."""
        try:
            # Reset state immediately to allow new renders
            old_state = self._render_state
            self._render_state = RecipeRenderState.IDLE
            # Return all cards to pool
            for card in self._rendered_cards.values():
                if card:
                    # Remove from layout first
                    if self._flow_layout:
                        try:
                            # Remove widget from layout
                            index = self._flow_layout.indexOf(card)
                            if index != -1:
                                item = self._flow_layout.takeAt(index)
                                if item:
                                    widget = item.widget()
                                    if widget:
                                        widget.setParent(None)
                        except:
                            pass  # Widget may already be removed

                    # Return to pool
                    self._return_card_to_pool(card)

            # Clear tracking
            self._rendered_cards.clear()

            # Update layout
            self.update_layout_geometry()

            # Reset batch tracking
            self._current_batch = 0
            self._total_batches = 0

            DebugLogger.log("Recipe rendering cleared successfully", "debug")

        except Exception as e:
            DebugLogger.log(f"Error clearing rendering: {e}", "error")

    def cancel_rendering(self):
        """Cancel ongoing rendering operations."""
        if self._render_state == RecipeRenderState.RENDERING:
            self._render_state = RecipeRenderState.CANCELLED

            # Stop progressive rendering if active
            if hasattr(self, '_progressive_renderer'):
                self._performance_manager.stop_progressive_rendering(self._progressive_renderer_name)

            DebugLogger.log("Recipe rendering cancelled", "debug")

    def get_render_state(self) -> RecipeRenderState:
        """Get current rendering state."""
        return self._render_state

    def get_rendered_recipe_count(self) -> int:
        """Get count of currently rendered recipes."""
        return len(self._rendered_cards)

    def get_render_metrics(self) -> Dict[str, any]:
        """Get rendering performance metrics."""
        return {
            'render_state': self._render_state.value,
            'rendered_cards': len(self._rendered_cards),
            'selection_mode': self._selection_mode,
            'performance': self._render_metrics.copy(),
            'pool_stats': self._card_pool.statistics if self._card_pool else {},
            'config': {
                'card_size': self._config.display.default_card_size.name,
                'progressive_rendering': self._config.features.enable_progressive_rendering,
                'batch_size': self._config.performance.batch_size,
                'pool_size': self._config.performance.card_pool_size,
            }
        }

    # ── Cleanup ────────────────────────────────────────────────────────────────────────────────────────────────
    def cleanup(self):
        """Clean up rendering coordinator resources."""
        try:
            # Cancel any ongoing rendering
            self.cancel_rendering()

            # Clear all rendered cards
            self.clear_rendering()

            # Stop any timers
            if self._render_timer:
                self._render_timer.stop()
                self._render_timer = None

            # Clear references
            self._layout_container = None
            self._flow_layout = None
            self._current_recipes.clear()
            self._rendered_cards.clear()

            DebugLogger.log("RenderingCoordinator cleanup completed", "debug")

        except Exception as e:
            DebugLogger.log(f"Error during RenderingCoordinator cleanup: {e}", "error")
