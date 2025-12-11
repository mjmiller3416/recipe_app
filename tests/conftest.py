import importlib.util
import os
from pathlib import Path
import sys

import pytest
from PySide6.QtWidgets import QApplication


def _load_recipe_models():
    module_path = Path(__file__).resolve().parents[1] / "app" / "ui" / "views" / "recipe_browser" / "models.py"
    spec = importlib.util.spec_from_file_location("recipe_browser_models", module_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("Failed to load recipe browser models module.")
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session", autouse=True)
def qt_app():
    """Provide a QApplication for Qt-dependent tests."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="session")
def recipe_models():
    """Load recipe browser models module without pulling in heavy view imports."""
    return _load_recipe_models()
