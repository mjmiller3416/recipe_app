"""app/ui/utils/svg_loader.py

Provides functions and classes for loading and recoloring SVG icons into QPixmaps or 
QIcons with support for high-DPI screens.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import re
from pathlib import Path
from typing import Union

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from app.config import AppPaths
from app.core.dev_tools import DebugLogger


# ── Class Definition ────────────────────────────────────────────────────────────
class SVGLoader:
    """Utility class for loading and recoloring SVG files.

    Supports output as QPixmap or QIcon, with optional color replacement and device pixel ratio scaling.
    """

    @staticmethod
    def load(
        file_path: Path,
        color: str,
        size: Union[QSize, tuple[int, int]] = QSize(24, 24),
        source: str = "#000",
        as_icon: bool = False,
    ) -> Union[QPixmap, QIcon]:
        """Load an SVG file, optionally recolor it, and render as QPixmap or QIcon.

        Args:
            file_path (str): Filesystem path to the SVG file.
            color (str): New fill/stroke color to apply.
            size (QSize or tuple[int, int], optional): Logical size for rendering. Defaults to QSize(24, 24).
            source (str, optional): Original fill/stroke color to replace. Defaults to "#000".
            as_icon (bool, optional): If True, returns a QIcon; otherwise, a QPixmap. Defaults to False.

        Returns:
            QPixmap or QIcon: The rendered and recolored SVG image, or an empty object on failure.
        """
        # ── Determine Logical Size ──
        if isinstance(size, tuple) and len(size) == 2:
            logical_size = QSize(int(size[0]), int(size[1]))
        elif isinstance(size, QSize):
            logical_size = size
        else:
            logical_size = QSize(24, 24) # fallback size

        # ── Validate Size ──
        if logical_size.width() <= 0 or logical_size.height() <= 0:
            logical_size = QSize(24, 24)

        # ── Read SVG ──
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                svg_data = f.read()
        except Exception as e:
            DebugLogger.log(f"svg_loader: Failed to open SVG file {file_path}: {e}", "error")
            return QIcon() if as_icon else QPixmap() # return empty instance on error

        # ── Note ───────────────────────────────────────────────────────────── #
        # Replace the source color (both fill and stroke) with the new color
        # Use regex for potentially more robust replacement across attributes
        # ───────────────────────────────────────────────────────────────────── #

        try:
            # ── Note ────────────────────────────────────────────────────────────────────────#
            # Handle potential variations like fill="#000", fill='black', stroke="..." etc.
            # Ensure source color is treated as a distinct value
            # Example (Standard Fill): fill="#000" or fill='black' or stroke="..."
            # ─────────────────────────────────────────────────────────────────────────────── #
            pattern = rf'(fill|stroke)=(["\']){re.escape(source)}\2'
            replacement = fr'\1="{color}"'
            svg_data = re.sub(pattern, replacement, svg_data, flags=re.IGNORECASE)

            # ── Note ───────────────────────────────────────────────────────────────────────────────── #
            # Also handle cases where fill might be specified without quotes (less common but possible)
            # or as style attributes (more complex, maybe handle later if needed)
            # Example (No Quotes Fill): fill=#000 or fill=black or stroke=...
            # ───────────────────────────────────────────────────────────────────────────────────────── #
            pattern_no_quotes = rf'(fill|stroke)={re.escape(source)}(?!\w)'
            replacement_no_quotes = fr'\1="{color}"'
            svg_data = re.sub(pattern_no_quotes, replacement_no_quotes, svg_data, flags=re.IGNORECASE)

        except re.error as e: # catch regex errors
             DebugLogger.log(f"svg_loader: Regex error processing {file_path}: {e}", "error")
             return QIcon() if as_icon else QPixmap() # return empty instance on error


        # ── Render SVG ──
        try:
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            if not renderer.isValid():
                 DebugLogger.log(f"svg_loader: Invalid SVG data after color replacement for {file_path}", "warning")
                 # Continue attempt to render, might still work partially or return empty
        except Exception as e: # Catch potential errors during QSvgRenderer creation
             DebugLogger.log(f"svg_loader: Failed to create QSvgRenderer for {file_path}: {e}", "error")
             return QIcon() if as_icon else QPixmap()


        # ── Handle Rendering ──
        app = QApplication.instance()

        # check device pixel ratio
        dpr = 1.0
        if app:
            screen = app.primaryScreen()
            if screen:
                dpr = screen.devicePixelRatio()

        # calculate physical size based on logical size and device pixel ratio
        physical = QSize(int(logical_size.width() * dpr), int(logical_size.height() * dpr))

        # ── Create QPixmap ──
        pixmap = QPixmap(physical)
        pixmap.fill(Qt.transparent) # use transparent background
        painter = QPainter(pixmap)

        # ── Enable HQ Rendering ──
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # ── Validate Renderer ──
        if renderer.isValid():
             renderer.render(painter, QRectF(0, 0, physical.width(), physical.height()))
        else:
            DebugLogger.log(f"svg_loader: Skipping render for {file_path} due to invalid SVG data", "warning")

        # ── Clean Up ──
        painter.end()
        pixmap.setDevicePixelRatio(dpr)

        # ── Retun QIcon or QPixmap ──
        return QIcon(pixmap) if as_icon else pixmap
