import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QHBoxLayout, QWidget, QFrame, QPushButton, QLabel)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QRect, Property
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QRadialGradient
from PySide6.QtWidgets import QGraphicsOpacityEffect


class CustomShadowFrame(QFrame):
    """A QFrame with custom painted shadow + opacity animation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_custom_effects()

    def setup_custom_effects(self):
        """Create custom shadow and opacity effects"""
        self.setFixedSize(300, 200)
        print(f"[SETUP] Custom frame geometry: {self.geometry()}")

        # Make the outer frame transparent
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        # Shadow properties for custom painting
        self._shadow_opacity = 180  # Alpha value 0-255 (using underscore for property backing)
        self.shadow_blur = 20
        self.shadow_offset_x = 5
        self.shadow_offset_y = 5

        # Inner content frame - positioned to leave room for shadow
        self.inner_frame = QFrame(self)
        self.inner_frame.setGeometry(30, 30, 240, 140)  # More margin for shadow
        self.inner_frame.setStyleSheet("""
            QFrame {
                background-color: #4a4a4a;
                border: 2px solid #6a6a6a;
                border-radius: 10px;
            }
        """)

        # Add content
        layout = QVBoxLayout(self.inner_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        label = QLabel("Custom Shadow Demo:\n\n• Hand-painted shadow effect\n• Opacity animation on content\n• No graphics effect jumping")
        label.setStyleSheet("color: white; font-size: 11px;")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Apply opacity to inner frame only
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.inner_frame.setGraphicsEffect(self.opacity_effect)

        # Animations
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Custom shadow animation - animate the shadow opacity property
        self.shadow_animation = QPropertyAnimation(self, b"shadow_opacity")
        self.shadow_animation.setDuration(500)
        self.shadow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        # Connect to repaint when shadow changes
        self.shadow_animation.valueChanged.connect(self.update)

        self.is_faded = False
        self.shadow_visible = True

        print(f"[SETUP] Custom frame setup complete: {self.geometry()}")

    # Property for shadow opacity animation (using Qt Property system)
    @Property(int)
    def shadow_opacity(self):
        return self._shadow_opacity

    @shadow_opacity.setter
    def shadow_opacity(self, opacity):
        self._shadow_opacity = opacity
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint event to draw shadow manually"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Only draw shadow if it has opacity
        if self._shadow_opacity > 0:
            # Calculate shadow rectangle
            inner_rect = self.inner_frame.geometry()
            shadow_rect = QRect(
                inner_rect.x() + self.shadow_offset_x,
                inner_rect.y() + self.shadow_offset_y,
                inner_rect.width(),
                inner_rect.height()
            )

            # Create multiple shadow layers for blur effect
            blur_layers = max(1, self.shadow_blur // 4)
            base_opacity = self._shadow_opacity / blur_layers

            for i in range(blur_layers):
                # Calculate this layer's properties
                layer_offset = i * 2
                layer_opacity = max(0, int(base_opacity * (blur_layers - i) / blur_layers))

                # Expand shadow rect for this layer
                expanded_rect = QRect(
                    shadow_rect.x() - layer_offset,
                    shadow_rect.y() - layer_offset,
                    shadow_rect.width() + (layer_offset * 2),
                    shadow_rect.height() + (layer_offset * 2)
                )

                # Set shadow color with calculated opacity
                shadow_color = QColor(0, 0, 0, layer_opacity)
                painter.setBrush(QBrush(shadow_color))
                painter.setPen(QPen(shadow_color, 1))

                # Draw rounded rectangle shadow
                painter.drawRoundedRect(expanded_rect, 12, 12)

        # Call parent paint event for normal widget painting
        super().paintEvent(event)

    def toggle_effects(self):
        """Toggle both shadow and opacity with smooth animations"""
        print(f"\n[TOGGLE] Custom button clicked! Current geometry: {self.geometry()}")
        print(f"[TOGGLE] is_faded: {self.is_faded}, shadow_visible: {self.shadow_visible}")

        # Toggle opacity
        if self.is_faded:
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(1.0)
            print(f"[TOGGLE] Fading IN: 0.0 -> 1.0")
        else:
            self.opacity_animation.setStartValue(1.0)
            self.opacity_animation.setEndValue(0.0)
            print(f"[TOGGLE] Fading OUT: 1.0 -> 0.0")

        # Toggle shadow
        if self.shadow_visible:
            self.shadow_animation.setStartValue(180)
            self.shadow_animation.setEndValue(0)
            print(f"[TOGGLE] Shadow fading OUT: 180 -> 0")
        else:
            self.shadow_animation.setStartValue(0)
            self.shadow_animation.setEndValue(180)
            print(f"[TOGGLE] Shadow fading IN: 0 -> 180")

        print(f"[TOGGLE] Before starting animations: {self.geometry()}")

        # Start both animations
        self.opacity_animation.start()
        self.shadow_animation.start()

        print(f"[TOGGLE] After starting animations: {self.geometry()}")

        self.is_faded = not self.is_faded
        self.shadow_visible = not self.shadow_visible
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Stacked Effects Demo")
        self.setGeometry(100, 100, 600, 450) # Increased height slightly for better spacing
        self.setStyleSheet("QMainWindow { background-color: #1e1e1e; }")

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Title
        title = QLabel("Stacked Effects: Drop Shadow + Opacity Animation")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # --- START OF FIX ---
        # A single container to hold the absolutely positioned widgets.
        # This container has no layout itself, so it won't interfere.
        demo_area = QWidget()
        demo_area.setFixedSize(400, 300) # Give it a fixed size

        # Create the animated frame and set its parent to our new container
        self.animated_frame = CustomShadowFrame(demo_area)
        print(f"[MAIN] Frame created with geometry: {self.animated_frame.geometry()}")

        # Force the frame to process events and settle before moving
        QApplication.processEvents()

        # Center the frame within the container: (400-300)/2 = 50
        self.animated_frame.move(50, 20)
        print(f"[MAIN] After move(50, 20): {self.animated_frame.geometry()}")

        # Force another event processing cycle
        QApplication.processEvents()
        print(f"[MAIN] After processEvents: {self.animated_frame.geometry()}")

        # Create the button and parent it to the container as well
        toggle_button = QPushButton("Toggle Effects", demo_area)
        toggle_button.setFixedSize(200, 45)
        # Center the button horizontally: (400-200)/2 = 100
        toggle_button.move(100, 240)
        toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; border: none;
                padding: 10px; border-radius: 8px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:pressed { background-color: #219a52; }
        """)
        toggle_button.clicked.connect(self.animated_frame.toggle_effects)

        # Add the container (with its absolutely positioned children) to the main layout.
        # The main layout will manage the position of demo_area, but not its children.
        main_layout.addWidget(demo_area, 0, Qt.AlignmentFlag.AlignCenter)
        # --- END OF FIX ---

        # Info label
        info = QLabel("""
<b>Custom Shadow Implementation:</b>
• Hand-painted shadow using QPainter in paintEvent()
• Multi-layer shadow rendering for blur effect
• Opacity animation on inner content only
• No QGraphicsEffect jumping issues
        """)
        info.setStyleSheet("""
            color: #888888; font-size: 11px; padding: 15px;
            background-color: #2a2a2a; border-radius: 8px; margin: 0 20px;
        """)
        main_layout.addWidget(info)
        main_layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
