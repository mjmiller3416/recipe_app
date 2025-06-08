\
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Slot, Qt # Import Qt

# Assuming demo_scb.py is in the root of recipe_app,
# and the script is run from the recipe_app root,
# or recipe_app is in PYTHONPATH.
from ui.components.inputs.smart_combobox import SmartComboBox


class SmartComboBoxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartComboBox Demo")
        self.setGeometry(100, 100, 700, 500)  # Adjusted size for better layout

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Label to display selection
        self.selection_label = QLabel("No selection yet.", self)
        self.selection_label.setAlignment(Qt.AlignCenter) # Center align text
        main_layout.addWidget(self.selection_label)

        # Grid for SmartComboBoxes
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        self.smart_comboboxes = []
        # Sample items for the comboboxes - ensure this list is not empty
        INGREDIENTS = [
            "All-purpose flour", "Almond milk", "Almonds", "Apple cider vinegar", "Apples", "Artichoke hearts",
            "Arugula", "Asparagus", "Avocado", "Bacon", "Baking powder", "Baking soda", "Balsamic vinegar",
            "Bananas", "Basil", "Bay leaves", "Beans", "Beef broth", "Beef, ground", "Beets", "Bell pepper",
            "Black beans", "Black olives", "Black pepper", "Blueberries", "Bok choy", "Bread", "Broccoli",
            "Brown rice", "Brown sugar", "Brussels sprouts", "Butter", "Cabbage", "Cacao powder", "Cajun seasoning",
            "Canola oil", "Cantaloupe", "Capers", "Carrots", "Cauliflower", "Celery", "Cheddar cheese",
            "Cherries", "Chia seeds", "Chicken breast", "Chicken broth", "Chicken thighs", "Chickpeas", "Chili flakes",
            "Chili powder", "Chives", "Chocolate chips", "Cilantro", "Cinnamon", "Cloves", "Coconut milk",
            "Coconut oil", "Coconut sugar", "Cocoa powder", "Coleslaw mix", "Condensed milk", "Coriander", "Corn",
            "Corn flour", "Corn starch", "Cottage cheese", "Couscous", "Cream cheese", "Cucumber", "Cumin",
            "Curry powder", "Deli turkey", "Dijon mustard", "Dill", "Egg noodles", "Eggplant", "Eggs",
            "Evaporated milk", "Feta cheese", "Figs", "Fish sauce", "Flour tortillas", "Garbanzo beans", "Garlic",
            "Garlic powder", "Ginger", "Gnocchi", "Goat cheese", "Grapes", "Green beans", "Green onions", "Ground cinnamon",
            "Ground turkey", "Gruyere", "Ham", "Heavy cream", "Honey", "Hot sauce", "Hummus", "Iceberg lettuce",
            "Italian seasoning", "Jalapeños", "Jam", "Jasmine rice", "Kale", "Ketchup", "Kidney beans",
            "Kosher salt", "Lamb", "Lasagna noodles", "Lemon juice", "Lemons", "Lettuce", "Lima beans", "Lime juice",
            "Limes", "Maple syrup", "Marinara sauce", "Marjoram", "Mayonnaise", "Milk", "Mint", "Monterey Jack",
            "Mozzarella", "Mushrooms", "Mustard", "Nutmeg", "Nutritional yeast", "Oats", "Olive oil", "Onion",
            "Onion powder", "Orange juice", "Oranges", "Oregano", "Paprika", "Parmesan", "Parsley", "Pasta",
            "Peaches", "Peanut butter", "Peanuts", "Pears", "Peas", "Pecans", "Pepperoni", "Pesto", "Pickles",
            "Pineapple", "Pinto beans", "Pita bread", "Plain yogurt", "Plums", "Pomegranate", "Poppy seeds",
            "Pork chops", "Potatoes", "Powdered sugar", "Pretzels", "Provolone", "Pumpkin", "Pumpkin pie spice",
            "Quinoa", "Radishes", "Raisins", "Raspberries", "Red bell pepper", "Red cabbage", "Red lentils",
            "Red onion", "Red pepper flakes", "Refried beans", "Ricotta", "Rice noodles", "Rice vinegar",
            "Roasted red peppers", "Romaine lettuce", "Rosemary", "Sage", "Salmon", "Salsa", "Salt", "Sausage",
            "Scallions", "Sesame oil", "Sesame seeds", "Shallots", "Sharp cheddar", "Shrimp", "Sour cream",
            "Soy milk", "Soy sauce", "Spaghetti", "Spinach", "Split peas", "Spring mix", "Squash", "Steak",
            "Strawberries", "Sugar", "Sun-dried tomatoes", "Sunflower seeds", "Sweet corn", "Sweet potato", "Swiss cheese",
            "Tahini", "Tarragon", "Thyme", "Tilapia", "Tofu", "Tomatillos", "Tomato paste", "Tomato sauce",
            "Tomatoes", "Tuna", "Turkey", "Vanilla extract", "Vegetable broth", "Vegetable oil", "Vinegar",
            "Walnuts", "Water", "Water chestnuts", "Watercress", "White beans", "White rice", "Whole wheat flour",
            "Worcestershire sauce", "Yogurt", "Zucchini"
        ]

        for i in range(3):  # 3 rows
            for j in range(3):  # 3 columns
                scb = SmartComboBox(
                    list_items=INGREDIENTS,
                    placeholder=f"Select ({i+1},{j+1})"
                )
                # Connect the signal to the handler
                scb.selection_trigger.connect(self.update_selection_label)
                grid_layout.addWidget(scb, i, j)
                self.smart_comboboxes.append(scb)

    @Slot(str)
    def update_selection_label(self, selected_text: str):
        """
        Handles the selection_trigger signal from any SmartComboBox.
        Updates the label to display the selected text.
        """
        self.selection_label.setText(f"Selected: {selected_text}")

def main():
    app = QApplication(sys.argv)

    # Note: For this demo to run correctly, the Python environment
    # must be able to find the 'ui', 'config', 'core' modules
    # as imported by SmartComboBox and its dependencies.
    # This usually means running the script from the project root directory
    # (g:\\My Drive\\Python\\recipe_app) or ensuring this directory is in PYTHONPATH.
    # Also, the icon paths in 'config.py' (SMART_COMBOBOX setting) must be valid.

    demo_window = SmartComboBoxDemo()
    demo_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # This ensures that the main function is called only when the script is executed directly.
    # Add the project root to sys.path to help with module resolution if needed,
    # though it's better if the execution environment handles this (e.g., running from root).
    # import os
    # project_root = os.path.dirname(os.path.abspath(__file__))
    # if project_root not in sys.path:
    #     sys.path.insert(0, project_root)
    
    main()
