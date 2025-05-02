# Description: Main entry point for the MealGenie application.

#🔸System Imports
import sys

from helpers.app_helpers.debug_logger import DebugLogger
from PySide6.QtCore import QCoreApplication
#🔸Third-Party Imports
from PySide6.QtWidgets import QApplication

#🔸Local Imports
from core.application import Application
from core.controllers import StyleManager
from database import DB_INSTANCE
from database.initialize_db import reset_to_version
from ui.tools.layout_debugger import DebugLayout


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

        # Initialize the PySide6 application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MealGenie")

        # Apply the stylesheet
        self.style_manager = StyleManager(self.app)

        # Set up the main application window
        self.main_window = Application()
        self.main_window.setWindowTitle("MealGenie")
        self.main_window.resize(1330, 800)
        self.main_window.show()

    def run(self):
        """
        Run the application's main event loop.
        """
        DebugLogger().log("Application initializing...\n", "info")
        sys.exit(self.app.exec())

if "--reset" in sys.argv:
    print("Resetting database...")
    db_path = "database/app_data.db"
    sql_file = "database/db_tables.sql"

    # Ensure database connection is closed before reset
    DB_INSTANCE.close_connection()

    # Perform the reset
    reset_to_version(db_path, sql_file)
    DebugLogger().log("Database reset complete.\n", "info")

elif "--test" in sys.argv:
    print("Launching in TEST MODE...\n")

    # 🔹 Minimal test setup (no main window!)
    app = QApplication(sys.argv)
    app.setApplicationName("Test App")

    # 🔹 Initialize DB + Styles (just like MealPlannerApp does)
    DB_INSTANCE.connect()  # Just in case
    StyleManager(app)

    # 🔹 Run your test harness
    from dev_sandbox.test_app import run_test
    test_window = run_test(app)

    sys.exit(app.exec())

elif "--import-recipes" in sys.argv:
    print("Importing recipes from CSV...\n")

    # 🔹 Initialize minimal app environment (optional if needed)
    DB_INSTANCE.connect()

    # 🔹 Import your function
    from scripts.db.recipes_with_ingredients import insert_recipes_from_csv

    # 🔹 Run it!
    insert_recipes_from_csv("database/recipes_with_ingredients.csv")

    DebugLogger().log("✅ Recipe import complete.\n", "success")

else:
    # Regular launch
    app = MealPlannerApp()
    app.run()
