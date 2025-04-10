# Package: MealGenie

# Description: Main entry point for the MealGenie application.
# This file initializes the PySide6 application, sets up the database, and runs the main event loop.

#🔸System Imports
import sys 

#🔸Third-Party Imports
from core.helpers.qt_imports import QApplication

#🔸Local Imports
from core.application import Application
from database import DB_INSTANCE
from database.initialize_db import reset_to_version
from core.managers import StyleManager
from core.helpers import DebugLogger

class MealPlannerApp:
    """
    Main application class for the Meal Planner using PySide6.
    Sets up the UI, database, and application logic.
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
    db_path = "app/database/app_data.db"
    sql_file = "app/database/db_tables.sql"

    # Ensure database connection is closed before reset
    DB_INSTANCE.close_connection()

    # Perform the reset
    reset_to_version(db_path, sql_file)
    DebugLogger().log("Database reset complete.\n", "info")

else:
    # Entry point: Create and run the Meal Planner application
    app = MealPlannerApp()
    app.run()