"""ui/components/form_field.py

A set of form field components for creating structured input forms in a PySide6 application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Any, Optional

from PySide6.QtWidgets import (QGridLayout, QLabel, QLineEdit, QSizePolicy,
                               QWidget)

from ui.components.inputs import SmartComboBox


# ── Class Definition ────────────────────────────────────────────────────────────
class FormField(QWidget):
    """
    Base class for form fields, providing a consistent layout and styling.
    
    Attributes:
        label (QLabel): The label for the form field.
        input_widget (QWidget): The input widget (e.g., QLineEdit, QTextEdit).
    """
    
    def __init__(
            self, 
            label_text: str, 
            widget: QWidget, 
            parent: Optional[QWidget] = None
    ) -> None:
        """Initializes the FormField with a label and an input widget."""
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.lbl = QLabel(label_text) 
        self.input_widget = widget
        
        self._build_ui()
    
    def _build_ui(self):
        """Builds the UI layout for the form field."""
        layout = QGridLayout(self)
        layout.setSpacing(10)

        # align the label and input widget
        self.lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.input_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        layout.addWidget(self.lbl, 0, 0)
        layout.addWidget(self.input_widget, 0, 1)
        layout.setColumnStretch(1, 1) # Make the second column stretchable

        ## set the size policy for the entire form field
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def __getattr__(self, name: str) -> Any:
        # forward unknown lookups to the inner widget
        return getattr(self.input_widget, name)


# ── Class Definition ────────────────────────────────────────────────────────────
class LineEditField(FormField):
    """
    Form field specifically for QLineEdit input.
    
    Inherits from FormField and initializes with a QLineEdit widget.
    """
    
    def __init__(
            self, 
            label_text: str, 
            placeholder: Optional[str] = None,
            parent: Optional[QWidget] = None
    ):
        """
        Initializes the LineEditField with a label and a QLineEdit.
        
        Args:
            label_text (str): The text for the label.
            placeholder (str, optional): Placeholder text for the QLineEdit.
            parent (QWidget, optional): Parent widget for this field.
        """
        widget = QLineEdit()

        if placeholder:
            widget.setPlaceholderText(placeholder)
        super().__init__(label_text, widget, parent)
        self.setFixedHeight(50)  # set a fixed height for the input field
    
    @property
    def textChanged(self):
        """Exposes the QLineEdit's textChanged signal."""
        return self.input_widget.textChanged

    def setValidator(self, validator):
        """
        Sets a validator for the QLineEdit input widget.

        Args:
            validator: A QValidator instance to validate the input.
        """
        self.input_widget.setValidator(validator)

    def text(self):
        """Returns the text from the QLineEdit input widget."""
        return self.input_widget.text()
    
    def clear(self):
        """Clears the current selection in the SmartComboBox."""
        self.input_widget.clear()

    def strip(self):
        """
        Returns the text from the QLineEdit input widget with leading and trailing whitespace removed.
        
        Returns:
            str: The stripped text.
        """
        return self.input_widget.text().strip()
    


# ── Class Definition ────────────────────────────────────────────────────────────
class ComboBoxField(FormField):
    """
    Form field specifically for SmartComboBox input.
    
    Inherits from FormField and initializes with a SmartComboBox widget.
    """

    def __init__(
            self, 
            label_text: str, 
            item_list: list[str], 
            parent: Optional[QWidget] = None
    ):
        """
        Initializes the ComboBoxField with a label and a SmartComboBox.
        
        Args:
            label_text (str): The text for the label.
            item_list (list[str]): List of items to populate the combo box.
            parent (QWidget, optional): Parent widget for this field.
        """
        widget = SmartComboBox(list=item_list)
        super().__init__(label_text, widget, parent)

    @property
    def selection_validated(self):
        """Exposes the SmartComboBox's selection_validated signal."""
        return self.input_widget.selection_validated
    
    def currentText(self):
        """Returns the current text from the SmartComboBox input widget."""
        return self.input_widget.currentText()
    
    def setCurrentIndex(self, index: int):
        """
        Sets the current index of the SmartComboBox.
        
        Args:
            index (int): The index to set as current.
        """
        self.input_widget.setCurrentIndex(index)
    
    