# test_application_window.py

from PySide6.QtWidgets import QApplication, QLabel
from ui.components.dialogs.application_window import ApplicationWindow

import sys


def main():
    app = QApplication(sys.argv)

    # ── Initialize Your Custom Window ──
    window = ApplicationWindow(width=800, height=500)

    # ── Add Some Sample Content ──
    label = QLabel("🎉 Hello from ApplicationWindow!", window.body)
    label.setStyleSheet("font-size: 18px; color: white;")
    window.content_layout.addWidget(label)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
