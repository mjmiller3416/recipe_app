"""app/ui/utils/global_signals.py

Global signals for application-wide communication.
"""

from PySide6.QtCore import QObject, Signal

class GlobalSignals(QObject):
    """Singleton for global signals used across the application."""
    _instance = None

    # Signal emitted when any widget gains focus
    widget_focused = Signal(object)  # Emits the focused widget

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True

# Create a single instance for import
global_signals = GlobalSignals()
