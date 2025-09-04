"""app/ui/services/stack.py

Navigation history and stack management for route-based navigation.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from _dev_tools import DebugLogger


# ── Navigation Entry ────────────────────────────────────────────────────────────────────────────────────────
@dataclass
class NavigationEntry:
    """Represents a single entry in the navigation history."""
    path: str
    params: Dict[str, str]
    timestamp: datetime
    title: Optional[str] = None
    data: Optional[Dict[str, Any]] = None  # Additional state data

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def full_path(self) -> str:
        """Get the full path with parameters substituted."""
        result = self.path
        for key, value in self.params.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result


# ── Navigation Stack ────────────────────────────────────────────────────────────────────────────────────────
class NavigationStack(QObject):
    """
    Manages navigation history and provides back/forward functionality.

    Signals:
        history_changed: Emitted when navigation history changes
        can_go_back_changed: Emitted when back availability changes
        can_go_forward_changed: Emitted when forward availability changes
    """

    history_changed = Signal()
    can_go_back_changed = Signal(bool)
    can_go_forward_changed = Signal(bool)

    def __init__(self, max_history: int = 50):
        super().__init__()
        self._history: List[NavigationEntry] = []
        self._current_index: int = -1
        self._max_history = max_history

    def push(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        replace_current: bool = False
    ):
        """
        Add a new entry to the navigation stack.

        Args:
            path: The route path
            params: Route parameters
            title: Optional title for the entry
            data: Optional additional state data
            replace_current: If True, replaces the current entry instead of adding new one
        """
        if params is None:
            params = {}

        entry = NavigationEntry(
            path=path,
            params=params,
            timestamp=datetime.now(),
            title=title,
            data=data
        )

        if replace_current and self._current_index >= 0:
            # Replace current entry
            self._history[self._current_index] = entry
            DebugLogger.log(f"Replaced navigation entry at index {self._current_index}: {entry.full_path}", "info")
        else:
            # Remove any forward history when pushing new entry
            if self._current_index < len(self._history) - 1:
                self._history = self._history[:self._current_index + 1]

            # Add new entry
            self._history.append(entry)
            self._current_index = len(self._history) - 1

            # Trim history if it exceeds max size
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
                self._current_index = len(self._history) - 1

            DebugLogger.log(f"Pushed navigation entry: {entry.full_path} (index: {self._current_index})", "info")

        self._emit_changes()

    def can_go_back(self) -> bool:
        """Check if backward navigation is possible."""
        return self._current_index > 0

    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return self._current_index < len(self._history) - 1

    def go_back(self) -> Optional[NavigationEntry]:
        """
        Navigate backward in history.

        Returns:
            The previous navigation entry, or None if can't go back
        """
        if not self.can_go_back():
            DebugLogger.log("Cannot go back - already at beginning of history", "warning")
            return None

        self._current_index -= 1
        entry = self._history[self._current_index]

        DebugLogger.log(f"Navigated back to: {entry.full_path} (index: {self._current_index})", "info")
        self._emit_changes()

        return entry

    def go_forward(self) -> Optional[NavigationEntry]:
        """
        Navigate forward in history.

        Returns:
            The next navigation entry, or None if can't go forward
        """
        if not self.can_go_forward():
            DebugLogger.log("Cannot go forward - already at end of history", "warning")
            return None

        self._current_index += 1
        entry = self._history[self._current_index]

        DebugLogger.log(f"Navigated forward to: {entry.full_path} (index: {self._current_index})", "info")
        self._emit_changes()

        return entry

    def current(self) -> Optional[NavigationEntry]:
        """Get the current navigation entry."""
        if self._current_index >= 0 and self._current_index < len(self._history):
            return self._history[self._current_index]
        return None

    def peek_back(self) -> Optional[NavigationEntry]:
        """Peek at the previous entry without navigating."""
        if self.can_go_back():
            return self._history[self._current_index - 1]
        return None

    def peek_forward(self) -> Optional[NavigationEntry]:
        """Peek at the next entry without navigating."""
        if self.can_go_forward():
            return self._history[self._current_index + 1]
        return None

    def get_history(self) -> List[NavigationEntry]:
        """Get a copy of the full navigation history."""
        return self._history.copy()

    def get_back_history(self, count: int = 10) -> List[NavigationEntry]:
        """
        Get recent backward history entries.

        Args:
            count: Maximum number of entries to return

        Returns:
            List of navigation entries in reverse chronological order
        """
        if self._current_index <= 0:
            return []

        start_idx = max(0, self._current_index - count)
        return self._history[start_idx:self._current_index][::-1]  # Reverse order

    def get_forward_history(self, count: int = 10) -> List[NavigationEntry]:
        """
        Get forward history entries.

        Args:
            count: Maximum number of entries to return

        Returns:
            List of navigation entries in chronological order
        """
        if not self.can_go_forward():
            return []

        end_idx = min(len(self._history), self._current_index + 1 + count)
        return self._history[self._current_index + 1:end_idx]

    def clear(self):
        """Clear all navigation history."""
        self._history.clear()
        self._current_index = -1
        DebugLogger.log("Cleared navigation history", "info")
        self._emit_changes()

    def remove_entries_matching(self, path_pattern: str):
        """
        Remove all history entries matching a path pattern.

        Args:
            path_pattern: Pattern to match against entry paths
        """
        original_count = len(self._history)

        # Filter out matching entries
        filtered_history = []
        new_current_index = -1

        for i, entry in enumerate(self._history):
            if path_pattern not in entry.path:
                if i <= self._current_index:
                    new_current_index = len(filtered_history)
                filtered_history.append(entry)

        self._history = filtered_history
        self._current_index = new_current_index

        removed_count = original_count - len(self._history)
        if removed_count > 0:
            DebugLogger.log(f"Removed {removed_count} navigation entries matching: {path_pattern}", "info")
            self._emit_changes()

    def replace_current_data(self, data: Dict[str, Any]):
        """
        Update the data for the current navigation entry.

        Args:
            data: New data to set for current entry
        """
        current_entry = self.current()
        if current_entry:
            current_entry.data = data
            DebugLogger.log(f"Updated data for current navigation entry: {current_entry.full_path}", "info")

    def get_current_index(self) -> int:
        """Get the current position in the history stack."""
        return self._current_index

    def get_history_size(self) -> int:
        """Get the total size of the navigation history."""
        return len(self._history)

    def _emit_changes(self):
        """Emit change signals to notify listeners."""
        self.history_changed.emit()
        self.can_go_back_changed.emit(self.can_go_back())
        self.can_go_forward_changed.emit(self.can_go_forward())

class NavigationStackManager:
    """
    Global manager for navigation stacks.

    Supports multiple navigation contexts (main, modal, etc.)
    """

    _stacks: Dict[str, NavigationStack] = {}

    @classmethod
    def get_stack(cls, context: str = "main") -> NavigationStack:
        """
        Get or create a navigation stack for a given context.

        Args:
            context: Navigation context name (e.g., "main", "modal")

        Returns:
            NavigationStack instance for the context
        """
        if context not in cls._stacks:
            cls._stacks[context] = NavigationStack()
            DebugLogger.log(f"Created navigation stack for context: {context}", "info")

        return cls._stacks[context]

    @classmethod
    def clear_stack(cls, context: str):
        """Clear a specific navigation stack."""
        if context in cls._stacks:
            cls._stacks[context].clear()

    @classmethod
    def clear_all_stacks(cls):
        """Clear all navigation stacks."""
        for stack in cls._stacks.values():
            stack.clear()
        DebugLogger.log("Cleared all navigation stacks", "info")

    @classmethod
    def get_all_contexts(cls) -> List[str]:
        """Get all available navigation contexts."""
        return list(cls._stacks.keys())
