"""MealGenie - A Meal Planning Application
This script initializes and runs the MealGenie application, setting up the main window,
database, and handling command-line arguments for special modes like testing and importing recipes.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import os
os.environ["QT_FONT_DPI"] = "96"
import sys

from PySide6.QtWidgets import QApplication

from dev_tools import startup_timer
from alembic.config import Config
from alembic import command
from pathlib import Path
from app.core.services.navigation_service import NavigationService
from dev_tools import DebugLogger
from app.style_manager import ThemeController
from app.ui import MainWindow

ALEMBIC_CFG = Config(str(Path(__file__).parent / "alembic.ini"))

def upgrade_db() -> None:
    """Apply any pending Alembic migrations."""
    command.upgrade(ALEMBIC_CFG, "head")

if "--reset" in sys.argv:
    db_path = Path(ALEMBIC_CFG.get_main_option("sqlalchemy.url").replace("sqlite:///", ""))
    if db_path.exists():
        db_path.unlink()
    upgrade_db()

elif "--test" in sys.argv:
    DebugLogger.log("Launching in TEST MODE...\n", "info")

    app = QApplication(sys.argv)
    app.setApplicationName("Test App")

    theme_controller = ThemeController()
    theme_controller.apply_full_theme()

    from dev_tools.test_harness import TestHarness
    TestHarness.launch_from_test_file(app)

    sys.exit(app.exec())

elif "--import-recipes" in sys.argv:
    DebugLogger.log("Importing legacy recipes...\n", "info")
    from scripts.migrate_legacy_data import main as migrate_legacy
    migrate_legacy()
    DebugLogger().log("Recipe import complete.\n", "success")

# ── Application Entry Point ──
else:
    app = QApplication(sys.argv)
    app.setApplicationName("MealGenie")
    DebugLogger.log("Starting MealGenie application...\n", "info")
    upgrade_db()

    theme_controller = ThemeController() 
    
    navigation_service_factory = NavigationService.create

    main_window = MainWindow(
        theme_controller=theme_controller,
        navigation_service_factory=navigation_service_factory
    )
    main_window.show() # show the main window

    QApplication.processEvents()  # make sure all pending events are flushed
    startup_timer.StartupTimer.summary("MealGenie startup") # log total startup time

    sys.exit(app.exec())