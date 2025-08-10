#!/usr/bin/env python3
"""Simple test to verify Card layout functionality."""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

# Add the app directory to the path
sys.path.append('.')

from app.ui.components.layout.card import Card

def test_card_layout():
    """Test Card layout creation and usage."""
    app = QApplication([])

    # Create a test window
    window = QWidget()
    window.setWindowTitle("Card Layout Test")
    main_layout = QVBoxLayout(window)

    # Test Card with HBox layout
    print("Creating Card...")
    card = Card()
    print("Setting object name...")
    card.setObjectName("TestCard")

    print("Adding hbox layout...")
    layout = card.addLayout("hbox")
    print(f"Layout type: {type(layout)}")

    print("Setting content margins...")
    layout.setContentsMargins(20, 15, 20, 15)

    print("Setting spacing...")
    layout.setSpacing(40)

    # Add some test widgets
    layout.addWidget(QLabel("Test 1"))
    layout.addWidget(QLabel("Test 2"))
    layout.addWidget(QLabel("Test 3"))

    main_layout.addWidget(card)

    window.resize(400, 200)
    window.show()

    print("Card layout test completed successfully!")

    # Run for a short time then quit
    app.processEvents()
    app.quit()

if __name__ == "__main__":
    test_card_layout()
