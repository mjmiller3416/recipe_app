import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from pytestqt.qtbot import QtBot

import importlib.util
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "ingredient_widget",
    ROOT_DIR / "app" / "ui" / "components" / "forms" / "ingredient_widget.py",
)
ingredient_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingredient_module)
IngredientWidget = ingredient_module.IngredientWidget


@pytest.fixture
def ingredient_widget(qtbot: QtBot) -> IngredientWidget:
    widget = IngredientWidget()
    qtbot.addWidget(widget)
    return widget


def test_emit_ingredient_data(ingredient_widget: IngredientWidget, qtbot: QtBot):
    ingredient_widget.le_quantity.setText("1.5")
    ingredient_widget.cb_unit.setCurrentText("cup")
    ingredient_widget.sle_ingredient_name.line_edit.setText("Sugar")
    ingredient_widget.cb_ingredient_category.setCurrentText("baking")

    with qtbot.waitSignal(ingredient_widget.ingredient_validated) as blocker:
        ingredient_widget.emit_ingredient_data()

    payload = blocker.args[0]
    assert payload["quantity"] == 1.5
    assert payload["unit"] == "cup"
    assert payload["ingredient_name"] == "Sugar"
    assert payload["ingredient_category"] == "baking"


def test_add_ingredient_signal(ingredient_widget: IngredientWidget, qtbot: QtBot):
    with qtbot.waitSignals([ingredient_widget.ingredient_validated, ingredient_widget.add_ingredient_requested]):
        qtbot.mouseClick(ingredient_widget.btn_ico_add, Qt.LeftButton)


def test_remove_ingredient_signal(qtbot: QtBot):
    container = QWidget()
    layout = QVBoxLayout(container)
    w1 = IngredientWidget()
    w2 = IngredientWidget()
    layout.addWidget(w1)
    layout.addWidget(w2)
    qtbot.addWidget(container)

    with qtbot.waitSignal(w2.remove_ingredient_requested):
        qtbot.mouseClick(w2.btn_ico_subtract, Qt.LeftButton)
