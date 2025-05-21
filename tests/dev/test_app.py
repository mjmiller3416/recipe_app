# ── Imports ─────────────────────────────────────────────────────────────────────
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea

from core.helpers.debug_logger import DebugLogger
from ui.components.inputs.smart_combobox import SmartComboBox


def run_test(app: QApplication) -> QScrollArea:
    """
    Launch the test window. This method is required by main.py --test entry point.

    Args:
        app (QApplication): The active QApplication instance.

    Returns:
        QScrollArea: The main test window with your test widget content.
    """

    # Build your test widget here 👇
    test_content = SmartComboBox(
        values=["Apple", "Banana", "Cherry", "Date", "Elderberry"],
        placeholder="Select a fruit",
    )

    # Wrap in scrollable test window
    scroll_window = QScrollArea()
    scroll_window.setWindowTitle("Test App")
    scroll_window.setWidgetResizable(True)
    scroll_window.setMinimumSize(1000, 800)
    scroll_window.setWidget(test_content)

    # Load stylesheet if needed

    scroll_window.show()
    return scroll_window


def create_test_widget() -> QWidget:
    """
    Construct and return your custom widget to test.

    Returns:
        QWidget: Your widget or test layout container.
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setSpacing(20)

    # 👇 Add your test widgets here
    # e.g., layout.addWidget(MyCustomWidget())

    return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Test App")

    test_win = run_test(app)
    sys.exit(app.exec())
