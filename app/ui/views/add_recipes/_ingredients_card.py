"""app/ui/views/add_recipes/_ingredients_card.py

This module defines the IngredientsCard class, which provides a container for managing
ingredient input forms within a card layout. It includes functionality to add and remove
ingredient forms dynamically and to collect ingredient data.
"""

# ── Imports ──
from PySide6.QtCore import Qt, Signal, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QColor

from app.style import Name
from app.ui.components.layout.card import ActionCard
from ._ingredient_form import IngredientForm
from ..base import BaseView


class IngredientsCard(ActionCard):
    """
    Container for managing ingredient widgets within a Card.
    Provides add/remove functionality and data collection.
    """

    ingredients_changed = Signal()  # Emitted when ingredients are added/removed

    def __init__(self, parent=None):
        """Initialize the ingredient container."""
        super().__init__(card_type="Default", parent=parent)

        self.setHeader("Ingredients")
        self.setSubHeader("List all the ingredients required for this recipe.")

        self.ingredient_widgets = []

        # Drag and drop state
        self._dragging_widget = None
        self._drag_start_pos = None
        self._drop_indicator = None
        self._drop_index = -1

        self._build_ui()
        self._setup_drop_indicator()


    # ── Private ──
    def _build_ui(self):
        """Set up the container UI with initial ingredient and add button."""
        # Add initial ingredient widget
        self._add_ingredient_widget()

        # Add button to card footer with left alignment and ADD icon
        self.addButton("Add Ingredient", icon=Name.ADD, alignment=Qt.AlignLeft)

        # Customize button icon size and connect click event
        if self.button:
            self.button.setIconSize(24, 24)
            # Connect to a method that adds AND focuses
            self.button.clicked.connect(self._on_add_button_clicked)

    def _on_add_button_clicked(self):
        """Handle add ingredient button click - add widget and set focus."""
        # Add the new ingredient
        self._add_ingredient_widget()

        # Get the newly added widget (last in the list)
        if self.ingredient_widgets:
            new_widget = self.ingredient_widgets[-1]
            # Set focus with a small delay to ensure rendering
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._focus_new_ingredient(new_widget))

    def _focus_new_ingredient(self, widget):
        """Set focus to the first input field of the ingredient widget."""
        if widget and hasattr(widget, 'le_quantity') and widget.le_quantity:
            widget.le_quantity.setFocus(Qt.TabFocusReason)

            # Update the parent's last_focused_widget tracker
            parent_view = self.parent()
            while parent_view and not isinstance(parent_view, BaseView):
                parent_view = parent_view.parent()

            if parent_view and hasattr(parent_view, 'last_focused_widget'):
                parent_view.last_focused_widget = widget.le_quantity

    def _get_ingredient_count(self) -> int:
        """Get the number of ingredient widgets."""
        return len(self.ingredient_widgets)

    def _add_ingredient_widget(self):
        """Add a new ingredient widget to the container."""
        ingredient_widget = IngredientForm()
        ingredient_widget.remove_ingredient_requested.connect(self._remove_ingredient_widget)

        # Connect drag handle for drag-and-drop
        if hasattr(ingredient_widget, 'drag_handle'):
            ingredient_widget.drag_handle.installEventFilter(self)

        self.ingredient_widgets.append(ingredient_widget)
        self.addWidget(ingredient_widget)

        self.ingredients_changed.emit()

    def _remove_ingredient_widget(self, widget: IngredientForm):
        """Remove an ingredient widget from the container."""
        if len(self.ingredient_widgets) <= 1:
            return  # Always keep at least one ingredient widget

        if widget in self.ingredient_widgets:
            self.ingredient_widgets.remove(widget)
            self.removeWidget(widget)
            widget.deleteLater()

        self.ingredients_changed.emit()

    def _setup_drop_indicator(self):
        """Create a visual indicator line for showing drop position."""
        self._drop_indicator = QFrame(self._content_container)
        self._drop_indicator.setFixedHeight(3)
        self._drop_indicator.setStyleSheet("background-color: #4CAF50;")
        self._drop_indicator.hide()

    def _get_widget_for_drag_handle(self, drag_handle):
        """Find the parent IngredientForm for a drag handle."""
        for widget in self.ingredient_widgets:
            if hasattr(widget, 'drag_handle') and widget.drag_handle == drag_handle:
                return widget
        return None

    def _get_drop_index(self, y_pos):
        """Calculate the index where the widget should be dropped based on y position."""
        if not self.ingredient_widgets:
            return 0

        for i, widget in enumerate(self.ingredient_widgets):
            if widget == self._dragging_widget:
                continue

            widget_center = widget.geometry().center().y()
            if y_pos < widget_center:
                return i

        return len(self.ingredient_widgets)

    def _reorder_widgets(self, from_index, to_index):
        """Reorder the widgets in both the list and the layout."""
        if from_index == to_index:
            return

        # Remove widget from list
        widget = self.ingredient_widgets.pop(from_index)

        # Adjust target index if needed
        if to_index > from_index:
            to_index -= 1

        # Insert widget at new position
        self.ingredient_widgets.insert(to_index, widget)

        # Rebuild the layout
        for w in self.ingredient_widgets:
            self.removeWidget(w)

        for w in self.ingredient_widgets:
            self.addWidget(w)

        self.ingredients_changed.emit()

    def _update_drop_indicator(self, drop_index):
        """Update the position of the drop indicator line."""
        if drop_index < 0 or not self._drop_indicator:
            self._drop_indicator.hide()
            return

        if drop_index >= len(self.ingredient_widgets):
            # Place at the bottom
            if self.ingredient_widgets:
                last_widget = self.ingredient_widgets[-1]
                y = last_widget.geometry().bottom()
            else:
                y = 0
        else:
            # Place above the widget at drop_index
            widget = self.ingredient_widgets[drop_index]
            y = widget.geometry().top() - 2

        self._drop_indicator.setGeometry(10, y, self._content_container.width() - 20, 3)
        self._drop_indicator.show()
        self._drop_indicator.raise_()


    # ── Public ──
    def getAllIngredientsData(self) -> list[dict]:
        """Collect data from all ingredient widgets."""
        ingredients_data = []

        for widget in self.ingredient_widgets:
            data = widget.getIngredientData()
            # Only include ingredients with at least a name
            if data.get("ingredient_name", "").strip():
                ingredients_data.append(data)

        return ingredients_data

    def setIngredients(self, ingredients: list[dict]) -> None:
        """Replace current ingredient widgets with provided ingredient data."""
        signals_were_blocked = self.blockSignals(True)
        self.clearAllIngredients()
        if not ingredients:
            if not signals_were_blocked:
                self.ingredients_changed.emit()
            self.blockSignals(signals_were_blocked)
            return

        # Populate the first widget (already created by clearAllIngredients)
        if self.ingredient_widgets:
            self.ingredient_widgets[0].setIngredientData(ingredients[0])

        # Add any remaining widgets
        for data in ingredients[1:]:
            self._add_ingredient_widget()
            self.ingredient_widgets[-1].setIngredientData(data)

        if not signals_were_blocked:
            self.ingredients_changed.emit()
        self.blockSignals(signals_were_blocked)

    def clearAllIngredients(self):
        """Clear all ingredient widgets and add one empty one."""
        # Remove all existing widgets
        for widget in self.ingredient_widgets:
            self.removeWidget(widget)
            widget.deleteLater()

        self.ingredient_widgets.clear()

        # Add one fresh ingredient widget
        self._add_ingredient_widget()

    # ── Event Handlers ──
    def eventFilter(self, obj, event):
        """Handle drag-and-drop events for ingredient reordering."""
        from PySide6.QtCore import QEvent

        # Check if this is a drag handle
        if obj in [w.drag_handle for w in self.ingredient_widgets if hasattr(w, 'drag_handle')]:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._drag_start_pos = event.pos()
                    self._dragging_widget = self._get_widget_for_drag_handle(obj)
                    return False

            elif event.type() == QEvent.MouseMove:
                if event.buttons() & Qt.LeftButton and self._dragging_widget:
                    # Start dragging if we've moved enough
                    if self._drag_start_pos and (event.pos() - self._drag_start_pos).manhattanLength() > 5:
                        # Convert position to content container coordinates
                        global_pos = obj.mapToGlobal(event.pos())
                        local_pos = self._content_container.mapFromGlobal(global_pos)

                        # Update drop indicator
                        drop_index = self._get_drop_index(local_pos.y())
                        if drop_index != self._drop_index:
                            self._drop_index = drop_index
                            self._update_drop_indicator(drop_index)

                        # Visual feedback on dragged widget
                        if not self._dragging_widget.graphicsEffect():
                            opacity_effect = QGraphicsOpacityEffect()
                            opacity_effect.setOpacity(0.6)
                            self._dragging_widget.setGraphicsEffect(opacity_effect)
                        obj.setCursor(Qt.ClosedHandCursor)
                        return True

            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton and self._dragging_widget:
                    # Perform the reorder
                    if self._drop_index >= 0:
                        from_index = self.ingredient_widgets.index(self._dragging_widget)
                        self._reorder_widgets(from_index, self._drop_index)

                    # Clean up - remove opacity effect
                    self._dragging_widget.setGraphicsEffect(None)
                    self._dragging_widget = None
                    self._drag_start_pos = None
                    self._drop_index = -1
                    self._drop_indicator.hide()
                    obj.setCursor(Qt.OpenHandCursor)
                    return True

            elif event.type() == QEvent.Enter:
                if not self._dragging_widget:
                    obj.setCursor(Qt.OpenHandCursor)

            elif event.type() == QEvent.Leave:
                if not self._dragging_widget:
                    obj.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)
