# helpers/icons/loader.py
#🔸Standard Library
import re
from pathlib import Path
from typing import Union

#🔸Third-party
from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from core.helpers.debug_logger import DebugLogger
#🔸Local Imports
from helpers.app_helpers.file_helpers import ICONS_DIR

# ────────────────────────────────────────────────────────────────────────────────


def icon_path(name: str) -> str:
    """
    Get the filesystem path to an icon by its name.

    Args:
        name (str): Name of the icon file (without extension).

    Returns:
        str: Full path to the icon file.
    """
    if not name:
        DebugLogger.log("[ERROR] [icon_path] Empty name passed to icon_path()", "error")
        return "invalid.svg"  # or a default fallback path?
    return str(ICONS_DIR / f"{name}")

# ────────────────────────────────────────────────────────────────────────────────
class SVGLoader:
    @staticmethod
    def load(
        path: str,
        color: str,
        size: Union[QSize, tuple[int, int]] = QSize(24, 24),
        source: str = "#000",
        as_icon: bool = False, # <-- Changed parameter
    ) -> Union[QPixmap, QIcon]:
        """
        Load an SVG file from the filesystem, replace a specific fill/stroke color,
        and render it as a QPixmap or QIcon.

        Args:
            path (str): Filesystem path to the SVG file.
            color (str): New fill/stroke color (e.g., '#FFFFFF', 'white').
            size (QSize | tuple[int, int], optional): Desired logical dimensions.
                                                       Defaults to QSize(24, 24).
            source (str, optional): Original fill/stroke color in the SVG to replace.
                                    Defaults to '#000'.
            as_icon (bool, optional): If True, return a QIcon. Otherwise (default),
                                      return a QPixmap. Defaults to False.

        Returns:
            QPixmap | QIcon: Rendered SVG as the specified type, or an empty
                             instance on failure.
        """
        # determine logical size
        if isinstance(size, tuple) and len(size) == 2:
            logical_size = QSize(int(size[0]), int(size[1]))
        elif isinstance(size, QSize):
            logical_size = size
        else:
            # Default fallback if 'size' is neither tuple nor QSize
            logical_size = QSize(24, 24)

        # Ensure size is valid
        if logical_size.width() <= 0 or logical_size.height() <= 0:
            logical_size = QSize(24, 24)

        # read SVG file
        try:
            with open(path, 'r', encoding='utf-8') as f:
                svg_data = f.read()
        except Exception as e:
            DebugLogger.log(f"svg_loader: Failed to open SVG file {path}: {e}", "error")
            # Return an empty instance of the appropriate type
            return QIcon() if as_icon else QPixmap()

        # Replace the source color (both fill and stroke) with the new color
        # Use regex for potentially more robust replacement across attributes
        try:
            # Handle potential variations like fill="#000", fill='black', stroke="..." etc.
            # Ensure source color is treated as a distinct value
            pattern = rf'(fill|stroke)=(["\']){re.escape(source)}\2'
            replacement = fr'\1="{color}"'
            svg_data = re.sub(pattern, replacement, svg_data, flags=re.IGNORECASE)

            # Also handle cases where fill might be specified without quotes (less common but possible)
            # or as style attributes (more complex, maybe handle later if needed)
            # Example basic handling for fill=black (no quotes)
            pattern_no_quotes = rf'(fill|stroke)={re.escape(source)}(?!\w)'
            replacement_no_quotes = fr'\1="{color}"'
            svg_data = re.sub(pattern_no_quotes, replacement_no_quotes, svg_data, flags=re.IGNORECASE)


        except re.error as e:
             DebugLogger.log(f"svg_loader: Regex error processing {path}: {e}", "error")
             return QIcon() if as_icon else QPixmap()


        # render the SVG
        try:
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            if not renderer.isValid():
                 DebugLogger.log(f"svg_loader: Invalid SVG data after color replacement for {path}", "warning")
                 # Continue attempt to render, might still work partially or return empty
        except Exception as e: # Catch potential errors during QSvgRenderer creation
             DebugLogger.log(f"svg_loader: Failed to create QSvgRenderer for {path}: {e}", "error")
             return QIcon() if as_icon else QPixmap()


        # handle rendering
        app = QApplication.instance()
        # Ensure safe access to primaryScreen and devicePixelRatio
        dpr = 1.0
        if app:
            screen = app.primaryScreen()
            if screen:
                dpr = screen.devicePixelRatio()

        physical = QSize(int(logical_size.width() * dpr), int(logical_size.height() * dpr))

        pixmap = QPixmap(physical)
        pixmap.fill(Qt.transparent) # Use the correct Qt namespace if aliased differently
        painter = QPainter(pixmap)
        # Enable high-quality rendering hints
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Check if renderer is valid before rendering
        if renderer.isValid():
             renderer.render(painter, QRectF(0, 0, physical.width(), physical.height()))
        else:
            DebugLogger.log(f"svg_loader: Skipping render for {path} due to invalid SVG data", "warning")


        painter.end()
        pixmap.setDevicePixelRatio(dpr)

        # return the rendered pixmap or icon based on the as_icon flag
        return QIcon(pixmap) if as_icon else pixmap
    