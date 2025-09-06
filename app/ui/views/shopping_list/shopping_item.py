"""app/ui/views/shopping_list/shopping_item.py

Shopping item widget for displaying individual items in the shopping list.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

class ShoppingItem(QWidget):
    """Widget representing a single shopping list item.

    Displays item name, quantity, and unit with a checkbox for marking
    as obtained. Shows recipe breakdown in tooltip when applicable.

    Signals:
        itemChecked: Emitted when item's checkbox state changes.
    """

    itemChecked = Signal(str, bool)

    def __init__(self, item, view_model, breakdown_map, parent=None):
        """Initialize the ShoppingItem.

        Args:
            item: The shopping item data object.
            view_model: ViewModel to handle shopping operations.
            breakdown_map: Mapping of recipe ingredients for tooltips.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.item = item
        self.view_model = view_model
        self.breakdown_map = breakdown_map

        # Create widgets
        self.checkbox = QCheckBox()
        self.label = QLabel()
        self.label.setObjectName("ShoppingItem")

        # Configure display text with quantity and unit
        unit_display = f" {self.item.unit}" if self.item.unit else ""
        self.plain_text = f"{self.item.ingredient_name}: {self.item.formatted_quantity()}{unit_display}"

        self.label.setTextFormat(Qt.RichText)

        # Initialize checkbox state and apply styling
        self.checkbox.setChecked(self.item.have)
        self._update_label_style()  # Apply strikethrough if already obtained
        self._set_tooltip_if_needed()  # Add recipe breakdown tooltip

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)

        # Connections
        self.checkbox.stateChanged.connect(self.onToggled)

        # Track signal connections for cleanup
        self._signal_connections = [
            (self.checkbox.stateChanged, self.onToggled)
        ]

    # ── Lifecycle Methods ───────────────────────────────────────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Clean up signal connections to prevent memory leaks."""
        for signal, slot in self._signal_connections:
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass  # Signal already disconnected or object deleted
        self._signal_connections.clear()

    # ── Private Methods ─────────────────────────────────────────────────────────────────────────────────────

    def _update_label_style(self) -> None:
        """Apply or remove strike-through based on checkbox state."""
        if self.checkbox.isChecked():
            self.label.setText(f"<s>{self.plain_text}</s>")
        else:
            self.label.setText(self.plain_text)

        # Re-apply tooltip after text change to maintain consistency
        self._set_tooltip_if_needed()

    def _set_tooltip_if_needed(self) -> None:
        """Set recipe breakdown tooltip for recipe-sourced items.

        Shows which recipes use this ingredient and in what quantities.
        """
        if self.item.source == "recipe":
            parts = self.breakdown_map.get(self.item.key(), [])
            if parts:
                # Format tooltip with recipe breakdown for clarity
                header = f"Used in {len(parts)} recipe(s):"
                recipe_lines = [f"• {qty} {unit} - {name}" for name, qty, unit in parts]
                text = f"{header}\n" + "\n".join(recipe_lines)
                self.label.setToolTip(text)

    # ── Event Handlers ──────────────────────────────────────────────────────────────────────────────────────

    def onToggled(self, state: int) -> None:
        """Handle checkbox toggle event.

        Args:
            state: Qt checkbox state value.
        """
        if self.view_model:
            self.view_model.toggle_item_status(self.item.id)
        self._update_label_style()

        # Notify parent category of state change
        self.itemChecked.emit(self.item.ingredient_name, self.checkbox.isChecked())
