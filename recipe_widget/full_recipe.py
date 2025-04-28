# 🔸 Third-party Imports
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont, QKeyEvent, QKeySequence, QPainter, QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PySide6.QtWidgets import (QDialog, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QScrollArea, QTextEdit, QVBoxLayout,
                               QWidget)

from core.application.title_bar import TitleBar
from helpers.debug_logger import DebugLogger
# 🔸 Local Imports
from database import DB_INSTANCE


class FullRecipe(QDialog):
    """
    A dialog for displaying and printing a complete recipe.

    This view renders a recipe's name, image, ingredients, directions,
    and metadata in a custom-styled window. It also supports print
    preview and clean PDF-style printing without UI chrome.

    Args:
        recipe_id (int): The ID of the recipe to load.
        parent (QWidget, optional): The parent widget. Defaults to None.
    """

    def __init__(self, recipe_id, parent=None):
        super().__init__(parent)
        self.setObjectName("FullRecipe")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.recipe_id = None
        self.recipe_data = None

        self._build_ui()
        self.load_recipe(recipe_id)

    def _build_ui(self):
        # ---- Outer Layout and Title Bar ----
        wrapper = QVBoxLayout(self)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(0)

        self.title_bar = TitleBar(self)
        wrapper.addWidget(self.title_bar)
        self.title_bar.btn_maximize.setVisible(False)
        self.title_bar.btn_toggle_sidebar.setVisible(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ---- Recipe Name Label ----
        self.lbl_recipe_name = QLabel("Recipe Name")
        self.lbl_recipe_name.setObjectName("lbl_recipe_name")
        font = QFont()
        font.setPointSize(26)
        self.lbl_recipe_name.setFont(font)
        layout.addWidget(self.lbl_recipe_name)

        # ---- Recipe Image ----
        self.lbl_recipe_image = QLabel()
        self.lbl_recipe_image.setObjectName("lbl_recipe_image")
        self.lbl_recipe_image.setMinimumHeight(250)
        self.lbl_recipe_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_recipe_image)

        # ---- Metadata (Time + Servings) ----
        self.lbl_total_time = QLabel("0 min")
        self.lbl_total_time.setObjectName("lbl_total_time")
        self.lbl_servings = QLabel("0")
        self.lbl_servings.setObjectName("lbl_servings")

        meta_layout = QHBoxLayout()
        meta_layout.addWidget(self.lbl_total_time)
        meta_layout.addStretch()
        meta_layout.addWidget(self.lbl_servings)
        layout.addLayout(meta_layout)

        # ---- Ingredients + Directions ----
        self.tb_ingredients = QTextEdit()
        self.tb_ingredients.setObjectName("tb_ingredients")
        self.tb_ingredients.setReadOnly(True)

        self.tb_directions = QTextEdit()
        self.tb_directions.setObjectName("tb_directions")
        self.tb_directions.setReadOnly(True)

        content_frame = QFrame()
        content_frame.setObjectName("content_frame")
        grid = QGridLayout(content_frame)
        grid.addWidget(self.tb_ingredients, 0, 0)
        grid.addWidget(self.tb_directions, 0, 1)

        layout.addWidget(content_frame)

        # ---- Scrollable Container ----
        container = QWidget()
        container.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(container)

        wrapper.addWidget(scroll)

        self.content_widget = container

    def load_recipe(self, recipe_id):
        """
        Fetch and display all relevant recipe data into the UI.

        Args:
            recipe_id (int): The ID of the recipe to load from the database.
        """
        # Log the fetch attempt
        DebugLogger.log(f"Fetching recipe with ID: {recipe_id}", "info")
        recipe = DB_INSTANCE.get_recipe(recipe_id)

        # Handle missing recipe case
        if not recipe:
            DebugLogger.log("Recipe not found!", "error")
            self.lbl_recipe_name.setText("Recipe Not Found")
            return

        # Set recipe metadata
        self.lbl_recipe_name.setText(recipe["recipe_name"])
        self.lbl_total_time.setText(f"{recipe['total_time']} min")
        self.lbl_servings.setText(f"{recipe['servings']}")
        self.tb_directions.setPlainText(recipe["directions"])

        # Format and populate ingredients
        ingredients_text = "\n".join(
            [f"{ing['quantity']} {ing['unit']} - {ing['ingredient_name']}"
            for ing in recipe["ingredients"]]
        )
        self.tb_ingredients.setPlainText(ingredients_text)

        # Load recipe image
        if recipe["image_path"]:
            pixmap = QPixmap(recipe["image_path"])
            if not pixmap.isNull():
                self.lbl_recipe_image.setPixmap(pixmap.scaled(300, 300))
            else:
                self.lbl_recipe_image.setText("Image Not Found")
        else:
            # Handle case where no image is available
            self.lbl_recipe_image.setText("No Image Available")

    def _render_without_toolbar_and_border(self, printer):
        """
        Render the content widget only (without the toolbar and frame)
        for clean print output.

        Args:
            printer (QPrinter): The printer to render onto.
        """
        toolbar_visible = self.title_bar.isVisible()
        self.title_bar.setVisible(False)

        painter = QPainter(printer)
        page_rect = printer.pageLayout().paintRectPixels(printer.resolution())

        scale_x = page_rect.width() / float(self.content_widget.width())
        scale_y = page_rect.height() / float(self.content_widget.height())
        scale = min(scale_x, scale_y)
        painter.scale(scale, scale)

        self.content_widget.render(painter, QPoint(0, 0))
        painter.end()

        self.title_bar.setVisible(toolbar_visible)

    def show_print_preview(self):
        """Display a print preview of the recipe without UI chrome."""
        printer = QPrinter(QPrinter.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self._render_without_toolbar_and_border)
        preview_dialog.exec()

    def print_recipe(self):
        """Print the recipe content without window decorations."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            self._render_without_toolbar_and_border(printer)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle keyboard shortcuts like Ctrl+P to trigger printing.

        Args:
            event (QKeyEvent): The key event triggered by the user.
        """
        if event.matches(QKeySequence.Print):
            self.print_recipe()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    import argparse
    import sys

    from PySide6.QtWidgets import QApplication

    # point this at wherever your FullRecipe lives
    from core.modules.recipe_module import Recipe
    from database import DB_INSTANCE

    parser = argparse.ArgumentParser(
        description="Launch FullRecipe dialog against your real DB"
    )
    parser.add_argument(
        "recipe_id",
        type=int,
        nargs="?",
        default=1,
        help="The ID of the recipe to load from your DB",
    )
    args = parser.parse_args()

    # 💾 fetch from *your* database
    raw_data = DB_INSTANCE.get_recipe(args.recipe_id)
    if not raw_data:
        print(f"❌ No recipe found with ID {args.recipe_id}")
        sys.exit(1)

    # 📦 wrap it in your Recipe helper (just to prove it’s working)
    recipe = Recipe(raw_data)
    print(
        f"✅ Loaded “{recipe.name}” "
        f"({recipe.formatted_total_time()}, serves {recipe.formatted_servings()})"
    )

    # 🚀 launch the dialog
    app = QApplication(sys.argv)
    dlg = FullRecipe(args.recipe_id)
    dlg.resize(800, 600)
    dlg.show()
    sys.exit(app.exec())
