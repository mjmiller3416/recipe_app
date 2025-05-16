
# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QComboBox, 
    QPushButton, QScrollArea, QFrame, QCheckBox
)

# ── Class Definition ────────────────────────────────────────────────────────────
class ShoppingList(QWidget):
    """Placeholder class for the ShoppingList screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize & Setup UI
        self.setObjectName("ShoppingList")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumSize(984, 818)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # ── Manual Add Section ──
        add_bar = QHBoxLayout()

        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Qty")
        self.input_qty.setFixedWidth(60)

        self.input_unit = QComboBox()
        self.input_unit.addItems(["", "g", "kg", "ml", "l", "cup", "tbsp", "tsp", "pcs"])
        self.input_unit.setFixedWidth(80)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ingredient name")

        self.btn_add = QPushButton("Add")
        self.btn_add.setFixedWidth(60)

        add_bar.addWidget(self.input_qty)
        add_bar.addWidget(self.input_unit)
        add_bar.addWidget(self.input_name)
        add_bar.addWidget(self.btn_add)

        main_layout.addLayout(add_bar)

        # ── Scrollable List Section ──
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(12)

        scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(scroll_area)

        # example category blocks (to be replaced with dynamic logic)
        self.add_category("Dairy", [
            ("1", "cup", "Shredded Cheddar", False),
            ("2", "tbsp", "Butter", False),
        ])

        self.add_category("Meat", [
            ("2", "lbs", "Ground Beef", False),
            ("1", "pkg", "Bacon", True),
        ])

    def add_category(self, category_name: str, items: list[tuple[str, str, str, bool]]):
        """Adds a category block with grouped items."""
        cat_label = QLabel(category_name)
        cat_label.setObjectName("CategoryLabel")
        self.scroll_layout.addWidget(cat_label)

        for qty, unit, name, checked in items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(8)

            checkbox = QCheckBox()
            checkbox.setChecked(checked)
            checkbox.stateChanged.connect(lambda _, cb=checkbox, n=name: self.toggle_strike(cb, n))

            label = QLabel(f"{qty} {unit} {name}")
            label.setObjectName("IngredientLabel")
            label.setProperty("checked", checked)
            if checked:
                label.setStyleSheet("text-decoration: line-through;")

            checkbox.toggled.connect(lambda state, lbl=label: lbl.setStyleSheet(
                "text-decoration: line-through;" if state else ""
            ))

            item_layout.addWidget(checkbox)
            item_layout.addWidget(label)
            item_layout.addStretch()

            self.scroll_layout.addLayout(item_layout)

    def toggle_strike(self, checkbox, name):
        pass  # logic handled inline above, this is just a placeholder if needed