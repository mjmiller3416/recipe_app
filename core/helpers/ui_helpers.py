# Package: app.helpers

# Description: This file contains helper functions for working with PyQt UI elements. The functions in this module are used to
# extract QPushButton icons dynamically, load SVG icons with color changes, and retrieve all QPushButton instances from a parent
# widget. These functions are commonly used in PyQt applications to manage icons and button interactions.

#🔸Third-party Imports
from qt_imports import (
    QPushButton, QSize, QIcon, QPixmap, QFile, QTextStream, QSvgRenderer,
    QByteArray, QPainter, Qt, QApplication, QRectF, QWidget, 
    QRegularExpressionValidator, QLineEdit, Property, QObject, QAbstractButton, QFontMetrics)

#🔸Local Imports
from debug_logger import DebugLogger

class SidebarAnimator(QObject):
    def __init__(self, sidebar):
        super().__init__()
        self._value = sidebar.width()
        self.sidebar = sidebar

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = max(0, value)  # Clamp to non-negative
        self.sidebar.setMaximumWidth(self._value)

    value = Property(int, getValue, setValue)

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

def get_button_icons(buttons):
    """
    Extracts icon file paths from QPushButtons dynamically.

    Args:
        buttons (dict): Dictionary of QPushButton objects.

    Returns:
        dict: A dictionary mapping button names to their assigned icon paths.
    """
    icon_paths = {}

    for name, button in buttons.items():
        icon = button.icon()
        if not icon.isNull():
            icon_path = f":/icons/{name.replace('btn_', '')}.svg"
            icon_paths[name] = icon_path
            # DebugLogger().log(f"Icon path for {name}: {icon_path}")
        

    return icon_paths 

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

    svg_renderer.render(painter, icon_rect)




def svg_loader(svg_path, color, size=None, return_type=None, crisp=None):
    """
    Loads an SVG and renders it into a styled QPixmap or QIcon.

    Args:
        svg_path (str): Qt resource path (e.g. ':/icons/search.svg').
        color (str): Fill color (e.g. '#FFFFFF').
        size (QSize or tuple): Output size (defaults to 24x24).
        return_type (type): QPixmap or QIcon.
        crisp (bool, optional): If not set, auto-determined by return_type:
            - QPixmap → True
            - QIcon   → False

    Returns:
        QPixmap or QIcon
    """
    if return_type not in (QPixmap, QIcon):
        DebugLogger.log_and_raise(
            "svg_loader: return_type must be QPixmap or QIcon",
            ValueError
        )

    if crisp is None:
        crisp = return_type is QPixmap

    if size is None:
        size = QSize(24, 24)
    elif isinstance(size, tuple):
        size = QSize(*size)

    file = QFile(svg_path)
    if not file.open(QFile.ReadOnly | QFile.Text):
        DebugLogger.log(f"Failed to open SVG path: {svg_path}", "error")
        return QIcon() if return_type is QIcon else QPixmap()

    svg_data = QTextStream(file).readAll()
    file.close()

    colored_svg = svg_data.replace('fill="#000"', f'fill="{color}"')
    renderer = QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))

    if not renderer.isValid():
        DebugLogger.log(f"Invalid SVG data: {svg_path}", "error")
        return QIcon() if return_type is QIcon else QPixmap()

    dpr = QApplication.primaryScreen().devicePixelRatio() if not crisp else 1.0
    target_size = QSize(int(size.width() * dpr), int(size.height() * dpr))

    pixmap = QPixmap(target_size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, target_size.width(), target_size.height()))
    painter.end()

    if not crisp:
        pixmap.setDevicePixelRatio(dpr)
    else:
        pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return QIcon(pixmap) if return_type is QIcon else pixmap



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
    
def set_scaled_image(label, image_path, size: QSize, fallback_text="No Image", style="color: gray; font-size: 12px;"):
    """
    Loads an image from disk, scales it, and sets it on a QLabel.
    
    Args:
        label (QLabel): The target label.
        image_path (str): The image file path.
        size (QSize): The target size to scale to.
        fallback_text (str, optional): Text to display if image fails to load.
        style (str, optional): Stylesheet for fallback text.
    """
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        label.setText(fallback_text)
        label.setStyleSheet(style)
    else:
        label.setPixmap(pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
#🔸END