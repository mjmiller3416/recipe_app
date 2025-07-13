import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsProxyWidget
)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Property, QObject, Signal
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QBrush, QTransform
from PySide6.QtCore import Qt, QRectF


class FlippableGraphicsItem(QGraphicsPixmapItem):
    """A graphics item that can be flipped with 3D rotation animation."""

    def __init__(self, pixmap=None, parent=None):
        super().__init__(pixmap, parent)
        self._rotation_y = 0
        self._scale_x = 1.0
        self.setTransformOriginPoint(self.boundingRect().center())

        # Create a QObject to handle the animation
        self._animation_helper = AnimationHelper(self)

    def set_rotation_y(self, value):
        """Set the rotation Y value and update the transform."""
        self._rotation_y = value
        # Create 3D flip effect by scaling X based on rotation
        scale_factor = abs(1.0 - abs(value) / 90.0)
        if abs(value) > 90:
            scale_factor = abs(abs(value) - 180) / 90.0

        # Reset transform and apply new scale
        self.setTransform(QTransform().scale(scale_factor, 1.0))
        self._scale_x = scale_factor

        # Hide item when fully rotated (back side)
        self.setVisible(abs(value) < 90)

    def get_rotation_y(self):
        """Get the current rotation Y value."""
        return self._rotation_y

    def get_animation_helper(self):
        """Get the animation helper object."""
        return self._animation_helper


class AnimationHelper(QObject):
    """Helper class to provide QObject functionality for animations."""

    def __init__(self, graphics_item):
        super().__init__()
        self.graphics_item = graphics_item
        self._rotation_y = 0

    @Property(float)
    def rotation_y(self):
        return self._rotation_y

    @rotation_y.setter
    def rotation_y(self, value):
        self._rotation_y = value
        self.graphics_item.set_rotation_y(value)


