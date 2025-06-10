""" main.py 

This module serves as the main entry point for the MealGenie application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import sys

from PySide6.QtWidgets import QApplication

from core.application import Application
from core.helpers import DebugLogger
from database.db_reset import reset_database
from database.init_db import init_db
from ui.tools.layout_debugger import LayoutDebugger




# ── Class Definition ────────────────────────────────────────────────────────────
class MealPlannerApp:
    """
    Main application class for MealGenie.

    Attributes:
        app (QApplication): The PySide6 application instance.
        main_window (Application): The main application window.

    Methods:
        run(): Starts the application's main event loop.
    """

    def __init__(self):
        """
        Initialize the application:
        - PySide6 UI setup.
        - Database initialization.
        - Theme loading.
        """
        

        # ── Initialize Application ──
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MealGenie")
        init_db() # initialize the database

        # ── Apply Theme ──
        #self.style_manager = StyleManager(self.app) # TODO: Refactor to use core/controllers/theme_controller.py

        # ── Setup Window ──
        self.main_window = Application()
        self.main_window.setWindowTitle("MealGenie")
        self.main_window.resize(1330, 800)
        self.main_window.show()

    def run(self):
        """ Run the application's main event loop. """
        DebugLogger().log("Application initializing...\n", "info")
        sys.exit(self.app.exec())

if "--reset" in sys.argv:
        reset_database()

elif "--test" in sys.argv:
    print("Launching in TEST MODE...\n")

    # ── Test Setup ──
    app = QApplication(sys.argv)
    app.setApplicationName("Test App")
    
    from style_manager.theme_controller import ThemeController
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

else:
    # ── Regular Launch ──
    app = MealPlannerApp()
    app.run()
