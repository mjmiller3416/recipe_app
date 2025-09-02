"""MealGenie - A Meal Planning Application (v2 with new navigation)
This script initializes and runs the MealGenie application, setting up the main window,
database, and handling command-line arguments for special modes like testing and importing recipes.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import os

os.environ["QT_FONT_DPI"] = "96"
import sys

import qframelesswindow.utils.win32_utils
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# Force-disable the border accent globally in the library
qframelesswindow.utils.win32_utils.isSystemBorderAccentEnabled = lambda: False
from app.style.theme_controller import  Mode, Theme
from app.ui.main_window_v2 import MainWindow  # New main window with v2 navigation
from _dev_tools import DebugLogger, startup_timer
from dotenv import load_dotenv

if "--reset" in sys.argv:
        pass

elif "--test" in sys.argv:
    DebugLogger.log("Launching in TEST MODE...\\n", "info")

    app = QApplication(sys.argv)
    app.setApplicationName("Test App")

    from _dev_tools.test_harness import TestHarness
    TestHarness.launch_from_test_file(app)

    sys.exit(app.exec())

elif "--import-recipes" in sys.argv:
    DebugLogger.log("Importing recipes from CSV...\\n", "info")

    # ── Import Recipes ──
    from _scripts.db.recipes_with_ingredients import insert_recipes_from_csv
    insert_recipes_from_csv("database/recipes_with_ingredients.csv")

    DebugLogger().log("Recipe import complete.\\n", "success")

# ── Application Entry Point ──
else:
    load_dotenv()

    app = QApplication(sys.argv)
    app.setApplicationName("MealGenie")
    app.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor  # or RoundPreferFloor
)
    DebugLogger.set_log_level("info")
    DebugLogger.log("Starting MealGenie application...\\n", "info")

    #Theme.setTheme(Color.TEAL, Mode.DARK)

    # ── Custom Color Map ──
    Theme.setCustomColorMap("material-theme.json", Mode.DARK)

    # ── Create Main Window with New Navigation System ──
    # No more navigation_service_factory needed - handled internally
    main_window = MainWindow()

    # Show the window in normal size first to establish restore geometry
    main_window.show()
    # Then immediately maximize to get the desired startup appearance
    #main_window.showMaximized()
    # Sync the window animator state with the actual maximized state
    main_window.animator._is_maximized = False
    main_window.title_bar.update_maximize_icon(False)

    # ── Simple QSS Inspector ──
    # Uncomment the lines below to enable the simple terminal-based QSS inspector
    from _dev_tools.qss_inspector import enable_qss_inspector
    inspector = enable_qss_inspector(app, main_window)

    QApplication.processEvents()  # make sure all pending events are flushed
    startup_timer.StartupTimer.summary("MealGenie startup") # log total startup time

    sys.exit(app.exec())
