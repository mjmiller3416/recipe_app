import types

from PySide6.QtCore import (Property, QByteArray, QFile, QObject, QRectF,
                            QSize, Qt, QTextStream)
from PySide6.QtGui import (QColor, QFontMetrics, QIcon, QPainter, QPaintEvent,
                           QPen, QPixmap, QRegularExpressionValidator)
from PySide6.QtSvg import QSvgRenderer
#🔸Third-party Imports
from PySide6.QtWidgets import (QAbstractButton, QApplication,  # Added QLabel
                               QFrame, QLabel, QLayout, QLineEdit, QPushButton,
                               QWidget)

from core.application.config import DEBUG_LAYOUT_BORDERS, icon_path
#🔸Local Imports
from core.helpers import DebugLogger

# Package: app.helpers

# Description: This file contains helper functions for working with PyQt UI elements. The functions in this module are used to
# extract QPushButton icons dynamically, load SVG icons with color changes, and retrieve all QPushButton instances from a parent
# widget. These functions are commonly used in PyQt applications to manage icons and button interactions.




def wrap_layout(layout_class: type[QLayout], name: str) -> tuple[QWidget, QLayout]:
    """
    Creates a QWidget wrapper with a named objectName and assigns the given layout.

    Args:
        layout_class (type): QVBoxLayout or QHBoxLayout
        name (str): Object name for styling via QSS

    Returns:
        (QWidget, QLayout): The container widget and its layout
    """
    container = QWidget()
    container.setObjectName(name)
    layout = layout_class(container)
    layout.setContentsMargins(0, 0, 0, 0)
    return container, layout

class HoverButton(QPushButton):
    """
    Custom QPushButton that supports hover-based icon switching.
    """

    def __init__(self, icon_default, icon_hover, icon_checked=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_default = icon_default
        self.icon_hover = icon_hover
        self.icon_checked = icon_checked or icon_default
        self.setIcon(self.icon_checked if self.isChecked() else self.icon_default)

    def enterEvent(self, event):
        if not self.isChecked():
            self.setIcon(self.icon_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self.setIcon(self.icon_default)
        super().leaveEvent(event)

    def setChecked(self, checked):
        super().setChecked(checked)
        self.setIcon(self.icon_checked if checked else self.icon_default)

def get_all_buttons(parent_widget):
    """
    Returns a list of all QPushButton instances inside the given parent widget.

    Args:
        parent_widget (QWidget): The parent container (e.g., self or self.ui).

    Returns:
        dict: A dictionary where keys are button objectNames and values are QPushButton objects.
    """
    return {btn.objectName(): btn for btn in parent_widget.findChildren(QAbstractButton)}

def get_button_icons(buttons: dict) -> dict:
    """
    Extracts icon file paths from QPushButtons dynamically.

    Args:
        buttons (dict): Dictionary of QPushButton objects.

    Returns:
        dict: A dictionary mapping button names to their assigned icon paths.
    """
    return {
    name: icon_path(name.removeprefix("btn_"))
    for name in buttons.keys()
    if name and name.startswith("btn_")
    }

def get_colored_svg_renderer(svg_path: str, color: str) -> QSvgRenderer:
    """
    Returns a QSvgRenderer with the specified fill color injected.
    Assumes the SVG uses 'fill="#000"' or similar for primary color.

    Args:
        svg_path (str): Path to SVG file or Qt resource.
        color (str): Fill color to replace existing fills.

    Returns:
        QSvgRenderer
    """
    file = QFile(svg_path)
    if not file.open(QFile.ReadOnly | QFile.Text):
        DebugLogger.log(f"Failed to open SVG path: {svg_path}", "error")
        return QSvgRenderer()  # Will be invalid

    svg_data = QTextStream(file).readAll()
    file.close()

    # Replace all fills that are black-ish
    import re
    colored_svg = re.sub(r'fill=["\']#?0{3,6}["\']', f'fill="{color}"', svg_data, flags=re.IGNORECASE)

    return QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))

