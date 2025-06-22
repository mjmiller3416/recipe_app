"""MealGenie - A Meal Planning Application
This script initializes and runs the MealGenie application, setting up the main window,
database, and handling command-line arguments for special modes like testing and importing recipes.
"""

import os
# ── Imports ─────────────────────────────────────────────────────────────────────
import sys

from PySide6.QtWidgets import QApplication

os.environ["QT_FONT_DPI"] = "96"

from app.core.data.db_reset import reset_database
from app.core.data.init_db import init_db
from app.core.services import NavigationService, RecipeService
from app.core.utils import DebugLogger
from app.style_manager import ThemeController
from app.ui import MainWindow

if "--reset" in sys.argv:
        reset_database()

elif "--test" in sys.argv:
    print("Launching in TEST MODE...\n")

    # ── Test Setup ──
    app = QApplication(sys.argv)
    app.setApplicationName("Test App")
    
    
    theme_controller = ThemeController()
    theme_controller.apply_full_theme()

    from tests.dev.my_test_app import run_test
    test_window = run_test(app)

    sys.exit(app.exec())

elif "--import-recipes" in sys.argv:
    DebugLogger.log("Importing recipes from CSV...\n", "info")

    # ── Import Recipes ──
    from scripts.db.recipes_with_ingredients import insert_recipes_from_csv
    insert_recipes_from_csv("database/recipes_with_ingredients.csv")

    DebugLogger().log("Recipe import complete.\n", "success")

# ── Application Entry Point ──
else:
    app = QApplication(sys.argv)
    app.setApplicationName("MealGenie")
    DebugLogger.log("Starting MealGenie application...\n", "info")
    init_db()
    RecipeService.initialize_cache()

    theme_controller = ThemeController() 
    
    navigation_service_factory = NavigationService.create

    main_window = MainWindow(
        theme_controller=theme_controller,
        navigation_service_factory=navigation_service_factory
    )

    main_window.show()
    sys.exit(app.exec())