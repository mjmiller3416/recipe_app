#!/usr/bin/env python3
"""Visual test to verify Card HBox layout functionality."""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

# Add the app directory to the path
sys.path.append('.')

from app.ui.components.layout.card import Card

def test_card_visual():
    """Visual test for Card layout."""
    app = QApplication([])

    # Create a test window
    window = QWidget()
    window.setWindowTitle("Card HBox Layout Visual Test")
    window.resize(600, 400)
    main_layout = QVBoxLayout(window)

    # Test 1: Card with VBox layout (default)
    vbox_card = Card()
    vbox_card.setObjectName("VBoxCard")
    vbox_layout = vbox_card.addLayout("vbox")
    vbox_layout.setContentsMargins(20, 15, 20, 15)
    vbox_layout.setSpacing(10)

    # Add widgets vertically
    vbox_layout.addWidget(QLabel("VBox Item 1"))
    vbox_layout.addWidget(QLabel("VBox Item 2"))
    vbox_layout.addWidget(QLabel("VBox Item 3"))

    main_layout.addWidget(QLabel("VBox Layout (items stacked vertically):"))
    main_layout.addWidget(vbox_card)

    # Test 2: Card with HBox layout
    hbox_card = Card()
    hbox_card.setObjectName("HBoxCard")
    hbox_layout = hbox_card.addLayout("hbox")  # This should create horizontal layout
    hbox_layout.setContentsMargins(20, 15, 20, 15)
    hbox_layout.setSpacing(40)

    # Add widgets horizontally
    hbox_layout.addWidget(QLabel("HBox Item 1"))
    hbox_layout.addWidget(QLabel("HBox Item 2"))
    hbox_layout.addWidget(QLabel("HBox Item 3"))

    main_layout.addWidget(QLabel("HBox Layout (items arranged horizontally):"))
    main_layout.addWidget(hbox_card)

    # Add some styling to make the difference clear
    vbox_card.setStyleSheet("QLabel { background: lightblue; padding: 5px; margin: 2px; }")
    hbox_card.setStyleSheet("QLabel { background: lightgreen; padding: 5px; margin: 2px; }")

    window.show()

    print("Visual test running...")
    print("VBox card should show items stacked vertically")
    print("HBox card should show items arranged horizontally")
    print("Close the window to end the test")

    app.exec()

if __name__ == "__main__":
    test_card_visual()