def draw_svg_icon_with_text_alignment(painter: QPainter,
                                      text: str,
                                      font_metrics: QFontMetrics,
                                      icon_size,
                                      svg_renderer,
                                      widget_width,
                                      widget_height,
                                      spacing=6):
    """
    Draws an SVG icon aligned with text as a centered group.

    Args:
        painter (QPainter): The active painter object.
        text (str): Button text.
        font_metrics (QFontMetrics): For measuring text width.
        icon_size (QSize): Size of the icon.
        svg_renderer (QSvgRenderer): The SVG renderer.
        widget_width (int): Width of the button.
        widget_height (int): Height of the button.
        spacing (int): Gap between icon and text.
    """
    text_width = font_metrics.horizontalAdvance(text)
    total_width = icon_size.width() + spacing + text_width
    start_x = (widget_width - total_width) / 2

    icon_rect = QRectF(
        start_x,
        (widget_height - icon_size.height()) / 2,
        icon_size.width(),
        icon_size.height()
    )


def svg_loader(svg_path: str,
               color: str,
               size: QSize | tuple | None = None,
               return_type: type = QPixmap,
               source_color: str = "#000000") -> QPixmap | QIcon:
    """
    Loads an SVG, replaces a specified source color, and renders it
    into a styled QPixmap or QIcon with HiDPI support.

    Args:
        svg_path (str): Qt resource path (e.g. ':/icons/search.svg') or file system path.
        color (str): The desired *new* fill color (e.g., '#FFFFFF', 'white').
                     Ensure this is a valid color representation for Qt/SVG.
        size (QSize | tuple, optional): Target logical size (width, height).
                                         Defaults to QSize(24, 24).
        return_type (type, optional): The desired return type, either QPixmap
                                      or QIcon. Defaults to QPixmap.
        source_color (str, optional): The *original* fill color within the SVG
                                      to be replaced. Defaults to '#000000' (black).
                                      Case-sensitive.

    Returns:
        QPixmap | QIcon: The rendered icon or pixmap. Returns an empty QPixmap
                         or QIcon if loading or rendering fails.

    Raises:
        ValueError: If return_type is not QPixmap or QIcon.

    Note:
        Performs simple, case-sensitive string replacement of 'fill="<source_color>"'.
        Reliable for single-color icons designed for this. May fail for complex SVGs.
    """
    # --- Basic Input Validation ---
    if return_type not in (QPixmap, QIcon):
        DebugLogger.log_and_raise(
            "svg_loader: return_type must be QPixmap or QIcon",
            ValueError
        )

    #DebugLogger.log(f"svg_loader: ENTERED - Path='{svg_path}', Color='{color}', Size='{size}', ReturnType='{return_type.__name__}', SourceColor='{source_color}'", "info")

    # --- *** Size Handling and logical_size Definition (This was missing/misplaced) *** ---
    if size is None:
        logical_size = QSize(24, 24) # Assignment
        #DebugLogger.log(f"svg_loader: Size is None, logical_size set to default: {logical_size}", "debug")
    elif isinstance(size, tuple):
        # Ensure tuple is valid (e.g., 2 elements, numeric) before unpacking
        if len(size) == 2 and isinstance(size[0], (int, float)) and isinstance(size[1], (int, float)):
             logical_size = QSize(int(size[0]), int(size[1])) # Assignment
             #DebugLogger.log(f"svg_loader: Size is tuple {size}, logical_size converted to: {logical_size}", "debug")
        else:
             #DebugLogger.log(f"svg_loader: Invalid tuple format for size '{size}'. Using default.", "warning")
             logical_size = QSize(24, 24) # Fallback Assignment
    elif isinstance(size, QSize):
        logical_size = size         # Assignment
        #DebugLogger.log(f"svg_loader: Size is QSize {size}, logical_size set to: {logical_size}", "debug")
    else:
        #DebugLogger.log(f"svg_loader: Invalid size type '{type(size)}'. Using default 24x24.", "warning")
        logical_size = QSize(24, 24) # Assignment

    # --- Secondary Size Validation ---
    if not logical_size.isValid() or logical_size.width() <= 0 or logical_size.height() <= 0:
         #DebugLogger.log(f"svg_loader: Invalid logical_size dimensions '{logical_size}' after conversion. Using default.", "warning")
         logical_size = QSize(24, 24)

    # --- Debug Check (Optional but helpful) ---
    # This confirms logical_size was definitely assigned by the block above
    if 'logical_size' not in locals():
        #DebugLogger.log("CRITICAL DEBUG: logical_size was NOT defined by the size handling block!", "error")
        # Avoid crash later by assigning default, but indicates a fundamental flaw if this prints
        logical_size = QSize(24, 24)
    #else:
        #DebugLogger.log(f"DEBUG: logical_size defined as type {type(logical_size)} value {logical_size} before loading file", "debug")
    # --- End Debug Check ---

    # --- Load SVG Data ---
    file = QFile(svg_path)
    svg_data = None # Initialize svg_data
    if not file.open(QFile.ReadOnly | QFile.Text):
        #DebugLogger.log(f"svg_loader: ERROR - Failed to open SVG path: {svg_path}", "error")
        return QIcon() if return_type is QIcon else QPixmap()
    try:
        stream = QTextStream(file)
        svg_data = stream.readAll()
        #DebugLogger.log(f"svg_loader: Successfully read {len(svg_data)} chars from {svg_path}", "info")
    except Exception as e:
        #DebugLogger.log(f"svg_loader: ERROR - Failed to read SVG data from {svg_path}: {e}", "error")
        return QIcon() if return_type is QIcon else QPixmap()
    finally:
        file.close()

    if svg_data is None:
         #DebugLogger.log(f"svg_loader: ERROR - svg_data is None after attempting read for {svg_path}", "error")
         return QIcon() if return_type is QIcon else QPixmap()

    # --- Color Replacement ---
    target_string = f'fill="{source_color}"'
    replacement_string = f'fill="{color}"'
    #DebugLogger.log(f"svg_loader: Attempting replacement: Find '{target_string}', Replace with '{replacement_string}'", "info")

    #if target_string not in svg_data:
         #DebugLogger.log(f"svg_loader: WARNING - Target string '{target_string}' NOT FOUND in raw SVG data for {svg_path}. Replacement will fail.", "warning")
         # Debug clues (optional but kept for now)
         #if f"fill='{source_color}'" in svg_data: DebugLogger.log(f"svg_loader: DEBUG CLUE - Found 'fill='{source_color}'' (single quotes) instead.", "info")
         #if f'fill = "{source_color}"' in svg_data: DebugLogger.log(f"svg_loader: DEBUG CLUE - Found 'fill = \"{source_color}\"' (spaces around =) instead.", "info")
         #if source_color=="#000" and 'fill="black"' in svg_data: DebugLogger.log(f"svg_loader: DEBUG CLUE - Found 'fill=\"black\"' instead.", "info")

    colored_svg_data = svg_data.replace(target_string, replacement_string)

    #if svg_data == colored_svg_data:
        #DebugLogger.log(f"svg_loader: WARNING - Replacement had NO effect for {svg_path}. Output SVG data is identical to input.", "warning")
    #else:
        #DebugLogger.log(f"svg_loader: SUCCESS - Replacement occurred for {svg_path}. Length before: {len(svg_data)}, after: {len(colored_svg_data)}.", "info")

    # --- Render SVG ---
    svg_bytes = QByteArray(colored_svg_data.encode("utf-8"))
    renderer = QSvgRenderer(svg_bytes)

    """ if not renderer.isValid():
        DebugLogger.log(f"svg_loader: ERROR - QSvgRenderer is NOT VALID after color replacement for path: {svg_path}.", "error")
        DebugLogger.log(f"svg_loader: Invalid SVG Data Snippet (first 500 chars):\n{colored_svg_data[:500]}", "error") # Log snippet
        return QIcon() if return_type is QIcon else QPixmap()
    else:
         DebugLogger.log(f"svg_loader: QSvgRenderer is VALID for {svg_path}", "info") """

    # --- HiDPI Handling ---
    app_instance = QApplication.instance()
    dpr = app_instance.primaryScreen().devicePixelRatio() if app_instance and app_instance.primaryScreen() else 1.0

    # Calculate physical_size using the QSize logical_size (already defined and validated)
    physical_size = QSize(int(logical_size.width() * dpr), int(logical_size.height() * dpr))
    #DebugLogger.log(f"svg_loader: DPR={dpr}, LogicalSize={logical_size}, PhysicalSize={physical_size}", "debug")

    # Create the target pixmap
    pixmap = QPixmap(physical_size)
    pixmap.fill(Qt.transparent) # Use Qt.transparent

    # --- Painting ---
    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        renderer.render(painter, QRectF(0.0, 0.0, physical_size.width(), physical_size.height()))
        #DebugLogger.log(f"svg_loader: Rendering completed for {svg_path}", "debug")
    except Exception as e:
         DebugLogger.log(f"svg_loader: ERROR during rendering for {svg_path}: {e}", "error")
         # Consider returning empty object on render failure too
         painter.end() # Ensure painter is ended on exception
         return QIcon() if return_type is QIcon else QPixmap()
    finally:
        # Ensure painter is ended if no exception occurred during render
        if painter.isActive():
             painter.end()

    # --- Final Pixmap Setup ---
    pixmap.setDevicePixelRatio(dpr)

    # --- Return Result ---
    result = QIcon(pixmap) if return_type is QIcon else pixmap
    #DebugLogger.log(f"svg_loader: EXITED NORMALLY - Returning {return_type.__name__} for {svg_path}", "info")
    return result

