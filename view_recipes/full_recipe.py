from qt_imports import (
    QDialog, QVBoxLayout, QWidget, Qt, QPixmap, QPainter,
    QPrinter, QPrintDialog, QPrintPreviewDialog, QKeySequence, QKeyEvent
)
from PySide6.QtCore import QPoint
from .ui_full_recipe import Ui_FullRecipe
from app.database import DB_INSTANCE
from debug_logger import DebugLogger
from app.application.title_bar import TitleBar
from style_manager import StyleManager

class FullRecipe(QDialog):
    """
    FullRecipe dialog displays a complete recipe and supports printing
    the window content (without the window border and toolbar) exactly
    as it appears on screen.
    """
    def __init__(self, recipe_id, parent=None):
        super().__init__(parent)
        self.setObjectName("FullRecipe")
        self.ui = Ui_FullRecipe()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        # Create and store the content widget that holds the grid layout
        self.content_widget = QWidget(self)
        self.content_widget.setLayout(self.ui.gridLayout)

        # Create a main layout for the dialog that includes a custom toolbar (title bar)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.content_widget)

        # Apply additional styles and load the recipe
        StyleManager(self)
        self.load_recipe(recipe_id)

    def load_recipe(self, recipe_id):
        """Fetch and display the recipe details."""
        DebugLogger.log(f"Fetching recipe with ID: {recipe_id}", "info")
        recipe = DB_INSTANCE.get_recipe(recipe_id)
        
        if not recipe:
            DebugLogger.log("Recipe not found!", "error")
            self.ui.lbl_recipe_name.setText("Recipe Not Found")
            return

        self.ui.lbl_recipe_name.setText(recipe["recipe_name"])
        self.ui.lbl_total_time.setText(f"{recipe['total_time']} min")
        self.ui.lbl_servings.setText(f"{recipe['servings']}")
        self.ui.tb_directions.setPlainText(recipe["directions"])
        
        ingredients_text = "\n".join(
            [f"{ing['quantity']} {ing['unit']} - {ing['ingredient_name']}" for ing in recipe["ingredients"]]
        )
        self.ui.tb_ingredients.setPlainText(ingredients_text)
        
        if recipe["image_path"]:
            pixmap = QPixmap(recipe["image_path"])
            if not pixmap.isNull():
                self.ui.lbl_recipe_image.setPixmap(pixmap.scaled(300, 300))
            else:
                self.ui.lbl_recipe_image.setText("Image Not Found")
        else:
            self.ui.lbl_recipe_image.setText("No Image Available")

    def _render_without_toolbar_and_border(self, printer):
        """
        Helper method that hides the toolbar and renders only the content widget,
        so the printed output does not include the window border or title bar.
        """
        # Temporarily hide the toolbar
        toolbar_visible = self.title_bar.isVisible()
        self.title_bar.setVisible(False)
        
        painter = QPainter(printer)
        # Use QPageLayout to get the printable area in pixels
        page_rect = printer.pageLayout().paintRectPixels(printer.resolution())
        # Scale using the content widget's size instead of the full dialog's size
        scale_x = page_rect.width() / float(self.content_widget.width())
        scale_y = page_rect.height() / float(self.content_widget.height())
        scale = min(scale_x, scale_y)
        painter.scale(scale, scale)
        
        # Render only the content widget (which holds your recipe details)
        self.content_widget.render(painter, QPoint(0, 0))
        painter.end()
        
        # Restore the toolbar's visibility for on-screen display
        self.title_bar.setVisible(toolbar_visible)

    def show_print_preview(self):
        """Display a print preview dialog that omits the window border and toolbar."""
        printer = QPrinter(QPrinter.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self._render_without_toolbar_and_border)
        preview_dialog.exec()

    def print_recipe(self):
        """Open a print dialog and print the recipe content without the window border."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            self._render_without_toolbar_and_border(printer)

    def keyPressEvent(self, event: QKeyEvent):
        """Intercept keyboard shortcuts, e.g., CTRL+P for printing."""
        if event.matches(QKeySequence.Print):
            self.print_recipe()
        else:
            super().keyPressEvent(event)
