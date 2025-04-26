# helpers/svg_loader.py

#🔸Standard Library
import re
from typing import Union

#🔸Third-party
from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

#🔸Local Imports
from core.helpers.debug_logger import DebugLogger

# ────────────────────────────────────────────────────────────────────────────────


def svg_loader(
    svg_path: str,
    color: str,
    size: Union[QSize, tuple[int, int]] = QSize(24, 24),
    return_type: type = QPixmap,
    source_color: str = "#000"     # ← default now matches 3-digit black
) -> Union[QPixmap, QIcon]:
    """
    Load an SVG file from the filesystem, replace a specific fill color, and render it
    as a QPixmap or QIcon.

    Args:
        svg_path (str): Filesystem path to the SVG file.
        color (str): New fill color (e.g., '#FFFFFF', 'white').
        size (QSize | tuple[int, int], optional): Desired logical dimensions.
                                                Defaults to QSize(24, 24).
        return_type (type, optional): QPixmap or QIcon. Defaults to QPixmap.
        source_color (str, optional): Original fill color in the SVG to replace.
                                      Defaults to '#000000'.

    Returns:
        QPixmap | QIcon: Rendered SVG, or an empty instance on failure.

    Raises:
        ValueError: If return_type is not QPixmap or QIcon.
    """
    # Validate return type
    if return_type not in (QPixmap, QIcon):
        raise ValueError("return_type must be QPixmap or QIcon")

    # Determine logical size
    if isinstance(size, tuple) and len(size) == 2:
        logical_size = QSize(int(size[0]), int(size[1]))
    elif isinstance(size, QSize):
        logical_size = size
    else:
        logical_size = QSize(24, 24)

    if logical_size.width() <= 0 or logical_size.height() <= 0:
        logical_size = QSize(24, 24)

    # Read SVG data directly from filesystem
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_data = f.read()
    except Exception as e:
        DebugLogger.log(f"svg_loader: Failed to open SVG file {svg_path}: {e}", "error")
        return QIcon() if return_type is QIcon else QPixmap()

    # Simple color replacement
    svg_data = svg_data.replace(f'fill="{source_color}"', f'fill="{color}"')

    # Replace all occurrences of the source color with the new color
    pattern     = rf'(fill|stroke)=["\']{re.escape(source_color)}["\']'
    replacement = fr'\1="{color}"'
    svg_data    = re.sub(pattern, replacement, svg_data)
    # Render SVG via QSvgRenderer
    renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))

    # Handle HiDPI
    app = QApplication.instance()
    dpr = app.primaryScreen().devicePixelRatio() if app and app.primaryScreen() else 1.0
    physical = QSize(int(logical_size.width() * dpr), int(logical_size.height() * dpr))

    pixmap = QPixmap(physical)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, physical.width(), physical.height()))
    painter.end()
    pixmap.setDevicePixelRatio(dpr)

    # Return as QIcon if requested
    return QIcon(pixmap) if return_type is QIcon else pixmap


if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                                   QVBoxLayout, QWidget)

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # Load as QPixmap
    pixmap = svg_loader("assets/icons/servings.svg", "#2e645d", (48, 48))
    label_pix = QLabel()
    label_pix.setPixmap(pixmap)
    layout.addWidget(label_pix)

    # Load as QIcon on a button
    icon = svg_loader("assets/icons/dashboard.svg", "#32c498", QSize(32, 32), return_type=QIcon)
    button_icon = QPushButton("Icon Example")
    button_icon.setIcon(icon)
    layout.addWidget(button_icon)

    window.show()
    sys.exit(app.exec())
