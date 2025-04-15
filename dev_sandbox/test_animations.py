from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QFrame
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup, QSequentialAnimationGroup, QTimer,
    QPoint
)
import sys


class AnimatedDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Animation Demo")
        self.setGeometry(100, 100, 500, 400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1️⃣ Fade-In Button
        self.fade_button = QPushButton("Fade Me In")
        self.fade_button.setVisible(False)
        layout.addWidget(self.fade_button)

        self.fade_button.clicked.connect(self.wiggle_me)

        # 2️⃣ Slide-In Widget
        self.slide_label = QLabel("Slide Into View")
        self.slide_label.setStyleSheet("background-color: #03B79E; color: white; padding: 10px;")
        self.slide_label.setFixedWidth(200)
        layout.addWidget(self.slide_label)
        self.slide_label.move(-300, 50)  # Start off-screen

        # 3️⃣ Collapsible Panel
        self.panel = QFrame()
        self.panel.setFrameShape(QFrame.Box)
        self.panel.setStyleSheet("background-color: #3B575B;")
        self.panel.setFixedHeight(0)
        layout.addWidget(self.panel)

        self.toggle_btn = QPushButton("Toggle Panel")
        layout.addWidget(self.toggle_btn)
        self.toggle_btn.clicked.connect(self.toggle_panel)

        # Start animations
        QTimer.singleShot(500, self.run_animations)

    def run_animations(self):
        # Fade-In
        self.fade_button.setVisible(True)
        effect = QGraphicsOpacityEffect(self.fade_button)
        self.fade_button.setGraphicsEffect(effect)

        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(1000)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)

        # Slide-In
        slide_anim = QPropertyAnimation(self.slide_label, b"pos")
        slide_anim.setDuration(1000)
        slide_anim.setStartValue(self.slide_label.pos())
        slide_anim.setEndValue(self.slide_label.pos() + QPoint(300, 0))
        slide_anim.setEasingCurve(QEasingCurve.OutBounce)

        # Run together
        group = QParallelAnimationGroup()
        group.addAnimation(fade_anim)
        group.addAnimation(slide_anim)
        group.start()

    def wiggle_me(self):
        start_x = self.fade_button.x()
        wiggle = QSequentialAnimationGroup()

        for offset in [15, -15, 10, -10, 5, -5, 0]:
            anim = QPropertyAnimation(self.fade_button, b"pos")
            anim.setDuration(50)
            anim.setEndValue(self.fade_button.pos() + Qt.QPoint(offset, 0))
            wiggle.addAnimation(anim)
        wiggle.start()
        
    def toggle_panel(self):
        collapsed = self.panel.height() == 0
        new_height = 100 if collapsed else 0

        anim = QPropertyAnimation(self.panel, b"maximumHeight")
        anim.setDuration(400)
        anim.setStartValue(self.panel.height())
        anim.setEndValue(new_height)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AnimatedDemo()
    demo.show()
    sys.exit(app.exec())
