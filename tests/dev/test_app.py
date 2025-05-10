#🔸System Imports
import sys

#🔸Local Imports
# Use the new slot widget and enum
from dev_sandbox.recipe_widget.recipe_slot import LayoutSize, RecipeWidget
# Debug logging
from helpers.app_helpers.debug_logger import DebugLogger
from PySide6.QtCore import Qt
#🔸Third-party Imports
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QScrollArea,
                               QVBoxLayout, QWidget)

# Load stylesheet helper
from core.helpers.app_helpers import load_stylesheet_for_widget
# Database
from database.database import DB_INSTANCE
# Recipe model
from database.modules.recipe_module import Recipe


# --- Fetch Recipe Data from DB ---
def fetch_recipes_for_test(recipe_ids: list[int]) -> dict[int, Recipe]:
    """Fetch and wrap recipes from the DB."""
    fetched: dict[int, Recipe] = {}
    if not DB_INSTANCE:
        DebugLogger.log("DB_INSTANCE is not available. Cannot fetch recipes.", "error")
        return fetched

    for rid in recipe_ids:
        try:
            data = DB_INSTANCE.get_recipe(rid)
            if data:
                fetched[rid] = Recipe(data)
                DebugLogger.log(f"Fetched recipe ID {rid}", "info")
            else:
                DebugLogger.log(f"Recipe ID {rid} not found", "warning")
        except Exception as e:
            DebugLogger.log(f"Error fetching recipe {rid}: {e}", "error", exc_info=True)
    return fetched

def create_test_widget(recipes: dict[int, Recipe]) -> QWidget:
    """
    Build a vertical list of rows, each showing:
      - one empty slot
      - up to two slots with recipes loaded
    for each LayoutSize (SMALL, MEDIUM, LARGE).
    """
    container = QWidget()
    main_lyt = QVBoxLayout(container)
    main_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_lyt.setSpacing(20)

    sizes = [LayoutSize.SMALL, LayoutSize.MEDIUM, LayoutSize.LARGE]
    recipe_ids = list(recipes.keys())[:2]  # show at most two recipes per size

    for size in sizes:
        # Section label
        lbl = QLabel(f"{size.name.capitalize()} Size ({size.value})")
        main_lyt.addWidget(lbl)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row.setSpacing(15)

        # 1) Empty slot
        empty_slot = RecipeWidget(size)
        row.addWidget(empty_slot)

        # 2) Up to two filled slots
        for rid in recipe_ids:
            recipe = recipes.get(rid)
            if recipe:
                slot = RecipeWidget(size)
                slot.set_recipe(recipe)
                row.addWidget(slot)
            else:
                DebugLogger.log(f"Skipping missing recipe {rid} for size {size}", "warning")

        main_lyt.addLayout(row)

    main_lyt.addStretch(1)
    return container

def run_test(app):
    # IDs to test—adjust as needed
    ids_to_load = [1, 2, 3]
    live_recipes = fetch_recipes_for_test(ids_to_load)

    if not live_recipes:
        DebugLogger.log("No recipes loaded; slots will remain empty or show errors.", "critical")

    win = QScrollArea()
    win.setWindowTitle("RecipeWidget Refactor Test")
    win.setWidgetResizable(True)
    win.setMinimumSize(1000, 800)

    content = create_test_widget(live_recipes)
    win.setWidget(content)
    win.show()

    load_stylesheet_for_widget(win, "dev_sandbox/recipe_widget/stylesheet.qss")
    return win

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not DB_INSTANCE:
        print("ERROR: DB_INSTANCE not initialized.")
        sys.exit(1)
    test_win = run_test(app)
    sys.exit(app.exec())
