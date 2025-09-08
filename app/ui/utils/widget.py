"""app/ui/utils/widget_utils.py

Widget creation and configuration utilities for the Recipe App.
Consolidates common widget setup patterns and theme registration logic.

# ── Internal Index ──────────────────────────────────────────
#
# ── Widget Creation & Setup ─────────────────────────────────
# CornmerAnchor                -> Anchor one widget's corner to another
# create_combo_box()           -> Standardized ComboBox creation
# create_line_edit()           -> Standardized LineEdit creation
# create_button()              -> Standardized Button creation
# create_text_edit()           -> Standardized TextEdit creation
#
# ── Theme & Styling ─────────────────────────────────────────
# register_widget_for_theme()  -> Register widget for theme system
# apply_object_name_pattern()  -> Apply consistent object naming
#
# ── Widget Configuration ────────────────────────────────────
# setup_form_field()           -> Configure form field with label
# setup_validation()           -> Apply validation to input widgets
# setup_placeholder_text()     -> Set placeholder text patterns

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from typing import List, Optional, Union

from PySide6.QtWidgets import QLabel, QLineEdit, QTextEdit, QWidget
from PySide6.QtCore import QEvent, QObject, QTimer

from app.style import Qss, Theme
from app.style.icon.config import Name, Type
from app.ui.components.widgets import Button, ComboBox


__all__ = [
    # Widget Creation & Setup
    'create_combo_box', 'create_line_edit', 'create_button', 'create_text_edit', 'CornmerAnchor',

    # Theme & Styling
    'register_widget_for_theme', 'apply_object_name_pattern',

    # Widget Configuration
    'setup_form_field', 'setup_validation', 'setup_placeholder_text',
]


# ── Widget Creation & Setup ─────────────────────────────────────────────────────────────────────────────────
class CornerAnchor(QObject):
    def __init__(self, anchor_widget, target_widget,
                 corner="bottom-left", x_offset=0, y_offset=0):
        super().__init__()
        self.anchor = anchor_widget
        self.target = target_widget
        self.corner = corner
        self.x_offset = x_offset
        self.y_offset = y_offset

        # watch for resize events on anchor's parent
        self.anchor.parent().installEventFilter(self)

        # delay the initial position update until layout is applied
        QTimer.singleShot(0, self.update_position)

        # make sure the target floats above
        self.target.raise_()

    def update_position(self):
        anchor_pos = self.anchor.mapToParent(self.anchor.rect().topLeft())
        anchor_size = self.anchor.size()
        target_size = self.target.size()

        match self.corner:
            case "top-left":
                x = anchor_pos.x()
                y = anchor_pos.y()
            case "top-right":
                x = anchor_pos.x() + anchor_size.width() - target_size.width()
                y = anchor_pos.y()
            case "bottom-left":
                x = anchor_pos.x()
                y = anchor_pos.y() + anchor_size.height() - target_size.height()
            case "bottom-right":
                x = anchor_pos.x() + anchor_size.width() - target_size.width()
                y = anchor_pos.y() + anchor_size.height() - target_size.height()
            case _:
                raise ValueError(f"Unsupported corner: {self.corner}")

        self.target.move(x + self.x_offset, y + self.y_offset)

    def eventFilter(self, obj, event):
        if obj == self.anchor.parent() and event.type() == QEvent.Resize:
            QTimer.singleShot(0, self.update_position)
        return super().eventFilter(obj, event)

def create_combo_box(
    list_items: List[str],
    placeholder: str = "",
    object_name: str = "ComboBox",
    context: Optional[str] = None,
    parent: Optional[QWidget] = None
) -> ComboBox:
    """
    Create a standardized ComboBox with consistent configuration.

    Args:
        list_items: List of items for the combo box
        placeholder: Placeholder text to display
        object_name: Object name for styling
        context: Context property for conditional styling
        parent: Parent widget

    Returns:
        ComboBox: Configured combo box widget

    Examples:
        combo = create_combo_box(["Option 1", "Option 2"], "Select option")
        combo = create_combo_box(MEAL_TYPES, "Select meal type", context="recipe_form")
    """
    combo = ComboBox(list_items=list_items, placeholder=placeholder, parent=parent)
    combo.setObjectName(object_name)

    if context:
        combo.setProperty("context", context)

    return combo

def create_line_edit(
    placeholder: str = "",
    object_name: str = "LineEdit",
    parent: Optional[QWidget] = None
) -> QLineEdit:
    """
    Create a standardized LineEdit with consistent configuration.

    Args:
        placeholder: Placeholder text to display
        object_name: Object name for styling
        parent: Parent widget

    Returns:
        QLineEdit: Configured line edit widget

    Examples:
        edit = create_line_edit("Enter recipe name", "RecipeNameLineEdit")
        edit = create_line_edit("e.g. 30 mins", "TimeLineEdit")
    """
    line_edit = QLineEdit(parent)
    line_edit.setPlaceholderText(placeholder)
    line_edit.setObjectName(object_name)

    return line_edit

def create_button(
    text: str,
    button_type: Union[Type, str] = Type.PRIMARY,
    icon: Optional[Name] = None,
    object_name: str = "Button",
    parent: Optional[QWidget] = None
) -> Button:
    """
    Create a standardized Button with consistent configuration.

    Args:
        text: Button text
        button_type: Button type (Type enum or string)
        icon: Optional icon for the button
        object_name: Object name for styling
        parent: Parent widget

    Returns:
        Button: Configured button widget

    Examples:
        btn = create_button("Save Recipe", Type.PRIMARY, Name.SAVE)
        btn = create_button("Cancel", Type.SECONDARY)
    """
    button = Button(text, button_type, icon, parent)
    button.setObjectName(object_name)

    return button

def create_text_edit(
    placeholder: str = "",
    object_name: str = "TextEdit",
    parent: Optional[QWidget] = None
) -> QTextEdit:
    """
    Create a standardized QTextEdit with consistent configuration.

    Args:
        placeholder: Placeholder text to display
        object_name: Object name for styling
        parent: Parent widget

    Returns:
        QTextEdit: Configured text edit widget

    Examples:
        text_edit = create_text_edit("Enter cooking directions...", "DirectionsTextEdit")
        notes_edit = create_text_edit("Add any notes...", "NotesTextEdit")
    """
    text_edit = QTextEdit(parent)
    text_edit.setPlaceholderText(placeholder)
    text_edit.setObjectName(object_name)

    return text_edit


# ── Theme & Styling ─────────────────────────────────────────────────────────────────────────────────────────
def register_widget_for_theme(widget: QWidget, qss_style: Qss) -> None:
    """
    Register widget with the theme system for consistent styling.

    Args:
        widget: Widget to register with theme system
        qss_style: QSS style identifier from Qss enum

    Examples:
        register_widget_for_theme(self, Qss.ADD_RECIPE)
        register_widget_for_theme(ingredient_form, Qss.INGREDIENT_WIDGET)
    """
    Theme.register_widget(widget, qss_style)

def apply_object_name_pattern(
    widget: QWidget,
    base_name: str,
    context: Optional[str] = None,
    field_type: Optional[str] = None
) -> None:
    """
    Apply consistent object naming pattern to widgets.

    Args:
        widget: Widget to name
        base_name: Base name for the widget
        context: Context or parent component name
        field_type: Type of field (LineEdit, ComboBox, etc.)

    Examples:
        apply_object_name_pattern(line_edit, "RecipeName", "Recipe", "LineEdit")
        # Results in: "RecipeNameLineEdit"

        apply_object_name_pattern(combo, "MealType", "Recipe", "ComboBox")
        # Results in: "MealTypeComboBox"
    """
    parts = [base_name]

    if field_type:
        parts.append(field_type)
    elif context:
        parts.append(context)

    object_name = "".join(parts)
    widget.setObjectName(object_name)


# ── Widget Configuration ────────────────────────────────────────────────────────────────────────────────────
def setup_form_field(
    label_text: str,
    widget: QWidget,
    parent: QWidget,
    tooltip: Optional[str] = None
) -> tuple[QLabel, QWidget]:
    """
    Set up a form field with label and optional tooltip.

    Args:
        label_text: Text for the label
        widget: Input widget (LineEdit, ComboBox, etc.)
        parent: Parent widget for the label
        tooltip: Optional tooltip text

    Returns:
        tuple[QLabel, QWidget]: (label, widget) pair

    Examples:
        label, edit = setup_form_field("Recipe Name", recipe_edit, self)
        label, combo = setup_form_field("Category", category_combo, self, "Select recipe category")
    """
    label = QLabel(label_text, parent)

    if tooltip:
        label.setToolTip(tooltip)
        widget.setToolTip(tooltip)

    return label, widget

def setup_validation(widget: QWidget, validator_pattern: str) -> None:
    """
    Apply validation pattern to input widgets.

    Args:
        widget: Widget to apply validation to
        validator_pattern: Validation pattern or type

    Examples:
        setup_validation(quantity_edit, "FLOAT_VALIDATOR")
        setup_validation(name_edit, "NAME_PATTERN")
    """
    # This would integrate with existing validation helpers
    # Implementation depends on current validation system
    pass

def setup_placeholder_text(
    widget: Union[QLineEdit, QTextEdit, ComboBox],
    field_type: str,
    context: Optional[str] = None
) -> None:
    """
    Set up consistent placeholder text patterns.

    Args:
        widget: Widget to set placeholder for
        field_type: Type of field (name, time, quantity, etc.)
        context: Context for more specific placeholders

    Examples:
        setup_placeholder_text(name_edit, "recipe_name")
        # Sets: "e.g. Spaghetti Carbonara"

        setup_placeholder_text(time_edit, "time")
        # Sets: "e.g. 30 mins"
    """
    placeholder_patterns = {
        "recipe_name": "e.g. Spaghetti Carbonara",
        "ingredient_name": "e.g. Olive Oil",
        "time": "e.g. 30 mins",
        "servings": "e.g. 4",
        "quantity": "e.g. 2",
        "unit": "e.g. cups",
        "category": "Select category",
        "meal_type": "Select meal type",
        "dietary": "Select dietary preference",
        "directions": "Enter cooking directions here...",
        "notes": "Add any additional notes here...",
    }

    placeholder = placeholder_patterns.get(field_type, "")

    if hasattr(widget, 'setPlaceholderText'):
        widget.setPlaceholderText(placeholder)
    elif hasattr(widget, 'setPlaceholder'):  # For ComboBox
        widget.setPlaceholder(placeholder)
