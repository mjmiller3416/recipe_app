# Minimal Test
import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QFrame, QPushButton, QSizePolicy,
                               QStackedWidget, QVBoxLayout, QWidget)

app = QApplication(sys.argv)

main_win = QWidget()
main_layout = QVBoxLayout(main_win)

# --- Create a container similar to RecipeSlot ---
slot_frame = QFrame()
slot_frame.setObjectName("SlotFrame")
slot_frame.setStyleSheet("QFrame#SlotFrame { border: 1px solid blue; }") # See the slot frame bounds

# --- Create the Stacked Widget ---
stack = QStackedWidget()
stack.setObjectName("Stack")
# stack.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred) # Try with/without
stack.setStyleSheet("QStackedWidget#Stack { border: 1px solid green; }") # See the stack bounds

# --- Create the Empty State Frame ---
empty_frame = QFrame()
empty_frame.setObjectName("EmptyFrame")
empty_frame.setFixedSize(QSize(280, 100))
empty_frame.setStyleSheet("QFrame#EmptyFrame { background-color: magenta; }") # See the empty frame bounds
# Add a button inside empty frame
empty_layout = QVBoxLayout(empty_frame)
button = QPushButton("Test Button")
empty_layout.addWidget(button)

# --- Add empty frame to stack ---
stack.addWidget(empty_frame)
stack.setCurrentIndex(0)

# --- Layout for the Slot Frame ---
slot_layout = QVBoxLayout(slot_frame)
slot_layout.setContentsMargins(0,0,0,0)
slot_layout.addWidget(stack) # Add stack to slot frame's layout

# --- Try forcing sizes ---
# stack.setFixedSize(280, 100) # Try forcing stack size directly
# slot_frame.setFixedSize(280, 100) # Try forcing slot frame size directly

# --- Add slot frame to main window layout ---
main_layout.addWidget(slot_frame)

main_win.show()
sys.exit(app.exec())
