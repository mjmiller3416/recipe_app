import sys

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QVBoxLayout,
                               QWidget)

from core.helpers import DebugLogger
# Assuming the script is run from a location where this import is valid.
from ui.components.inputs import SmartLineEdit


class SmartLineEditDemo(QWidget):
    """
    A demonstration and test widget for the SmartLineEdit component.
    It showcases how to connect to and handle both the item_selected and
    custom_text_submitted signals.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLineEdit Demo")
        self.setGeometry(100, 100, 700, 500)

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # A more descriptive label to provide feedback on which signal was caught.
        self.feedback_label = QLabel(
            "Type in a box and select an item, or type a custom value and press Enter or Tab away.",
            self
        )
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setWordWrap(True) # Allow text to wrap if window is small
        main_layout.addWidget(self.feedback_label)

        # Grid for SmartLineEdits
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        # A comprehensive list of items for the completer.
        INGREDIENTS = [
            "All-purpose flour", "Almond milk", "Almonds", "Apple cider vinegar", "Apples", "Avocado",
            "Bacon", "Baking powder", "Baking soda", "Balsamic vinegar", "Bananas", "Basil", "Beef, ground",
            "Bell pepper", "Black beans", "Black pepper", "Blueberries", "Broccoli", "Brown sugar", "Butter",
            "Carrots", "Cauliflower", "Celery", "Cheddar cheese", "Chicken breast", "Chickpeas", "Chili powder",
            "Cilantro", "Cinnamon", "Coconut milk", "Corn", "Cream cheese", "Cucumber", "Cumin", "Dijon mustard",
            "Eggs", "Feta cheese", "Garlic", "Garlic powder", "Ginger", "Green beans", "Green onions",

            "Heavy cream", "Honey", "Hummus", "Italian seasoning", "Jalapeños", "Kale", "Ketchup", "Lemon juice",
            "Lemons", "Lettuce", "Lime juice", "Limes", "Maple syrup", "Mayonnaise", "Milk", "Mint", "Mushrooms",
            "Olive oil", "Onion", "Onion powder", "Orange juice", "Oregano", "Paprika", "Parmesan", "Parsley",
            "Pasta", "Peanut butter", "Peas", "Pesto", "Pickles", "Pineapple", "Pinto beans", "Potatoes",
            "Quinoa", "Red onion", "Red pepper flakes", "Rice", "Rosemary", "Salmon", "Salsa", "Salt",
            "Sausage", "Sesame oil", "Shallots", "Shrimp", "Sour cream", "Soy sauce", "Spaghetti", "Spinach",
            "Strawberries", "Sugar", "Sweet potato", "Thyme", "Tofu", "Tomato paste", "Tomatoes", "Tuna",
            "Vanilla extract", "Vegetable broth", "Vinegar", "Walnuts", "Worcestershire sauce", "Yogurt", "Zucchini"
        ]

        for i in range(3):  # 3 rows
            for j in range(3):  # 3 columns
                sle = SmartLineEdit(
                    list_items=INGREDIENTS,
                    placeholder=f"Enter text ({i+1},{j+1})"
                )
                # --- CONNECT TO THE TWO DISTINCT SIGNALS ---
                sle.item_selected.connect(self.handle_item_selected)
                sle.custom_text_submitted.connect(self.handle_custom_text_submitted)
                
                grid_layout.addWidget(sle, i, j)

    @Slot(str)
    def handle_item_selected(self, text: str):
        """
        Handles the `item_selected` signal from a SmartLineEdit.
        This slot is triggered when a known item from the list is selected
        or submitted.
        """
        self.feedback_label.setText(f"✅ Known Item Selected: '{text}'")
        DebugLogger.log(f"[SIGNAL]] 'item_selected' received with text: {text}", "info")

    @Slot(str)
    def handle_custom_text_submitted(self, text: str):
        """
        Handles the `custom_text_submitted` signal from a SmartLineEdit.
        This slot is triggered when user-entered text that is NOT in the list
        is submitted.
        """
        self.feedback_label.setText(f"✨ Custom Text Submitted: '{text}'")
        DebugLogger.log(f"[SIGNAL] 'custom_text_submitted' received with text: {text}", "info")


def main():
    app = QApplication(sys.argv)
    demo_window = SmartLineEditDemo()
    demo_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()