def apply_error_style(widget: QWidget, error_message: str = None):
    """
    Highlights the invalid field with a red border and shows a tooltip.

    Args:
        widget (QWidget): The specific UI widget that caused the error.
        error_message (str): The validation error message to display.
    """

    widget.setStyleSheet("border: 1px solid red;")

    if error_message:
        widget.setToolTip(error_message)

def clear_error_styles(widget: QLineEdit):
    """
    Removes error highlighting and tooltip from validated UI field.

    Args:
        widget (QLineEdit): Remove error styling effects from widget.
    """
    widget.setStyleSheet("")
    widget.setToolTip("")

def dynamic_validation(widget: QLineEdit, validation_rule):
    """
    Applies real-time validation to a QLineEdit widget based on a predefined validation type.

    Args:
        widget (QLineEdit): The input field to validate.
        validation_type (str): The type of validation (must match a key in VALIDATION_RULES).
        error_message (str): The error message to display when validation fails.
    """

    # Create a new validator instance for this widget
    validator = validation_rule(widget)
    widget.setValidator(validator)

    def validate_input():
        text = widget.text()
        state = validator.validate(text, 0)[0]  # Get validation state

        if state == QRegularExpressionValidator.Acceptable:
            clear_error_styles(widget)
        else:
            apply_error_style(widget)

    widget.textChanged.connect(validate_input)  # Real-time validation

