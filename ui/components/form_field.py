"""ui/components/form_field.py

A set of form field components for creating structured input forms in a PySide6 application.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from typing import Optional
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from PySide6.QtWidgets import QLineEdit
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.lbl)
        layout.addWidget(self.input_widget)


# ── Class Definition ────────────────────────────────────────────────────────────
class LineEditField(FormField):
    """
    Form field specifically for QLineEdit input.
    
    Inherits from FormField and initializes with a QLineEdit widget.
    """
    
    def __init__(self, label_text: str, parent: Optional[QWidget] = None):
        """
        Initializes the LineEditField with a label and a QLineEdit.
        
        Args:
            label_text (str): The text for the label.
            parent (QWidget, optional): Parent widget for this field.
        """
        widget = QLineEdit()
        super().__init__(label_text, widget, parent)


# ── Class Definition ────────────────────────────────────────────────────────────
class ComboBoxField(FormField):
    """
    Form field specifically for SmartComboBox input.
    
    Inherits from FormField and initializes with a SmartComboBox widget.
    """
    
    def __init__(self, label_text: str, parent: Optional[QWidget] = None):
        """
        Initializes the ComboBoxField with a label and a SmartComboBox.
        
        Args:
            label_text (str): The text for the label.
            parent (QWidget, optional): Parent widget for this field.
        """
        widget = SmartComboBox()
        super().__init__(label_text, widget, parent)