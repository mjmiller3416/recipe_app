import os
import sys
import re

# ── Config ─────────────────────────────────────────────────────────────
BASE_DIR = r"G:\My Drive\Python\recipe_app\tests\dev"

# ── Helpers ─────────────────────────────────────────────────────────────
def camel_to_snake(name: str) -> str:
    """Converts CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def get_input_with_default(prompt: str, default: str) -> str:
    """Prompts user input with a default value."""
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

def create_template_file(class_name: str, file_path: str) -> None:
    """Creates a new Python file with the test class template."""
    with open(file_path, "w") as f:
        f.write(f'''"""Test script for {class_name}."""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

class {class_name}(QMainWindow):
    """A test class for development testing."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("{class_name}")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set layout (QMainWindow requires this!)
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        # Example content
        label = QLabel("Hello from {class_name}!")
        central_layout.addWidget(label)

        self.setCentralWidget(central_widget)  # Essential to avoid warnings

        self.show()

def run_test(app):
    """Runs the test window."""
    window = {class_name}(app)
    return window
''')

    print(f"\n[OK] Created: {file_path}\n")

# ── Main Execution ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🛠️  Test Class Generator")
    print("─────────────────────────────────────────────")
    print("This script will create a template test class file.")
    print("You can press backspace and re-enter the name if you change your mind.\n")

    while True:
        class_name = get_input_with_default("Enter class name", "MyTestApp")
        file_name = camel_to_snake(class_name) + ".py"
        file_path = os.path.join(BASE_DIR, file_name)

        if os.path.exists(file_path):
            choice = input(f"⚠️  File '{file_name}' already exists. Overwrite? (y/n): ").strip().lower()
            if choice == "y":
                create_template_file(class_name, file_path)
                break
            else:
                print("Let's try a new name!\n")
        else:
            create_template_file(class_name, file_path)
            break
