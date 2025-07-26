"""MealGenie - A Meal Planning Application
This script initializes and runs the MealGenie application, setting up the main window,
database, and handling command-line arguments for special modes like testing and importing recipes.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import os

os.environ["QT_FONT_DPI"] = "96"
import sys

from PySide6.QtWidgets import QApplication

from app.theme_manager.theme import Color, Mode, Theme
from app.ui.main_window import MainWindow
from app.ui.services.navigation_service import NavigationService
from dev_tools import DebugLogger, startup_timer

if "--reset" in sys.argv:
        pass

elif "--test" in sys.argv:
    DebugLogger.log("Launching in TEST MODE...\n", "info")

    app = QApplication(sys.argv)
    app.setApplicationName("Test App")

    from dev_tools.test_harness import TestHarness
    TestHarness.launch_from_test_file(app)

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
    DebugLogger.set_log_level("info")
    DebugLogger.log("Starting MealGenie application...\n", "info")

    Theme.setTheme(Color.GRAY, Mode.DARK)
    navigation_service_factory = NavigationService.create

    main_window = MainWindow(
        navigation_service_factory=navigation_service_factory
    )
    main_window.show() # show the main window

    QApplication.processEvents()  # make sure all pending events are flushed
    startup_timer.StartupTimer.summary("MealGenie startup") # log total startup time

    sys.exit(app.exec())
