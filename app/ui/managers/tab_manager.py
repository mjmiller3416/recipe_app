"""app/ui/utils/tab_manager.py

Centralized tab management utility for QTabWidget operations.
Provides consistent tab lifecycle management, index tracking, and state coordination
to eliminate repetitive tab management logic across UI components.

# ── Internal Index ──────────────────────────────────────────
#
# ── Core Tab Management ─────────────────────────────────────
# TabManager                   -> Central tab management utility
# TabManager.add_tab()         -> Add tab with automatic index management
# TabManager.remove_tab()      -> Remove tab with index cleanup
# TabManager.get_tab_widget()  -> Retrieve widget by index
# TabManager.set_tab_title()   -> Update tab title
#
# ── Index & Registry Management ─────────────────────────────
# TabManager.update_mapping()  -> Rebuild tab index mapping
# TabManager.get_valid_indices() -> Get all valid tab indices
# TabManager.handle_deletion_index_update() -> Manage indices after deletion
#
# ── State & Signals ─────────────────────────────────────────
# TabManager.get_tab_count()   -> Get count of managed tabs
# TabManager.get_current_index() -> Get currently selected tab
# TabManager.set_current_index() -> Set active tab
#
# ── Special Tab Support ─────────────────────────────────────
# TabManager.has_special_tab() -> Check for special tabs (like +)
# TabManager.get_insert_index() -> Get insertion point for new tabs

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QTabWidget, QWidget

from _dev_tools import DebugLogger

__all__ = [
    # Core Tab Management
    'TabManager', 'TabState',

    # Tab Operations
    'TabOperation',
]


# ── Enums ───────────────────────────────────────────────────────────────────────────────────────────────────
class TabState(Enum):
    """Tab state enumeration for tracking tab lifecycle."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MODIFIED = "modified"
    LOADING = "loading"
    ERROR = "error"

class TabOperation(Enum):
    """Tab operation types for signal emissions."""
    ADDED = "added"
    REMOVED = "removed"
    ACTIVATED = "activated"
    MODIFIED = "modified"
    MOVED = "moved"


