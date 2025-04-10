from core.helpers.qt_imports import (
    QDialog, QVBoxLayout, QWidget, Qt, QPixmap, QLabel, QTextBrowser,
    QGridLayout, QHBoxLayout, QSize, QPrinter, QPrintDialog,
    QPrintPreviewDialog, QPainter, QKeySequence, QKeyEvent
)
from PySide6.QtCore import QPoint
from database import DB_INSTANCE
from core.helpers import DebugLogger
from core.application.title_bar import TitleBar
from core.managers.style_manager import StyleManager


class FullRecipe(QDialog):
    def __init__(self, recipe_id, parent=None):
        super().__init__(parent)
        self.setObjectName("FullRecipe")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setMinimumSize(682, 880)

        # Build recipe content layout
        self._build_ui()

        # Wrap in toolbar layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.content_widget)

        StyleManager(self)
        self.load_recipe(recipe_id)

    def _build_ui(self):
        self.lbl_recipe_name = QLabel("Recipe Name")
        self.lbl_recipe_name.setFont(self.lbl_recipe_name.font().setPointSize(26))

        # LEFT: Ingredient area
        self.lbl_total_time_icon = QLabel()
        self.lbl_total_time_icon.setPixmap(QPixmap(":/icons/total_time.svg"))
        self.lbl_total_time_icon.setMaximumSize(QSize(20, 20))
        self.lbl_total_time_icon.setScaledContents(True)

        self.lbl_total_time = QLabel()
        lyt_total_time = QHBoxLayout()
        lyt_total_time.setContentsMargins(0, 0, 0, 0)
        lyt_total_time.addWidget(self.lbl_total_time_icon, alignment=Qt.AlignRight)
        lyt_total_time.addWidget(self.lbl_total_time, alignment=Qt.AlignLeft)

        self.lbl_servings_icon = QLabel()
        self.lbl_servings_icon.setPixmap(QPixmap(":/icons/servings.svg"))
        self.lbl_servings_icon.setMaximumSize(QSize(20, 20))
        self.lbl_servings_icon.setScaledContents(True)

        self.lbl_servings = QLabel()
        lyt_servings = QHBoxLayout()
        lyt_servings.addWidget(self.lbl_servings_icon, alignment=Qt.AlignRight)
        lyt_servings.addWidget(self.lbl_servings, alignment=Qt.AlignLeft)

        self.tb_ingredients = QTextBrowser()

        lyt_ingredients = QVBoxLayout()
        lyt_ingredients.addLayout(lyt_total_time)
        lyt_ingredients.addLayout(lyt_servings)
        lyt_ingredients.addWidget(self.tb_ingredients)
        lyt_ingredients.setStretch(0, 1)
        lyt_ingredients.setStretch(1, 1)
        lyt_ingredients.setStretch(2, 5)

        # RIGHT: Image + Directions
        self.lbl_recipe_image = QLabel("Image")
        self.lbl_recipe_image.setMinimumSize(QSize(300, 300))
        self.lbl_recipe_image.setAlignment(Qt.AlignCenter)

        self.tb_directions = QTextBrowser()

        lyt_directions = QVBoxLayout()
        lyt_directions.addWidget(self.lbl_recipe_image, alignment=Qt.AlignHCenter)
        lyt_directions.addWidget(self.tb_directions)

        # Combine into grid
        grid = QGridLayout()
        grid.addWidget(self.lbl_recipe_name, 0, 0, 1, 2)
        grid.addLayout(lyt_ingredients, 1, 0)
        grid.addLayout(lyt_directions, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        self.content_widget = QWidget()
        self.content_widget.setLayout(grid)

    def load_recipe(self, recipe_id):
        DebugLogger.log(f"Fetching recipe with ID: {recipe_id}", "info")
        recipe = DB_INSTANCE.get_recipe(recipe_id)

        if not recipe:
            DebugLogger.log("Recipe not found!", "error")
            self.lbl_recipe_name.setText("Recipe Not Found")
            return

        self.lbl_recipe_name.setText(recipe["recipe_name"])
        self.lbl_total_time.setText(f"{recipe['total_time']} min")
        self.lbl_servings.setText(f"{recipe['servings']}")
        self.tb_directions.setPlainText(recipe["directions"])

        ingredients_text = "\n".join(
            [f"{ing['quantity']} {ing['unit']} - {ing['ingredient_name']}" for ing in recipe["ingredients"]]
        )
        self.tb_ingredients.setPlainText(ingredients_text)

        if recipe["image_path"]:
            pixmap = QPixmap(recipe["image_path"])
            if not pixmap.isNull():
                self.lbl_recipe_image.setPixmap(pixmap.scaled(300, 300))
            else:
                self.lbl_recipe_image.setText("Image Not Found")
        else:
            self.lbl_recipe_image.setText("No Image Available")

    def _render_without_toolbar_and_border(self, printer):
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
        printer = QPrinter(QPrinter.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self._render_without_toolbar_and_border)
        preview_dialog.exec()

    def print_recipe(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self._render_without_toolbar_and_border(printer)

    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.Print):
            self.print_recipe()
        else:
            super().keyPressEvent(event)
