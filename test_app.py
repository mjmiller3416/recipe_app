import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QApplication

from ui.components.dialogs import DialogWindow
from style_manager.theme_controller import ThemeController
from core.application.sidebar import Sidebar
from ui.animations import SidebarAnimator

class TestApplicationWindow:
    def __init__(self):
        # ── Initialize Main Window ──
        self.app = QApplication(sys.argv)
        self.window = DialogWindow(width=1280, height=820)

        # ── Initialize ThemeController ──
        self.theme_controller = ThemeController()
        self.theme_controller.apply_full_theme()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    test_app = TestApplicationWindow()
    test_app.run()