# ── Tab Manager Utility ─────────────────────────────────────────────────────────────────────────────────────
class TabManager(QObject):
    """
    Centralized tab management utility for QTabWidget operations.

    Provides comprehensive tab lifecycle management including:
    - Tab creation, deletion, and index management
    - Tab registry/mapping operations
    - State tracking and change notifications
    - Special tab handling (e.g., "+" tabs)
    - Index cleanup after tab operations

    This utility eliminates repetitive tab management logic and provides
    consistent tab behavior across different UI components.
    """

    # Signals for tab state changes
    tab_added = Signal(int, object)        # index, widget
    tab_removed = Signal(int, object)      # index, widget
    tab_activated = Signal(int, object)    # index, widget
    tab_state_changed = Signal(int, str)   # index, state
    tab_mapping_updated = Signal(dict)     # updated mapping

    def __init__(self, tab_widget: QTabWidget, parent: Optional[QObject] = None):
        """
        Initialize TabManager with target QTabWidget.

        Args:
            tab_widget: The QTabWidget to manage
            parent: Optional parent QObject
        """
        super().__init__(parent)

        self._tab_widget = tab_widget
        self._tab_registry: Dict[int, QWidget] = {}  # {index: widget}
        self._tab_states: Dict[int, TabState] = {}   # {index: state}
        self._special_tab_indices: List[int] = []    # Indices of special tabs (like +)

        # Connect to tab widget signals
        self._connect_signals()

        DebugLogger.log("TabManager initialized", "info")

    def _connect_signals(self) -> None:
        """Connect to QTabWidget signals for automatic state management."""
        if self._tab_widget:
            self._tab_widget.currentChanged.connect(self._on_tab_changed)
            # Note: We don't connect tabBarClicked here as that should be handled
            # by the parent component for special tab logic

    # ── Core Tab Management ─────────────────────────────────────────────────────────────────────────────────
    def add_tab(self, widget: QWidget, title: str, insert_at: Optional[int] = None) -> int:
        """
        Add a new tab with automatic index management.

        Args:
            widget: Widget to add as tab content
            title: Tab title
            insert_at: Optional insertion index. If None, inserts before special tabs

        Returns:
            Index of the newly added tab

        Raises:
            ValueError: If widget is None or title is empty
        """
        if not widget:
            raise ValueError("Widget cannot be None")
        if not title.strip():
            raise ValueError("Title cannot be empty")

        # Determine insertion index
        if insert_at is None:
            insert_at = self._get_default_insert_index()

        # Update existing registry indices before insertion
        self._update_indices_before_insertion(insert_at)

        # Insert the tab
        index = self._tab_widget.insertTab(insert_at, widget, title)

        # Add to registry and state at the actual index returned
        self._tab_registry[index] = widget
        self._tab_states[index] = TabState.ACTIVE

        # Set as current tab
        self._tab_widget.setCurrentIndex(index)

        DebugLogger.log(f"Added tab '{title}' at index {index}", "info")

        # Emit signal
        self.tab_added.emit(index, widget)
        self.tab_mapping_updated.emit(self._tab_registry.copy())

        return index

    def remove_tab(self, index: int) -> bool:
        """
        Remove tab and handle index cleanup.

        Args:
            index: Index of tab to remove

        Returns:
            True if tab was successfully removed, False otherwise
        """
        if not self._is_valid_tab_index(index):
            DebugLogger.log(f"Cannot remove tab: invalid index {index}", "warning")
            return False

        if index in self._special_tab_indices:
            DebugLogger.log(f"Cannot remove special tab at index {index}", "warning")
            return False

        # Get widget before removal
        widget = self._tab_registry.get(index)

        # Determine new selected tab if removing current tab
        current_tab = self._tab_widget.currentIndex()
        new_selected_index = None

        if index == current_tab:
            new_selected_index = self._calculate_new_selection_index(index)

        # Remove the tab
        self._tab_widget.removeTab(index)

        # Update registry and states
        self._update_indices_after_removal(index)

        # Set new selection if needed
        if new_selected_index is not None and new_selected_index < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(new_selected_index)
            DebugLogger.log(f"Auto-selected tab at index {new_selected_index} after deletion", "info")

        DebugLogger.log(f"Removed tab at index {index}", "info")

        # Emit signals
        if widget:
            self.tab_removed.emit(index, widget)
        self.tab_mapping_updated.emit(self._tab_registry.copy())

        return True

    def get_tab_widget(self, index: int) -> Optional[QWidget]:
        """
        Get widget for the specified tab index.

        Args:
            index: Tab index

        Returns:
            Widget at the given index, or None if invalid
        """
        return self._tab_registry.get(index)

    def set_tab_title(self, index: int, title: str) -> bool:
        """
        Update tab title.

        Args:
            index: Tab index
            title: New title

        Returns:
            True if title was updated, False otherwise
        """
        if not self._is_valid_tab_index(index):
            return False

        if not title.strip():
            DebugLogger.log("Cannot set empty tab title", "warning")
            return False

        self._tab_widget.setTabText(index, title)
        DebugLogger.log(f"Updated tab {index} title to '{title}'", "info")
        return True

    # ── Index & Registry Management ─────────────────────────────────────────────────────────────────────────
    def update_mapping(self) -> None:
        """
        Rebuild tab index mapping from current tab widget state.
        Useful for synchronizing after external tab operations.
        """
        old_registry = self._tab_registry.copy()
        self._tab_registry.clear()
        self._tab_states.clear()

        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            if widget and i not in self._special_tab_indices:
                self._tab_registry[i] = widget
                self._tab_states[i] = TabState.ACTIVE

        DebugLogger.log("Tab mapping updated", "info")
        self.tab_mapping_updated.emit(self._tab_registry.copy())

    def get_valid_indices(self) -> List[int]:
        """
        Get list of all valid (non-special) tab indices.

        Returns:
            List of valid tab indices
        """
        return [i for i in self._tab_registry.keys() if i not in self._special_tab_indices]

    def handle_deletion_index_update(self, deleted_index: int) -> int:
        """
        Calculate index adjustments after a tab deletion.

        Args:
            deleted_index: Index of the deleted tab

        Returns:
            Number of indices that were updated
        """
        return self._update_indices_after_removal(deleted_index)

    # ── State & Signals ─────────────────────────────────────────────────────────────────────────────────────
    def get_tab_count(self) -> int:
        """
        Get count of managed tabs (excluding special tabs).

        Returns:
            Number of managed tabs
        """
        return len(self._tab_registry)

    def get_current_index(self) -> int:
        """
        Get currently selected tab index.

        Returns:
            Current tab index
        """
        return self._tab_widget.currentIndex()

    def set_current_index(self, index: int) -> bool:
        """
        Set active tab by index.

        Args:
            index: Index to activate

        Returns:
            True if tab was activated, False otherwise
        """
        if not (0 <= index < self._tab_widget.count()):
            return False

        self._tab_widget.setCurrentIndex(index)
        return True

    def get_tab_state(self, index: int) -> Optional[TabState]:
        """
        Get state of tab at given index.

        Args:
            index: Tab index

        Returns:
            TabState or None if invalid index
        """
        return self._tab_states.get(index)

    def set_tab_state(self, index: int, state: TabState) -> bool:
        """
        Set state of tab at given index.

        Args:
            index: Tab index
            state: New tab state

        Returns:
            True if state was updated, False otherwise
        """
        if not self._is_valid_tab_index(index):
            return False

        old_state = self._tab_states.get(index)
        self._tab_states[index] = state

        if old_state != state:
            DebugLogger.log(f"Tab {index} state changed from {old_state} to {state}", "info")
            self.tab_state_changed.emit(index, state.value)

        return True

    # ── Special Tab Support ─────────────────────────────────────────────────────────────────────────────────
    def register_special_tab(self, index: int) -> None:
        """
        Register a tab as special (e.g., "+" tab that should not be managed normally).

        Args:
            index: Index of special tab
        """
        if index not in self._special_tab_indices:
            self._special_tab_indices.append(index)
            # Remove from regular registry if present
            self._tab_registry.pop(index, None)
            self._tab_states.pop(index, None)
            DebugLogger.log(f"Registered special tab at index {index}", "info")

    def unregister_special_tab(self, index: int) -> None:
        """
        Unregister a special tab.

        Args:
            index: Index to unregister
        """
        if index in self._special_tab_indices:
            self._special_tab_indices.remove(index)
            DebugLogger.log(f"Unregistered special tab at index {index}", "info")

    def has_special_tab(self) -> bool:
        """
        Check if any special tabs are registered.

        Returns:
            True if special tabs exist
        """
        return len(self._special_tab_indices) > 0

    def get_insert_index(self) -> int:
        """
        Get appropriate insertion index for new tabs (before special tabs).

        Returns:
            Index where new tabs should be inserted
        """
        return self._get_default_insert_index()

    # ── Internal Helper Methods ─────────────────────────────────────────────────────────────────────────────
    def _is_valid_tab_index(self, index: int) -> bool:
        """Check if index is valid for tab operations."""
        return 0 <= index < self._tab_widget.count() and index in self._tab_registry

    def _get_default_insert_index(self) -> int:
        """Get default insertion index (before special tabs)."""
        if self._special_tab_indices:
            return min(self._special_tab_indices)
        return self._tab_widget.count()

    def _calculate_new_selection_index(self, deleted_index: int) -> Optional[int]:
        """Calculate which tab to select after deletion."""
        total_managed_tabs = len(self._tab_registry)

        if total_managed_tabs <= 1:
            return None

        # Try previous tab first
        if deleted_index > 0:
            return deleted_index - 1
        # If deleting first tab, select next (which becomes index 0)
        elif total_managed_tabs > 1:
            return 0

        return None

    def _update_indices_before_insertion(self, insert_at: int) -> None:
        """Update internal indices before tab insertion."""
        # Create new registry with updated indices for existing tabs that will shift
        new_registry = {}
        new_states = {}

        for old_index, widget in self._tab_registry.items():
            if old_index >= insert_at:
                new_index = old_index + 1
                new_registry[new_index] = widget
                new_states[new_index] = self._tab_states.get(old_index, TabState.ACTIVE)
            else:
                new_registry[old_index] = widget
                new_states[old_index] = self._tab_states.get(old_index, TabState.ACTIVE)

        self._tab_registry = new_registry
        self._tab_states = new_states

        # Update special tab indices
        self._special_tab_indices = [
            idx + 1 if idx >= insert_at else idx
            for idx in self._special_tab_indices
        ]

    def _update_indices_after_removal(self, removed_index: int) -> int:
        """Update internal indices after tab removal."""
        # Remove from registry and states
        self._tab_registry.pop(removed_index, None)
        self._tab_states.pop(removed_index, None)

        # Create new registry with updated indices
        new_registry = {}
        new_states = {}
        updates_count = 0

        for old_index, widget in self._tab_registry.items():
            if old_index > removed_index:
                new_index = old_index - 1
                new_registry[new_index] = widget
                new_states[new_index] = self._tab_states.get(old_index, TabState.ACTIVE)
                updates_count += 1
            else:
                new_registry[old_index] = widget
                new_states[old_index] = self._tab_states.get(old_index, TabState.ACTIVE)

        self._tab_registry = new_registry
        self._tab_states = new_states

        # Update special tab indices
        self._special_tab_indices = [
            idx - 1 if idx > removed_index else idx
            for idx in self._special_tab_indices
        ]

        return updates_count

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab selection changes."""
        widget = self.get_tab_widget(index)
        if widget and index in self._tab_registry:
            self.tab_activated.emit(index, widget)
            DebugLogger.log(f"Tab activated: index {index}", "info")

    # ── Registry Access (Read-Only) ─────────────────────────────────────────────────────────────────────────
    @property
    def tab_registry(self) -> Dict[int, QWidget]:
        """
        Get read-only copy of tab registry.

        Returns:
            Copy of current tab registry
        """
        return self._tab_registry.copy()

    @property
    def tab_widget(self) -> QTabWidget:
        """
        Get managed tab widget.

        Returns:
            The QTabWidget being managed
        """
        return self._tab_widget
