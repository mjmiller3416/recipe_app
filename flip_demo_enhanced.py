"""Enhanced Page Flip Animation Demo

This demo shows how to use the enhanced Animator class with page flip animations
that can be applied to any QWidget or QFrame.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import QEasingCurve, Qt
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

# Import our enhanced animator
from app.ui.animations.animator import Animator


class DemoPage(QFrame):
    """A demo page with customizable content."""

    def __init__(self, title, content, color, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 10px;
                padding: 20px;
            }}
            QLabel {{
                color: white;
                background-color: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title_label)

        # Content
        content_label = QLabel(content)
        content_label.setAlignment(Qt.AlignTop)
        content_label.setWordWrap(True)
        content_label.setFont(QFont("Arial", 12))
        layout.addWidget(content_label)


class EnhancedFlipDemo(QMainWindow):
    """Enhanced page flip demo application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Page Flip Animation Demo")
        self.setFixedSize(900, 700)

        # Create demo pages
        self.pages = [
            DemoPage(
                "Shopping List Overview",
                "This is your main shopping list view.\n\n"
                "Features:\n"
                "• Categorized ingredients\n"
                "• Manual item addition\n"
                "• Recipe-based generation\n"
                "• Smart quantity calculation",
                "#2E86C1"
            ),
            DemoPage(
                "Recipe Management",
                "Manage your recipes with ease.\n\n"
                "Features:\n"
                "• Recipe creation and editing\n"
                "• Ingredient management\n"
                "• Nutritional information\n"
                "• Cooking instructions",
                "#28B463"
            ),
            DemoPage(
                "Settings & Preferences",
                "Customize your experience.\n\n"
                "Options:\n"
                "• Theme selection\n"
                "• Default measurements\n"
                "• Notification settings\n"
                "• Data backup/restore",
                "#F39C12"
            ),
            DemoPage(
                "Statistics & Analytics",
                "Track your cooking journey.\n\n"
                "Insights:\n"
                "• Most used ingredients\n"
                "• Cooking frequency\n"
                "• Cost analysis\n"
                "• Nutritional tracking",
                "#E74C3C"
            )
        ]

        self.current_page_index = 0
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Enhanced Page Flip Animation Demo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Create flip container
        self.flip_container = Animator.create_flip_container()
        self.flip_container.setFixedSize(600, 400)

        # Configure flip animation
        Animator.configure_flip_animation(
            self.flip_container,
            duration=1000,
            easing=QEasingCurve.OutBounce,
            flip_axis='y',
            fade_during_flip=True,
            scale_during_flip=True
        )

        # Set initial page
        self.flip_container.set_current_widget(self.pages[0])

        main_layout.addWidget(self.flip_container, alignment=Qt.AlignCenter)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_page)

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_page)

        # Style buttons
        button_style = """
            QPushButton {
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #3498DB;
                border-radius: 8px;
                background-color: #3498DB;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980B9;
                border-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                border-color: #BDC3C7;
                color: #7F8C8D;
            }
        """

        for button in [self.prev_button, self.next_button, self.refresh_button]:
            button.setStyleSheet(button_style)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)

        main_layout.addLayout(nav_layout)

        # Animation controls
        controls_layout = QVBoxLayout()

        controls_label = QLabel("Animation Controls")
        controls_label.setFont(QFont("Arial", 16, QFont.Bold))
        controls_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(controls_label)

        # Speed control
        speed_layout = QHBoxLayout()

        slow_button = QPushButton("Slow (2s)")
        slow_button.clicked.connect(lambda: self.set_animation_speed(2000))

        normal_button = QPushButton("Normal (1s)")
        normal_button.clicked.connect(lambda: self.set_animation_speed(1000))

        fast_button = QPushButton("Fast (0.5s)")
        fast_button.clicked.connect(lambda: self.set_animation_speed(500))

        control_button_style = """
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                border: 1px solid #95A5A6;
                border-radius: 4px;
                background-color: #ECF0F1;
                color: #2C3E50;
            }
            QPushButton:hover {
                background-color: #D5DBDB;
            }
        """

        for button in [slow_button, normal_button, fast_button]:
            button.setStyleSheet(control_button_style)

        speed_layout.addWidget(slow_button)
        speed_layout.addWidget(normal_button)
        speed_layout.addWidget(fast_button)

        controls_layout.addLayout(speed_layout)

        # Axis control
        axis_layout = QHBoxLayout()

        horizontal_button = QPushButton("Horizontal Flip")
        horizontal_button.clicked.connect(lambda: self.set_flip_axis('y'))

        vertical_button = QPushButton("Vertical Flip")
        vertical_button.clicked.connect(lambda: self.set_flip_axis('x'))

        for button in [horizontal_button, vertical_button]:
            button.setStyleSheet(control_button_style)

        axis_layout.addWidget(horizontal_button)
        axis_layout.addWidget(vertical_button)

        controls_layout.addLayout(axis_layout)

        main_layout.addLayout(controls_layout)

        # Page indicator
        self.page_indicator = QLabel()
        self.page_indicator.setAlignment(Qt.AlignCenter)
        self.page_indicator.setFont(QFont("Arial", 14))
        self.page_indicator.setStyleSheet("color: #7F8C8D; margin-top: 10px;")
        main_layout.addWidget(self.page_indicator)

        self.update_page_indicator()

    def next_page(self):
        """Navigate to the next page."""
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            next_page = self.pages[self.current_page_index]
            self.flip_container.flip_to_widget(next_page, self.update_navigation)

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            prev_page = self.pages[self.current_page_index]
            self.flip_container.flip_to_widget(prev_page, self.update_navigation)

    def refresh_page(self):
        """Refresh the current page with a flip animation."""
        current_page = self.pages[self.current_page_index]
        Animator.animate_widget_flip(
            current_page,
            duration=800,
            flip_axis='y',
            fade=True,
            scale=True
        )

    def update_navigation(self):
        """Update navigation button states."""
        self.prev_button.setEnabled(self.current_page_index > 0)
        self.next_button.setEnabled(self.current_page_index < len(self.pages) - 1)
        self.update_page_indicator()

    def update_page_indicator(self):
        """Update the page indicator."""
        self.page_indicator.setText(f"Page {self.current_page_index + 1} of {len(self.pages)}")

    def set_animation_speed(self, duration):
        """Set the animation speed."""
        Animator.configure_flip_animation(
            self.flip_container,
            duration=duration
        )

    def set_flip_axis(self, axis):
        """Set the flip axis."""
        Animator.configure_flip_animation(
            self.flip_container,
            flip_axis=axis
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #F8F9FA;
        }
    """)

    demo = EnhancedFlipDemo()
    demo.show()

    sys.exit(app.exec())
