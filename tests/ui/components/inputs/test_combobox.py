"""tests.ui.components.inputs.test_combobox

This module contains the unit tests for the ComboBox widget.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from app.ui.components.inputs.combobox import ComboBox

# ── Constants ───────────────────────────────────────────────────────────────────
INITIAL_ITEMS = ["Apple", "Banana", "Cherry"]
PLACEHOLDER_TEXT = "Select a fruit"

# ── Fixtures ────────────────────────────────────────────────────────────────────
@pytest.fixture
def combobox(qtbot: QtBot) -> ComboBox:
    """Fixture to create a ComboBox instance with initial items."""
    widget = ComboBox(list_items=INITIAL_ITEMS, placeholder=PLACEHOLDER_TEXT)
    qtbot.addWidget(widget)
    return widget

# ── Test Cases ──────────────────────────────────────────────────────────────────
class TestComboBox:
    """Test cases for the ComboBox widget."""

    def test_initialization(self, combobox: ComboBox):
        """Test the initial state of the ComboBox."""
        assert combobox.line_edit.placeholderText() == PLACEHOLDER_TEXT
        assert combobox.model.stringList() == INITIAL_ITEMS
        assert combobox.currentText() == ""

    def test_set_current_text(self, combobox: ComboBox, qtbot: QtBot):
        """Test setting the current text and signal emission."""
        with qtbot.waitSignals([combobox.currentTextChanged, combobox.selection_validated]):
            combobox.setCurrentText("Banana")
        
        assert combobox.currentText() == "Banana"

    def test_set_current_index(self, combobox: ComboBox, qtbot: QtBot):
        """Test setting the current index."""
        with qtbot.waitSignal(combobox.selection_validated):
            combobox.setCurrentIndex(2)
        
        assert combobox.currentText() == "Cherry"

    def test_set_invalid_index(self, combobox: ComboBox, qtbot: QtBot):
        """Test setting an invalid index."""
        with qtbot.waitSignal(combobox.selection_validated):
            combobox.setCurrentIndex(99)
        
        assert combobox.currentText() == ""

    def test_find_text(self, combobox: ComboBox):
        """Test finding text in the ComboBox."""
        assert combobox.findText("Banana") == 1
        assert combobox.findText("cherry", flags=Qt.MatchContains) == 2
        assert combobox.findText("Grape") == -1

    def test_add_item(self, combobox: ComboBox):
        """Test adding a new item."""
        combobox.addItem("Date")
        assert combobox.model.rowCount() == 4
        assert combobox.model.stringList()[-1] == "Date"

    def test_add_existing_item(self, combobox: ComboBox):
        """Test adding an existing item."""
        combobox.addItem("Apple")
        assert combobox.model.rowCount() == 3

    def test_popup_expands_on_click(self, combobox: ComboBox, qtbot: QtBot):
        """Popup should be visible when clicking anywhere on the widget."""
        qtbot.mouseClick(combobox.line_edit, Qt.LeftButton)
        assert combobox.completer.popup().isVisible()