def set_scaled_image(label: QLabel, image_path: str, size: QSize, fallback_text="No Image", style="color: gray; font-size: 12px;"):
    """
    Loads an image from disk, scales it, and sets it on a QLabel.
    Ensures the label has a fixed size matching the target scaled size.

    Args:
        label (QLabel): The target label.
        image_path (str): The image file path.
        size (QSize): The target size to scale to and set on the label.
        fallback_text (str, optional): Text to display if image fails to load.
        style (str, optional): Stylesheet for fallback text.
    """
    pixmap = QPixmap(image_path)
    label.setFixedSize(size) # Ensure label size matches target
    label.setAlignment(Qt.AlignCenter) # Center content

    if pixmap.isNull():
        label.clear() # Clear any previous pixmap
        label.setText(fallback_text)
        label.setStyleSheet(style)
        #DebugLogger.log(f"set_scaled_image: Failed to load {image_path}. Set fallback text.", "warning")
    else:
        scaled_pixmap = pixmap.scaled(size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # Crop the pixmap to the exact target size if aspect ratio didn't match perfectly
        if scaled_pixmap.size() != size:
             # Center the crop
             x_offset = (scaled_pixmap.width() - size.width()) / 2
             y_offset = (scaled_pixmap.height() - size.height()) / 2
             scaled_pixmap = scaled_pixmap.copy(x_offset, y_offset, size.width(), size.height())

        label.setPixmap(scaled_pixmap)
        label.setText("") # Clear any fallback text
        label.setStyleSheet("") # Clear fallback style
        #DebugLogger.log(f"set_scaled_image: Successfully loaded and scaled {image_path} to {size}.", "debug")



#🔸END
