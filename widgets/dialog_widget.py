# Package: app.widgets.dialog

# Description: This file contains the DialogWidget class, which is a subclass of QDialog. The DialogWidget class is used to 
# create a custom dialog window that can display different types of messages (info, warning, confirmation, error). 
# It allows for dynamic button visibility based on the message type and provides methods to set messages and handle button clicks.


#🔸Primary Imports

#🔸Third-Party Imports
from qt_imports import (QDialog, Qt, QDialogButtonBox, QGraphicsDropShadowEffect, QColor, QPixmap)

#🔸Local Imports
from .ui_dialog_widget import Ui_DialogWidget
from style_manager import SUCCESS_COLOR
from app.helpers import svg_loader
from debug_logger import DebugLogger

class DialogWidget(QDialog):
    """Custom dialog for displaying messages with dynamic button visibility."""
    
    def __init__(self, message_type="info", message="", description="", parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogWidget()
        self.ui.setupUi(self)
        self.setObjectName("DialogWidget")
        self.setFixedHeight(220)  # Or any desired pixel value
        self.setFixedWidth(400)  # Or any desired pixel value

        # Custom Dialog Initialized
        DebugLogger.log(f"DialogWidget initialized", "info")

        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove title bar

        # Customize the dialog icon color 
        # ⚠️ Returns false - not treated as an actual icon in UI
        self.pixmap = svg_loader(":/icons/success.svg", SUCCESS_COLOR, size=self.ui.lbl_icon.size(), return_type=QPixmap)
        self.ui.lbl_icon.setPixmap(self.pixmap)

        # Dynamically configure buttons
        self.configure_buttons(message_type)

        # Set the message labels
        self.set_messages(message, description)

        # Apply shadow effect
        self.apply_shadow()

    def apply_shadow(self):
        """
        Creates and applies a QGraphicsDropShadowEffect to the entire dialog.
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)     # Adjust for a softer or sharper blur
        shadow.setXOffset(0)         # Horizontal offset of shadow
        shadow.setYOffset(5)         # Vertical offset of shadow
        shadow.setColor(QColor(0, 0, 0, 165))  # Shadow color (RGBA)
        self.setGraphicsEffect(shadow)

    def showEvent(self, event):
        super().showEvent(event)
        self.center_dialog()  # Center the dialog when shown

    def center_dialog(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            dialog_rect = self.geometry()

            center_x = parent_rect.x() + (parent_rect.width() - dialog_rect.width()) // 2
            center_y = parent_rect.y() + (
                parent_rect.height() // 3
                - dialog_rect.height() // 2
            )
            
            # Manually shift the dialog a bit. Negative = move left, positive = move right
            horizontal_nudge = -20  # e.g. move 20px left
            center_x += horizontal_nudge
            
            self.move(center_x, center_y)


    def configure_buttons(self, message_type):
        """
        Shows/hides buttons based on message type.
        
        Args:
            message_type (str): Type of message ('info', 'warning', 'confirmation', 'error').
        """

        # Remove all buttons first
        self.ui.buttonBox.clear()

        if message_type == "info":
            # Just an OK button
            self.ui.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole)
            
            # Connect signals
            self.ui.buttonBox.accepted.connect(self.accept)

        elif message_type == "warning":
            # OK and Cancel
            self.ui.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole)
            self.ui.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
            
            # Connect signals
            self.ui.buttonBox.accepted.connect(self.accept)
            self.ui.buttonBox.rejected.connect(self.reject)

        elif message_type == "confirmation":
            # Save, Discard, Cancel
            self.ui.buttonBox.addButton("Save", QDialogButtonBox.AcceptRole)
            discard_button = self.ui.buttonBox.addButton("Discard", QDialogButtonBox.DestructiveRole)
            self.ui.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole) 

            # Connect signals
            self.ui.buttonBox.accepted.connect(self.accept)
            discard_button.clicked.connect(self.discard_changes)
            self.ui.buttonBox.rejected.connect(self.reject)

        elif message_type == "error":
            # Just an OK button, since errors don’t need user choices
            self.ui.buttonBox.addButton("OK", QDialogButtonBox.AcceptRole)

            # Connect signals
            self.ui.buttonBox.accepted.connect(self.accept)    

    def set_messages(self, message, description):
        """
        Updates the message and descriptive message labels.
        
        Args:
            message (str): Main message to display.
            description (str): Additional descriptive text.
        """
        self.ui.lbl_message.setText(message)
        self.ui.lbl_description.setText(description)

        # ⚠️ Add additional logic to dynamically change  icon based on message type

    def discard_changes(self):
        """Handles the 'Discard' button logic."""
        print("Changes discarded!")  # Replace with actual discard logic
        self.accept()  # Close the dialog

    def keyPressEvent(self, event):
        """Handles key presses for Enter (OK) and Esc (Cancel)."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()  # Triggers OK / Save button
        elif event.key() == Qt.Key_Escape:
            self.reject()  # Triggers Cancel button
        else:
            super().keyPressEvent(event)  # Default behavior

#🔸END