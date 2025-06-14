import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QApplication

from core.application.app_window import ApplicationWindow
from style_manager.theme_controller import ThemeController
from core.application.sidebar import Sidebar
from ui.animations import SidebarAnimator



class TestApplicationWindow:
    def __init__(self):
        # ── Initialize Main Window ──
        self.app = QApplication(sys.argv)
        self.window = ApplicationWindow(width=1280, height=820)

        # ── Initialize ThemeController ──
        self.theme_controller = ThemeController()
        self.theme_controller.apply_full_theme()

        # ── Instantiate Sidebar ──
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(250)
        self.window.content_layout.addWidget(self.sidebar)
        self.sidebar_is_expanded = True

        # ── Connect Signals ──
        self._connect_signals()

    def _connect_signals(self):
        self.window.sidebar_toggle_requested.connect(self.toggle_sidebar)

    def toggle_sidebar(self):
        """ Toggle the sidebar's expanded/collapsed state with animation."""
        collapsed_width = 0
        expanded_width = 215

        # determine start and end widths
        start_width = self.sidebar.width()
        end_width = collapsed_width if self.sidebar_is_expanded else expanded_width

        # create the animator
        self.sidebar_animator = SidebarAnimator(self.sidebar)

        # create the animation
        self.sidebar_animation = QPropertyAnimation(self.sidebar_animator, b"value")
        self.sidebar_animation.setDuration(500)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.OutExpo)

        self.sidebar_animation.start() # start the animation
        self.sidebar_is_expanded = not self.sidebar_is_expanded
    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    test_app = TestApplicationWindow()
    test_app.run()
