from PySide6.QtCore import QObject, QEvent

class DebugFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.ToolTip:
            print(f"[Tooltip Triggered] Target: {obj}, Class: {obj.__class__.__name__}")
        else:
            print(f"[Event {event.type()}] on {obj.__class__.__name__}")
        return super().eventFilter(obj, event)
