import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QGroupBox
)
from PySide6.QtGui import QPixmap, QFontDatabase
from PySide6.QtCore import Qt, QSize

# --- MOCK DATA ---
# This dictionary holds all the recipe information.
recipe_data = {
    "name": "Garlic Butter Shrimp Scampi",
    "image_url": "https://i.imgur.com/vXw2yJv.jpeg",
    "meal_type": "Dinner",
    "category": "Seafood",
    "dietary": "Low-Carb",
    "total_time": "20 minutes",
    "servings": "4 servings",
    "ingredients": [
        "1 lb large shrimp, peeled and deveined",
        "8 tbsp unsalted butter, divided",
        "5 cloves garlic, minced",
        "1/2 cup dry white wine or chicken broth",
        "1/4 cup chopped fresh parsley",
        "1/2 tsp red pepper flakes (optional)",
        "Salt and black pepper to taste",
        "1 tbsp lemon juice"
    ],
    "directions": [
        "Pat shrimp dry and season with salt and pepper.",
        "In a large skillet, melt 4 tbsp of butter over medium-high heat. Add the shrimp and cook for 1-2 minutes per side, until pink. Remove shrimp from the skillet and set aside.",
        "Reduce heat to medium. Melt the remaining 4 tbsp of butter in the same skillet. Add the minced garlic and red pepper flakes, and cook for about 1 minute until fragrant.",
        "Pour in the white wine (or broth) and bring to a simmer. Cook for 2-3 minutes, scraping up any browned bits from the bottom of the pan.",
        "Return the shrimp to the skillet. Stir in the fresh parsley and lemon juice. Sauté for another minute to heat the shrimp through.",
        "Serve immediately, garnished with extra parsley if desired."
    ],
    "notes": "Excellent served over zucchini noodles for a low-carb option, or with crusty bread to soak up the delicious sauce."
}

# --- STYLESHEET (QSS) ---
# This QSS provides a modern, dark-themed look for the application.
STYLESHEET = """
QWidget {
    background-color: #2E3440; /* Nord Polar Night */
    color: #ECEFF4; /* Nord Snow Storm */
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 14px;
}

QScrollArea {
    border: none;
}

#mainWidget {
    padding: 15px;
}

#recipeTitle {
    font-size: 32px;
    font-weight: bold;
    color: #88C0D0; /* Nord Frost */
    padding-bottom: 5px;
}

#recipeSubtitle {
    font-size: 16px;
    font-style: italic;
    color: #A3BE8C; /* Nord Frost - Green */
    padding-bottom: 15px;
}

#recipeImage {
    border: 2px solid #4C566A; /* Nord Polar Night - Lighter */
    border-radius: 8px;
    margin-bottom: 15px;
}

QGroupBox {
    background-color: #3B4252; /* Nord Polar Night - Lighter */
    border: 1px solid #4C566A;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 15px;
    padding-bottom: 10px;
    padding-left: 10px;
    padding-right: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 5px 15px;
    background-color: #81A1C1; /* Nord Frost - Blue */
    border-radius: 5px;
    color: #2E3440;
    font-weight: bold;
}

#detailsLabel {
    font-size: 15px;
    font-weight: bold;
    color: #EBCB8B; /* Nord Frost - Yellow */
    padding: 8px;
    background-color: #434C5E;
    border-radius: 5px;
}

.ingredientLabel, .directionLabel, #notesLabel {
    padding-top: 5px;
    line-height: 1.5;
}

QScrollBar:vertical {
    border: none;
    background: #2E3440;
    width: 12px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #5E81AC;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""

class RecipeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Full Recipe Details")
        self.setGeometry(100, 100, 700, 900)

        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main widget and layout
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        scroll_area.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- 1. Recipe Header ---
        title_label = QLabel(recipe_data["name"])
        title_label.setObjectName("recipeTitle")
        title_label.setWordWrap(True)

        subtitle_text = f"{recipe_data['meal_type']} | {recipe_data['category']} | {recipe_data['dietary']}"
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setObjectName("recipeSubtitle")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        # --- 2. Recipe Image ---
        image_label = QLabel()
        image_label.setObjectName("recipeImage")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        try:
            # Download image from URL
            response = requests.get(recipe_data["image_url"], stream=True)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                # Scale image to fit width while maintaining aspect ratio
                scaled_pixmap = pixmap.scaledToWidth(650, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("Image not available")
        except requests.exceptions.RequestException:
            image_label.setText("Failed to load image")

        layout.addWidget(image_label)

        # --- 3. Key Details (Time, Servings) ---
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(0, 10, 0, 10)

        time_label = QLabel(f"🕒 Total Time: {recipe_data['total_time']}")
        time_label.setObjectName("detailsLabel")
        servings_label = QLabel(f"🍽️ Servings: {recipe_data['servings']}")
        servings_label.setObjectName("detailsLabel")

        details_layout.addWidget(time_label, 1, Qt.AlignmentFlag.AlignCenter)
        details_layout.addWidget(servings_label, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(details_layout)

        # --- 4. Ingredients ---
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(ingredients_group)
        for item in recipe_data["ingredients"]:
            ingredient_label = QLabel(f"• {item}")
            ingredient_label.setProperty("class", "ingredientLabel")
            ingredient_label.setWordWrap(True)
            ingredients_layout.addWidget(ingredient_label)
        layout.addWidget(ingredients_group)

        # --- 5. Directions ---
        directions_group = QGroupBox("Directions")
        directions_layout = QVBoxLayout(directions_group)
        for i, step in enumerate(recipe_data["directions"], 1):
            direction_label = QLabel(f"<b>{i}.</b> {step}")
            direction_label.setProperty("class", "directionLabel")
            direction_label.setWordWrap(True)
            directions_layout.addWidget(direction_label)
        layout.addWidget(directions_group)

        # --- 6. Notes ---
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        notes_label = QLabel(recipe_data["notes"])
        notes_label.setObjectName("notesLabel")
        notes_label.setWordWrap(True)
        notes_layout.addWidget(notes_label)
        layout.addWidget(notes_group)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply the stylesheet to the entire application
    app.setStyleSheet(STYLESHEET)

    window = RecipeWindow()
    window.show()
    sys.exit(app.exec())
