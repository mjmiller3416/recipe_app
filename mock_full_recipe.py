import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QPixmap, QPainter, QBrush, QColor

class RecipeCard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Title
        title = QLabel("Classic Beef Bolognese")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Tags container
        tags_container = QWidget()
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.addStretch()

        # Create tags
        tags = [
            ("🏠", "Dinner"),
            ("🥩", "Beef"),
            ("❤️", "High-Protein")
        ]

        for icon, text in tags:
            tag = QLabel(f"{icon} {text}")
            tag.setObjectName("tag")
            tags_layout.addWidget(tag)
            tags_layout.addSpacing(20)

        tags_layout.addStretch()
        main_layout.addWidget(tags_container)

        # Image placeholder
        image_placeholder = QLabel()
        image_placeholder.setObjectName("imagePlaceholder")
        image_placeholder.setText("1200 × 600")
        image_placeholder.setAlignment(Qt.AlignCenter)
        image_placeholder.setMinimumHeight(300)
        main_layout.addWidget(image_placeholder)

        # Info cards container - single frame with grid layout
        info_container = QFrame()
        info_container.setObjectName("infoContainer")
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(20, 15, 20, 15)
        info_layout.setSpacing(40)

        # Info cards data
        info_data = [
            ("🕐", "Total Time", "2 hours 30 mins"),
            ("👥", "Servings", "6"),
            ("🏷️", "Category", "Beef"),
            ("❤️", "Dietary", "High-Protein")
        ]

        for i, (icon, title, value) in enumerate(info_data):
            info_item = self.create_info_item(icon, title, value)
            info_layout.addWidget(info_item)

        main_layout.addWidget(info_container)

        # Recipe content container
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(30)

        # Left column - Ingredients
        ingredients_widget = self.create_ingredients_section()
        content_layout.addWidget(ingredients_widget, 1)

        # Right column - Directions and Notes
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(25)

        directions_widget = self.create_directions_section()
        notes_widget = self.create_notes_section()

        right_layout.addWidget(directions_widget)
        right_layout.addWidget(notes_widget)
        right_layout.addStretch()

        content_layout.addWidget(right_column, 2)

        main_layout.addWidget(content_container)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_info_item(self, icon, title, value):
        item = QWidget()

        layout = QVBoxLayout(item)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setObjectName("infoIcon")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("infoTitle")
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("infoValue")
        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return item

    def create_ingredients_section(self):
        widget = QFrame()
        widget.setObjectName("sectionCard")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        header = QLabel("🗒️ Ingredients")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Ingredients list
        ingredients = [
            ("2 tbsp", "Olive Oil"),
            ("1 large", "Onion, finely chopped"),
            ("2", "Carrots, finely chopped"),
            ("2", "Celery stalks, finely chopped"),
            ("2 cloves", "Garlic, minced"),
            ("1 lb", "Ground Beef"),
            ("1/2 lb", "Ground Pork"),
            ("1 cup", "Dry Red Wine"),
            ("28 oz can", "Crushed Tomatoes"),
            ("1 cup", "Whole Milk"),
            ("1 tsp", "Nutmeg, freshly grated"),
            ("to taste", "Salt & Black Pepper"),
            ("1 lb", "Tagliatelle Pasta"),
            ("for serving", "Parmesan Cheese")
        ]

        for amount, ingredient in ingredients:
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)

            amount_label = QLabel(amount)
            amount_label.setObjectName("ingredientAmount")
            amount_label.setMinimumWidth(80)

            ingredient_label = QLabel(ingredient)
            ingredient_label.setObjectName("ingredientName")

            item_layout.addWidget(amount_label)
            item_layout.addWidget(ingredient_label)
            item_layout.addStretch()

            item_widget = QWidget()
            item_widget.setLayout(item_layout)
            layout.addWidget(item_widget)

        return widget

    def create_directions_section(self):
        widget = QFrame()
        widget.setObjectName("sectionCard")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        header = QLabel("📋 Directions")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Directions list
        directions = [
            "Heat olive oil in a large pot or Dutch oven over medium heat. Add onion, carrots, and celery. Cook until softened, about 10 minutes.",
            "Add garlic and cook for another minute until fragrant.",
            "Increase heat to medium-high, add ground beef and pork. Break up the meat with a spoon and cook until browned.",
            "Pour in the red wine and cook until it has evaporated, scraping any browned bits from the bottom of the pot.",
            "Stir in the crushed tomatoes, milk, and nutmeg. Season with salt and pepper.",
            "Bring to a simmer, then reduce heat to low, cover, and let it cook for at least 2 hours, stirring occasionally. The longer it simmers, the better the flavor.",
            "About 15 minutes before the sauce is done, cook the pasta according to package directions until al dente.",
            "Serve the sauce over the pasta, topped with a generous amount of Parmesan cheese."
        ]

        for i, direction in enumerate(directions, 1):
            direction_layout = QHBoxLayout()
            direction_layout.setContentsMargins(0, 0, 0, 0)
            direction_layout.setAlignment(Qt.AlignLeft)

            number_label = QLabel(f"{i}.")
            number_label.setObjectName("directionNumber")
            number_label.setMinimumWidth(25)
            number_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            text_label = QLabel(direction)
            text_label.setObjectName("directionText")
            text_label.setWordWrap(True)
            text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            direction_layout.addWidget(number_label)
            direction_layout.addWidget(text_label)

            direction_widget = QWidget()
            direction_widget.setLayout(direction_layout)
            layout.addWidget(direction_widget)

        return widget

    def create_notes_section(self):
        widget = QFrame()
        widget.setObjectName("sectionCard")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header
        header = QLabel("📝 Notes")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Notes text
        notes_text = QLabel("This sauce freezes beautifully. Make a double batch and save half for a quick weeknight meal.")
        notes_text.setObjectName("notesText")
        notes_text.setWordWrap(True)
        layout.addWidget(notes_text)

        return widget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Recipe Card Application")
        self.setMinimumSize(1200, 800)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create recipe card
        recipe_card = RecipeCard()
        scroll.setWidget(recipe_card)

        self.setCentralWidget(scroll)

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        style = """
        QMainWindow {
            background-color: #f5f2e8;
        }

        QScrollArea {
            border: none;
            background-color: #f5f2e8;
        }

        QLabel#title {
            font-size: 42px;
            font-weight: bold;
            color: #8B4513;
            font-family: Georgia, serif;
            margin: 20px 0;
        }

        #tag {
            background-color: #ffffff;
            color: #8B4513;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid #e0d5c7;
        }

        QLabel#imagePlaceholder {
            background-color: #d0c7ba;
            color: #8B4513;
            font-size: 48px;
            font-weight: bold;
            border-radius: 12px;
            margin: 20px 0;
        }

        QFrame#infoContainer {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0d5c7;
            margin: 10px 0;
        }

        QLabel#infoIcon {
            font-size: 24px;
            color: #8B4513;
        }

        QLabel#infoTitle {
            font-size: 14px;
            color: #8B4513;
            font-weight: 500;
        }

        QLabel#infoValue {
            font-size: 16px;
            color: #333333;
            font-weight: bold;
        }

        QFrame#sectionCard {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0d5c7;
            margin: 5px;
        }

        QLabel#sectionHeader {
            font-size: 24px;
            font-weight: bold;
            color: #8B4513;
            margin-bottom: 10px;
            font-family: Georgia, serif;
        }

        QLabel#ingredientAmount {
            font-size: 14px;
            color: #8B4513;
            font-weight: bold;
            padding-right: 15px;
        }

        QLabel#ingredientName {
            font-size: 14px;
            color: #333333;
            font-weight: normal;
        }

        QLabel#directionNumber {
            font-size: 16px;
            color: #8B4513;
            font-weight: bold;
            padding-right: 10px;
        }

        QLabel#directionText {
            font-size: 14px;
            color: #333333;
            line-height: 1.5;
            margin-bottom: 10px;
        }

        QLabel#notesText {
            font-size: 14px;
            color: #666666;
            font-style: italic;
            line-height: 1.5;
        }
        """

        self.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
