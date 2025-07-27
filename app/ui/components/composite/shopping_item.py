"""app/ui/components/composite/shopping_item.py

This module defines a composite widget for displaying individual shopping list items,
including a checkbox to mark items as obtained and a label showing item details.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

from dev_tools import DebugLogger


# ── Shopping Item Widget ─────────────────────────────────────────────────────────────────────
class ShoppingItemWidget(QWidget):
    def __init__(self, item, shopping_svc, breakdown_map, parent=None):
        """Initialize the ShoppingItemWidget.

        Args:
            item: The shopping item data object.
            shopping_svc: Service to manage shopping list operations.
            breakdown_map: Mapping of recipe ingredients for tooltips.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.item = item
        self.shopping_svc = shopping_svc
        self.breakdown_map = breakdown_map

        # ── Create Widgets ──
        self.checkbox = QCheckBox()
        self.label = QLabel()

        # ── Configure Widgets ──
        unit_display = f" {self.item.unit}" if self.item.unit else ""
        self.plain_text = f"{self.item.ingredient_name}: {self.item.formatted_quantity()}{unit_display}"

        self.label.setTextFormat(Qt.RichText)

        self.checkbox.setChecked(self.item.have)
        self._update_label_style() # set initial style after checkbox state is set
        self._set_tooltip_if_needed() # set tooltip after label text is finalized

        # ── Layout ──
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)

        # ── Connections ──
        self.checkbox.stateChanged.connect(self.on_toggled)

    def on_toggled(self, state):
        """Handle the toggle action."""
        if self.shopping_svc:
            self.shopping_svc.toggle_item_status(self.item.id)
        self._update_label_style()

    def _update_label_style(self):
        """Apply or remove strike-through based on checkbox state."""
        if self.checkbox.isChecked():
            self.label.setText(f"<s>{self.plain_text}</s>")
        else:
            self.label.setText(self.plain_text)

        # Always ensure tooltip is set after text change
        self._set_tooltip_if_needed()

    def _set_tooltip_if_needed(self):
        """Sets the recipe breakdown tooltip."""
        DebugLogger.log("Setting tooltip for ingredient {ingredient_name}, source: {source}, key: {key}", "debug", ingredient_name=self.item.ingredient_name, source=self.item.source, key=self.item.key())

        if self.item.source == "recipe":
            parts = self.breakdown_map.get(self.item.key(), [])
            DebugLogger.log("Found {count} parts in breakdown_map for ingredient", "debug", count=len(parts))
            if parts:
                # Create a more readable tooltip format
                header = f"Used in {len(parts)} recipe(s):"
                recipe_lines = [f"• {qty} {unit} - {name}" for name, qty, unit in parts]
                text = f"{header}\n" + "\n".join(recipe_lines)
                DebugLogger.log("Setting ingredient tooltip: {text}", "debug", text=text)
                self.label.setToolTip(text)
            else:
                DebugLogger.log("No recipe parts found for ingredient, skipping tooltip", "debug")
        else:
            DebugLogger.log("Non-recipe shopping item, no tooltip needed", "debug")
