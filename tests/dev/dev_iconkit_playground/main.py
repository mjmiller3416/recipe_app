import sys
from pathlib import Path

# Dynamically add the project root to sys.path
project_root = Path(__file__).resolve().parents[3]  # adjust if your nesting changes
sys.path.insert(0, str(project_root))

from icon_test_window import IconTestWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IconTestWindow()
    window.show()
    sys.exit(app.exec())
