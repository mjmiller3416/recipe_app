"""Standalone test window for IngredientWidget."""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from app.ui.components.forms import IngredientWidget
from app.ui.components.layout.widget_frame import WidgetFrame


class IngredientWidgetTestApp(QMainWindow):
    """Minimal window replicating AddRecipes ingredient logic."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("IngredientWidget Test")
        self.setGeometry(100, 100, 500, 400)

        self.ingredient_widgets = []
        self.stored_ingredients = []

        central_widget = QWidget()
        self.central_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.ingredients_frame = WidgetFrame(
            title="Ingredients",
            layout=QVBoxLayout,
            scrollable=True,
            spacing=0,
        )
        self.central_layout.addWidget(self.ingredients_frame)

        self._add_ingredient(removable=False)

    def _add_ingredient(self, removable=True):
        widget = IngredientWidget(removable=removable)
        widget.remove_ingredient_requested.connect(self._remove_ingredient)
        widget.add_ingredient_requested.connect(self._add_ingredient)
        widget.ingredient_validated.connect(self._store_ingredient)
        self.ingredient_widgets.append(widget)
        self.ingredients_frame.addWidget(widget)

    def _remove_ingredient(self, widget):
        self.ingredients_frame.removeWidget(widget)
        widget.deleteLater()
        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)

    def _store_ingredient(self, data: dict):
        self.stored_ingredients.append(data)


def run_test(app):
    """Entry point used by main.py when launched with --test."""
    window = IngredientWidgetTestApp(app)
    return window
