"""ui/tools.form_helpers.py
This module contains helper functions for populating UI elements in PySide6 applications."""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QComboBox


def populate_combobox(combobox: QComboBox, *values):
    """
    Populates a QComboBox with the provided values.

    Args:
        combobox (QComboBox): The combobox to populate.
        *values (str or list): A list of values or multiple string arguments.
    """
    if len(values) == 1 and isinstance(values[0], list):
        values = values[0]  # Unpack list if a single list argument is passed

    combobox.clear()
    combobox.addItems(values)
