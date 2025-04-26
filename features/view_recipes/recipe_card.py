
#🔸Third-Party Imports
from core.helpers.debug_logger import DebugLogger
from core.helpers.qt_imports import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                                     QPixmap, QSize, QSizePolicy, QSpacerItem,
                                     Qt, QVBoxLayout, QWidget, Signal)
from core.helpers.ui_helpers import set_scaled_image

#🔸Local Imports
from .full_recipe import FullRecipe


class RecipeCard(QFrame):
    """
    A flexible recipe card widget that supports two display modes:
    - 'full': Larger layout with a 300x300 image and vertical stacking
    - 'mini': Compact layout with 100x100 image and grid-based layout

    Both share the same style via the 'RecipeCard' object name.
    """

    recipe_clicked = Signal(int)  # Emits the recipe ID when clicked

    def __init__(self, recipe_data, mode="full", clickable=True, meal_selection=False, parent=None):
        super().__init__(parent)

        self.recipe_data = recipe_data
        self.recipe_id = recipe_data.get("id")
        self.mode = mode
        self.clickable = clickable
        self.meal_selection = meal_selection

        # Set object name for shared styling
        self.setObjectName("RecipeCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            #RecipeCard {
                background-color: #282C34;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }

            #lbl_recipe_name {
                color: #03B79E;
                font-size: 18px;
                font-weight: bold;
            }

            #lbl_cook_time, 
            #lbl_servings {
                color: #E1E1E3;
                font-size: 14px;
            }
         """)

        # Build the appropriate layout
        self.build_ui()
        self.populate()

        if self.clickable and not self.meal_selection:
            self.recipe_clicked.connect(self.show_full_recipe)

    def build_ui(self):
        """Constructs the UI layout depending on the mode."""
        if self.mode == "mini":
            self.build_mini_layout()
            self.setStyleSheet("""
            #RecipeCard {
                background-color: #282C34;
                border-top-left-radius: 0px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 10px;
            }

            #lbl_recipe_name {
                color: #03B79E;
                font-size: 18px;
                font-weight: bold;
            }

            #lbl_cook_time, 
            #lbl_servings {
                color: #E1E1E3;
                font-size: 14px;
            }
         """)
        else:
            self.build_full_layout()

    def build_full_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)  # Full control via manual spacers

        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("lbl_image")
        self.lbl_image.setMinimumSize(300, 300)
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        spacer_img_title = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        spacer_title_time = QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed)
        spacer_time_servings = QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.lbl_recipe_name = QLabel()
        self.lbl_recipe_name.setObjectName("lbl_recipe_name")
        self.lbl_recipe_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_cook_time = QLabel()
        self.lbl_cook_time.setObjectName("lbl_cook_time")
        self.lbl_cook_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_servings = QLabel()
        self.lbl_servings.setObjectName("lbl_servings")
        self.lbl_servings.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_image, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addItem(spacer_img_title)
        layout.addWidget(self.lbl_recipe_name)
        layout.addItem(spacer_title_time)
        layout.addWidget(self.lbl_cook_time)
        layout.addItem(spacer_time_servings)
        layout.addWidget(self.lbl_servings)


    def build_mini_layout(self):
        """Constructs a mini layout for the RecipeCard, suitable for side dish display."""
        # Outer layout applied to the RecipeCard
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 🟦 Create a stylable wrapper to hold the mini layout
        self.mini_wrapper = QWidget()
        self.mini_wrapper.setObjectName("MiniWrapper")
        mini_wrapper_layout = QGridLayout(self.mini_wrapper)
        mini_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        mini_wrapper_layout.setSpacing(0)

        # 🖼 Image setup
        self.lbl_image = QLabel()
        self.lbl_image.setObjectName("lbl_image")
        self.lbl_image.setFixedSize(100, 100)
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 📋 Details section (name, time, servings)
        self.details_layout = QGridLayout()
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(2)

        self.lbl_recipe_name = QLabel()
        self.lbl_recipe_name.setObjectName("lbl_recipe_name")
        self.lbl_recipe_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_cook_time = QLabel()
        self.lbl_cook_time.setObjectName("lbl_cook_time")
        self.lbl_cook_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_servings = QLabel()
        self.lbl_servings.setObjectName("lbl_servings")
        self.lbl_servings.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.details_layout.addWidget(self.lbl_recipe_name, 0, 0, 1, 2)
        time_servings_layout = QHBoxLayout()
        time_servings_layout.setSpacing(15)  # adjust spacing as needed
        time_servings_layout.setContentsMargins(0, 0, 0, 0)
        time_servings_layout.addWidget(self.lbl_cook_time)
        time_servings_layout.addWidget(self.lbl_servings)

        self.details_layout.addLayout(time_servings_layout, 1, 0, 1, 2)

        # ➕ Add widgets to mini_wrapper
        mini_wrapper_layout.addWidget(self.lbl_image, 0, 0)
        mini_wrapper_layout.addLayout(self.details_layout, 0, 1)
        self.mini_wrapper.setMinimumWidth(360)

        # ➕ Add the styled wrapper to the card's main layout
        self.layout.addWidget(self.mini_wrapper, 0, 0)

    def populate(self):
        """Populates the RecipeCard with data from the recipe_data dictionary."""
        name = self.recipe_data.get("recipe_name", "Unnamed")
        time = self.recipe_data.get("total_time", "N/A")
        servings = self.recipe_data.get("servings", "N/A")

        self.lbl_recipe_name.setText(name)
        self.lbl_cook_time.setText(f"Time: {time} min")
        self.lbl_servings.setText(f"Serves: {servings}")

        image_path = self.recipe_data.get("image_path")
        if image_path:
            self.set_image(image_path)

    def set_image(self, image_path):
        """
        Sets the image for the RecipeCard based on the provided path.
        
        Args:
            image_path (str): The path to the recipe image file.
        """
        size = QSize(100, 100) if self.mode == "mini" else QSize(300, 300)
        set_scaled_image(self.lbl_image, image_path, size)

    def mousePressEvent(self, event):
        """
        Handles mouse press events on the RecipeCard.
        
        Args:
            event (QMouseEvent): The mouse event that occurred.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.recipe_clicked.emit(self.recipe_id)

    def show_full_recipe(self, recipe_id):
        """
        Opens the FullRecipe dialog for the given recipe ID.
        
        Args:
            recipe_id (int): The ID of the recipe to display in the FullRecipe dialog.
        """
        DebugLogger.log(f"Opening FullRecipe dialog for Recipe ID: {recipe_id}", "info")
        dialog = FullRecipe(recipe_id, self)
        dialog.exec()

    @staticmethod
    def wrapped(recipe_data, aspect_ratio=3 / 4, **kwargs):
        """
        Wraps a RecipeCard in a QWidget that maintains a fixed aspect ratio.
        
        Args:
            recipe_data (dict): Recipe data to initialize the RecipeCard.
            aspect_ratio (float): Desired width / height ratio. Default is 3:4.
            **kwargs: Additional arguments to pass to RecipeCard.

        Returns:
            QWidget: A widget containing the RecipeCard with fixed aspect ratio behavior.
        """
        from core.helpers.qt_imports import QVBoxLayout, QWidget

        # Create the card
        card = RecipeCard(recipe_data, **kwargs)

        # Create wrapper widget and layout
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(card)

        # Inject resizeEvent into wrapper
        def resize_event(event):
            """ Adjust the wrapper size to maintain the aspect ratio.
            
            This method is called when the wrapper is resized. It calculates the height based on the current width and the aspect ratio.
            If the width is changed, it sets the height accordingly to maintain the aspect ratio.
            
            Args:
                event (QResizeEvent): The resize event that triggered this method.
            """
            width = wrapper.width()
            height = int(width / aspect_ratio)
            wrapper.setMinimumHeight(height)
            wrapper.setMaximumHeight(height)

        wrapper.resizeEvent = resize_event

        return wrapper
