"""app/ui/managers/performance/progressive_renderer.py

Generic progressive rendering system for improved perceived performance.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Generic, List, Optional, TypeVar

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import weakref

from PySide6.QtCore import QObject, QTimer, Signal

from _dev_tools.debug_logger import DebugLogger

# ── Type Variables ─────────────────────────────────────────────────────────────────────────────────────────
T = TypeVar('T')


# ── Enums ──────────────────────────────────────────────────────────────────────────────────────────────────
class RenderState(Enum):
    """Progressive rendering states."""
    IDLE = "idle"
    RENDERING = "rendering" 
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ── Interfaces ─────────────────────────────────────────────────────────────────────────────────────────────
class ProgressiveRenderTarget(ABC):
    """Interface for objects that can handle progressive rendering."""
    
    @abstractmethod
    def render_batch(self, items: List[Any], batch_index: int, total_batches: int):
        """
        Render a batch of items.
        
        Args:
            items: Items to render in this batch
            batch_index: Index of current batch (0-based)
            total_batches: Total number of batches
        """
        pass
    
    @abstractmethod
    def on_render_complete(self):
        """Called when progressive rendering completes."""
        pass
    
    def on_render_started(self, total_items: int, total_batches: int):
        """Called when progressive rendering starts."""
        pass
    
    def on_batch_complete(self, batch_index: int, total_batches: int):
        """Called when a batch completes."""
        pass


# ── Progressive Renderer ───────────────────────────────────────────────────────────────────────────────────
class ProgressiveRenderer(Generic[T], QObject):
    """
    Generic progressive renderer for improved perceived performance.
    
    Signals:
        rendering_started: Emitted when rendering starts (total_items, total_batches)
        batch_rendered: Emitted when a batch is rendered (batch_index, batch_size)
        rendering_progress: Emitted with progress updates (completed, total, percentage)
        rendering_completed: Emitted when rendering completes
        rendering_cancelled: Emitted when rendering is cancelled
        rendering_paused: Emitted when rendering is paused
        rendering_resumed: Emitted when rendering is resumed
    """
    
    # Signals
    rendering_started = Signal(int, int)    # total_items, total_batches
    batch_rendered = Signal(int, int)       # batch_index, batch_size
    rendering_progress = Signal(int, int, float)  # completed, total, percentage
    rendering_completed = Signal()
    rendering_cancelled = Signal()
    rendering_paused = Signal()
    rendering_resumed = Signal()
    
    def __init__(
        self,
        target: ProgressiveRenderTarget,
        default_batch_size: int = 5,
        default_delay_ms: int = 10
    ):
        """
        Initialize progressive renderer.
        
        Args:
            target: Target object that handles rendering
            default_batch_size: Default number of items per batch
            default_delay_ms: Default delay between batches in milliseconds
        """
        super().__init__()
        
        self._target = weakref.ref(target) if target else None
        self._default_batch_size = default_batch_size
        self._default_delay_ms = default_delay_ms
        
        # Rendering state
        self._state = RenderState.IDLE
        self._pending_items: List[T] = []
        self._current_batch_index = 0
        self._total_batches = 0
        self._batch_size = default_batch_size
        self._delay_ms = default_delay_ms
        
        # Timer for progressive rendering
        self._render_timer = QTimer()
        self._render_timer.timeout.connect(self._render_next_batch)
        self._render_timer.setSingleShot(True)
        
        # Statistics
        self._total_rendered = 0
        self._start_time = 0.0
    
    def start_rendering(
        self,
        items: List[T],
        batch_size: Optional[int] = None,
        delay_ms: Optional[int] = None
    ):
        """
        Start progressive rendering of items.
        
        Args:
            items: Items to render progressively
            batch_size: Number of items per batch (uses default if None)
            delay_ms: Delay between batches in milliseconds (uses default if None)
        """
        if self._state == RenderState.RENDERING:
            DebugLogger.log("Progressive rendering already in progress", "warning")
            return
        
        if not items:
            DebugLogger.log("No items to render", "debug")
            return
        
        # Setup rendering parameters
        self._pending_items = items.copy()
        self._batch_size = batch_size or self._default_batch_size
        self._delay_ms = delay_ms or self._default_delay_ms
        self._current_batch_index = 0
        self._total_batches = (len(items) + self._batch_size - 1) // self._batch_size
        self._total_rendered = 0
        self._start_time = 0.0
        
        # Update state
        self._state = RenderState.RENDERING
        
        # Emit signals
        self.rendering_started.emit(len(items), self._total_batches)
        
        # Notify target
        target = self._target() if self._target else None
        if target:
            target.on_render_started(len(items), self._total_batches)
        
        DebugLogger.log(
            f"Starting progressive render of {len(items)} items "
            f"in {self._total_batches} batches (batch size: {self._batch_size})",
            "debug"
        )
        
        # Start rendering immediately
        self._render_next_batch()
    
    def pause_rendering(self):
        """Pause progressive rendering."""
        if self._state != RenderState.RENDERING:
            return
        
        self._state = RenderState.PAUSED
        self._render_timer.stop()
        self.rendering_paused.emit()
        DebugLogger.log("Progressive rendering paused", "debug")
    
    def resume_rendering(self):
        """Resume paused progressive rendering."""
        if self._state != RenderState.PAUSED:
            return
        
        self._state = RenderState.RENDERING
        self._render_timer.start(self._delay_ms)
        self.rendering_resumed.emit()
        DebugLogger.log("Progressive rendering resumed", "debug")
    
    def cancel_rendering(self):
        """Cancel progressive rendering."""
        if self._state in (RenderState.IDLE, RenderState.COMPLETED, RenderState.CANCELLED):
            return
        
        self._state = RenderState.CANCELLED
        self._render_timer.stop()
        self._pending_items.clear()
        self.rendering_cancelled.emit()
        DebugLogger.log("Progressive rendering cancelled", "debug")
    
    def _render_next_batch(self):
        """Render the next batch of items."""
        # Check if we should continue
        if self._state != RenderState.RENDERING:
            return
        
        target = self._target() if self._target else None
        if not target or not self._pending_items:
            self._complete_rendering()
            return
        
        # Prepare batch
        batch_size = min(self._batch_size, len(self._pending_items))
        current_batch = []
        
        for _ in range(batch_size):
            if self._pending_items:
                item = self._pending_items.pop(0)
                current_batch.append(item)
        
        if not current_batch:
            self._complete_rendering()
            return
        
        # Render batch
        try:
            target.render_batch(current_batch, self._current_batch_index, self._total_batches)
            
            # Update statistics
            self._total_rendered += len(current_batch)
            
            # Emit progress signals
            self.batch_rendered.emit(self._current_batch_index, len(current_batch))
            
            total_items = self._total_rendered + len(self._pending_items)
            progress_percentage = (self._total_rendered / total_items) * 100 if total_items > 0 else 100
            self.rendering_progress.emit(self._total_rendered, total_items, progress_percentage)
            
            # Notify target
            target.on_batch_complete(self._current_batch_index, self._total_batches)
            
            DebugLogger.log(
                f"Rendered batch {self._current_batch_index + 1}/{self._total_batches} "
                f"({len(current_batch)} items, {len(self._pending_items)} remaining)",
                "debug"
            )
            
            self._current_batch_index += 1
            
        except Exception as e:
            DebugLogger.log(f"Error rendering batch: {e}", "error")
            self.cancel_rendering()
            return
        
        # Schedule next batch or complete
        if self._pending_items and self._state == RenderState.RENDERING:
            self._render_timer.start(self._delay_ms)
        else:
            self._complete_rendering()
    
    def _complete_rendering(self):
        """Complete progressive rendering."""
        self._state = RenderState.COMPLETED
        self._render_timer.stop()
        
        # Notify target
        target = self._target() if self._target else None
        if target:
            target.on_render_complete()
        
        # Emit completion signal
        self.rendering_completed.emit()
        
        DebugLogger.log(
            f"Progressive rendering completed ({self._total_rendered} items rendered)",
            "debug"
        )
    
    # ── Properties ──────────────────────────────────────────────────────────────────────────────────────────
    @property
    def state(self) -> RenderState:
        """Get current rendering state."""
        return self._state
    
    @property
    def is_rendering(self) -> bool:
        """Check if currently rendering."""
        return self._state == RenderState.RENDERING
    
    @property
    def is_paused(self) -> bool:
        """Check if rendering is paused."""
        return self._state == RenderState.PAUSED
    
    @property
    def progress_info(self) -> dict:
        """Get current progress information."""
        total_items = self._total_rendered + len(self._pending_items)
        return {
            'state': self._state.value,
            'total_items': total_items,
            'rendered_items': self._total_rendered,
            'pending_items': len(self._pending_items),
            'current_batch': self._current_batch_index,
            'total_batches': self._total_batches,
            'batch_size': self._batch_size,
            'delay_ms': self._delay_ms,
            'progress_percentage': (self._total_rendered / total_items) * 100 if total_items > 0 else 100
        }


# ── Callback-based Renderer ────────────────────────────────────────────────────────────────────────────────
class CallbackProgressiveRenderer(ProgressiveRenderer[T]):
    """Progressive renderer that uses callbacks instead of interface."""
    
    def __init__(
        self,
        render_callback: Callable[[List[T], int, int], None],
        completion_callback: Optional[Callable[[], None]] = None,
        start_callback: Optional[Callable[[int, int], None]] = None,
        batch_callback: Optional[Callable[[int, int], None]] = None,
        default_batch_size: int = 5,
        default_delay_ms: int = 10
    ):
        """
        Initialize callback-based progressive renderer.
        
        Args:
            render_callback: Callback for rendering batches (items, batch_index, total_batches)
            completion_callback: Optional callback for completion
            start_callback: Optional callback for start (total_items, total_batches)
            batch_callback: Optional callback for batch completion (batch_index, total_batches)
            default_batch_size: Default number of items per batch
            default_delay_ms: Default delay between batches in milliseconds
        """
        # Create a wrapper target
        target = CallbackTarget(
            render_callback=render_callback,
            completion_callback=completion_callback,
            start_callback=start_callback,
            batch_callback=batch_callback
        )
        
        super().__init__(target, default_batch_size, default_delay_ms)


class CallbackTarget(ProgressiveRenderTarget):
    """Helper class to wrap callbacks as a render target."""
    
    def __init__(
        self,
        render_callback: Callable[[List[Any], int, int], None],
        completion_callback: Optional[Callable[[], None]] = None,
        start_callback: Optional[Callable[[int, int], None]] = None,
        batch_callback: Optional[Callable[[int, int], None]] = None
    ):
        self._render_callback = render_callback
        self._completion_callback = completion_callback
        self._start_callback = start_callback
        self._batch_callback = batch_callback
    
    def render_batch(self, items: List[Any], batch_index: int, total_batches: int):
        """Render a batch using the callback."""
        self._render_callback(items, batch_index, total_batches)
    
    def on_render_complete(self):
        """Call completion callback if provided."""
        if self._completion_callback:
            self._completion_callback()
    
    def on_render_started(self, total_items: int, total_batches: int):
        """Call start callback if provided."""
        if self._start_callback:
            self._start_callback(total_items, total_batches)
    
    def on_batch_complete(self, batch_index: int, total_batches: int):
        """Call batch completion callback if provided."""
        if self._batch_callback:
            self._batch_callback(batch_index, total_batches)