class PageFlipView(QGraphicsView):
    """Graphics view that handles page flipping animations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedSize(600, 400)

        # Create page items
        self.current_page = FlippableGraphicsItem()
        self.next_page = FlippableGraphicsItem()

        self.scene.addItem(self.current_page)
        self.scene.addItem(self.next_page)

        # Initially hide next page
        self.next_page.setVisible(False)

        # Animation properties
        self.animation_duration = 800
        self.is_flipping = False

    def create_page_pixmap(self, title: str, content: str, color: QColor) -> QPixmap:
        """Create a pixmap representing a page with title and content."""
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw border
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.drawRect(10, 10, 480, 280)

        # Draw title
        title_font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(50, 50, 50))
        painter.drawText(QRectF(20, 30, 460, 50), Qt.AlignCenter, title)

        # Draw content
        content_font = QFont("Arial", 14)
        painter.setFont(content_font)
        painter.setPen(QColor(80, 80, 80))
        painter.drawText(QRectF(30, 100, 440, 180), Qt.AlignLeft | Qt.TextWordWrap, content)

        # Add page background gradient
        gradient_brush = QBrush(color)
        gradient_brush.setStyle(Qt.Dense7Pattern)
        painter.setBrush(gradient_brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(20, 250, 460, 30)

        painter.end()
        return pixmap

    def flip_to_next(self, current_pixmap: QPixmap, next_pixmap: QPixmap):
        """Animate flipping from current page to next page."""
        if self.is_flipping:
            return

        self.is_flipping = True

        # Set up pages
        self.current_page.setPixmap(current_pixmap)
        self.next_page.setPixmap(next_pixmap)

        # Position pages
        self.current_page.setPos(0, 0)
        self.next_page.setPos(0, 0)

        # Reset rotations
        self.current_page.set_rotation_y(0)
        self.next_page.set_rotation_y(180)

        # Show both pages
        self.current_page.setVisible(True)
        self.next_page.setVisible(False)

        # Create animations using the helper objects
        self.current_animation = QPropertyAnimation(self.current_page.get_animation_helper(), b"rotation_y")
        self.current_animation.setDuration(self.animation_duration)
        self.current_animation.setStartValue(0)
        self.current_animation.setEndValue(180)
        self.current_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.next_animation = QPropertyAnimation(self.next_page.get_animation_helper(), b"rotation_y")
        self.next_animation.setDuration(self.animation_duration)
        self.next_animation.setStartValue(180)
        self.next_animation.setEndValue(0)
        self.next_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Show next page when current page is half-way flipped
        def show_next_page():
            self.next_page.setVisible(True)

        QTimer.singleShot(self.animation_duration // 2, show_next_page)

        # Handle animation completion
        def on_flip_complete():
            self.is_flipping = False
            # Swap pages for next flip
            self.current_page, self.next_page = self.next_page, self.current_page

        self.next_animation.finished.connect(on_flip_complete)

        # Start animations
        self.current_animation.start()
        self.next_animation.start()


class PageFlipDemo(QMainWindow):
    """Main demo application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Flip Animation Demo")
        self.setFixedSize(800, 600)

        # Sample page data
        self.pages = [
            {
                "title": "Shopping List - Recipes",
                "content": "• Italian Pasta Recipe\n• Chicken Curry Recipe\n• Chocolate Cake Recipe\n\nClick 'Next Page' to see the ingredients breakdown.",
                "color": QColor(70, 130, 180)
            },
            {
                "title": "Shopping List - Ingredients",
                "content": "Pantry Items:\n• Pasta - 2 lbs\n• Rice - 1 lb\n• Flour - 3 cups\n\nFresh Items:\n• Chicken - 2 lbs\n• Tomatoes - 6 pieces\n• Onions - 3 pieces",
                "color": QColor(60, 179, 113)
            },
            {
                "title": "Shopping List - Dairy & Spices",
                "content": "Dairy:\n• Milk - 1 gallon\n• Cheese - 8 oz\n• Butter - 1 stick\n\nSpices:\n• Curry powder - 2 tbsp\n• Salt - 1 tsp\n• Black pepper - 1 tsp",
                "color": QColor(255, 165, 0)
            },
            {
                "title": "Shopping Summary",
                "content": "Total Items: 12\nEstimated Cost: $45.50\n\nCategories:\n• Pantry Items: 3\n• Fresh Items: 6\n• Dairy & Spices: 6\n\nReady to go shopping!",
                "color": QColor(220, 20, 60)
            }
        ]

        self.current_page_index = 0
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Page Flip Animation Demo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # Page flip view
        self.flip_view = PageFlipView()
        self.flip_view.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #ccc;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.flip_view, alignment=Qt.AlignCenter)

        # Control buttons
        button_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.next_page)

        # Style buttons
        button_style = """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
        """

        self.prev_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

        button_layout.addWidget(self.prev_button)
        button_layout.addStretch()
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        # Page indicator
        self.page_indicator = QLabel()
        self.page_indicator.setAlignment(Qt.AlignCenter)
        self.page_indicator.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.page_indicator)

        # Load initial page
        self.update_page_display()

    def update_page_display(self):
        """Update the page display and controls."""
        current_page = self.pages[self.current_page_index]
        current_pixmap = self.flip_view.create_page_pixmap(
            current_page["title"],
            current_page["content"],
            current_page["color"]
        )

        # Set initial page without animation
        self.flip_view.current_page.setPixmap(current_pixmap)
        self.flip_view.current_page.setPos(0, 0)
        self.flip_view.current_page.set_rotation_y(0)
        self.flip_view.current_page.setVisible(True)
        self.flip_view.next_page.setVisible(False)

        # Update controls
        self.prev_button.setEnabled(self.current_page_index > 0)
        self.next_button.setEnabled(self.current_page_index < len(self.pages) - 1)

        # Update page indicator
        self.page_indicator.setText(f"Page {self.current_page_index + 1} of {len(self.pages)}")

    def next_page(self):
        """Flip to the next page."""
        if self.current_page_index < len(self.pages) - 1 and not self.flip_view.is_flipping:
            next_index = self.current_page_index + 1

            current_page = self.pages[self.current_page_index]
            next_page = self.pages[next_index]

            current_pixmap = self.flip_view.create_page_pixmap(
                current_page["title"],
                current_page["content"],
                current_page["color"]
            )

            next_pixmap = self.flip_view.create_page_pixmap(
                next_page["title"],
                next_page["content"],
                next_page["color"]
            )

            self.flip_view.flip_to_next(current_pixmap, next_pixmap)
            self.current_page_index = next_index

            # Update controls after animation
            QTimer.singleShot(self.flip_view.animation_duration + 100, self.update_controls)

    def previous_page(self):
        """Flip to the previous page."""
        if self.current_page_index > 0 and not self.flip_view.is_flipping:
            prev_index = self.current_page_index - 1

            current_page = self.pages[self.current_page_index]
            prev_page = self.pages[prev_index]

            current_pixmap = self.flip_view.create_page_pixmap(
                current_page["title"],
                current_page["content"],
                current_page["color"]
            )

            prev_pixmap = self.flip_view.create_page_pixmap(
                prev_page["title"],
                prev_page["content"],
                prev_page["color"]
            )

            self.flip_view.flip_to_next(current_pixmap, prev_pixmap)
            self.current_page_index = prev_index

            # Update controls after animation
            QTimer.singleShot(self.flip_view.animation_duration + 100, self.update_controls)

    def update_controls(self):
        """Update button states and page indicator."""
        self.prev_button.setEnabled(self.current_page_index > 0)
        self.next_button.setEnabled(self.current_page_index < len(self.pages) - 1)
        self.page_indicator.setText(f"Page {self.current_page_index + 1} of {len(self.pages)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
    """)

    demo = PageFlipDemo()
    demo.show()

    sys.exit(app.exec())
