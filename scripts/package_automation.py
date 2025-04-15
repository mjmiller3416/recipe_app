import os

# Define paths
BASE_DIR = "app/widgets"  # Adjust based on your project structure

# Template for the Python class
CLASS_TEMPLATE = """# Third-party Imports
from qt_imports import QWidget

# Local Imports
from app.widgets.{folder_name}.ui_{class_name_snake} import Ui_{class_name}

class {class_name}(QWidget):
    \"\"\"
    {class_name} class for displaying a compact view of a recipe.
    \"\"\"
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load UI
        self.ui = Ui_{class_name}()
        self.ui.setupUi(self)

        # Set Object Name
        self.setObjectName("{class_name}")
"""

# Template for __init__.py
INIT_TEMPLATE = """\"\"\"
Initialization file for the {folder_name} package.

This module initializes the {class_name} and its associated UI components.
\"\"\"

# Import the main class
from .{class_name_snake} import {class_name}

# Import the UI form
from .ui_{class_name_snake} import Ui_{class_name}
"""

def to_snake_case(name):
    """Converts PascalCase to snake_case."""
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")

def create_widget_structure(class_name):
    """Creates the necessary folder and files for a new widget."""
    class_name_snake = to_snake_case(class_name)
    folder_name = class_name_snake

    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create __init__.py
    init_path = os.path.join(folder_path, "__init__.py")
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(INIT_TEMPLATE.format(class_name=class_name, class_name_snake=class_name_snake, folder_name=folder_name))

    # Create the main class file
    class_path = os.path.join(folder_path, f"{class_name_snake}.py")
    with open(class_path, "w", encoding="utf-8") as f:
        f.write(CLASS_TEMPLATE.format(class_name=class_name, class_name_snake=class_name_snake, folder_name=folder_name))

    print(f"✅ Widget structure created for {class_name} at {folder_path}")

    # Print file associations for easy copy-paste
    print("\n🔹 Copy and paste the following into settings.json:\n")
    print(f'"material-icon-theme.folders.associations": {{')
    print(f'    "{class_name_snake}": "class"')
    print(f'}},\n')

    print(f'"material-icon-theme.files.associations": {{')
    print(f'    "{class_name_snake}.py": "python",')
    print(f'    "ui_{class_name_snake}.py": "Apiblueprint"')
    print(f'}}\n')

def main():
    class_name = input("Enter the new widget class name (e.g., MiniRecipeCard): ").strip()
    create_widget_structure(class_name)
    print("🎉 Automation complete!")

if __name__ == "__main__":
    main()
