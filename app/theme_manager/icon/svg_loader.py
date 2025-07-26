"""app/theme_manager/icon/svg_loader.py

Module for loading and recoloring SVG icons.

Provides functions to load and recolor SVG files into QPixmaps or QIcons
with support for high-DPI screens. It replaces specified colors in the SVG
data before rendering.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import re
from pathlib import Path
from typing import Union

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from dev_tools import DebugLogger

# Fallback path for default error icon
_ERROR_ICON_PATH = Path(__file__).parent.parent.parent / "assets" / "icons" / "error.svg"

def _replace_svg_colors(svg_data: str, source: str, new_color: str) -> str:
    """
    Replace fill and stroke occurrences of source color with new_color in SVG data.
    Handles both quoted and unquoted attributes.
    """
    # Replace attributes with optional quotes
    pattern = r'(fill|stroke)=([\'\"]?)' + re.escape(source) + r'\2'
    replacement = r'\1="' + new_color + r'"'
    svg_data = re.sub(pattern, replacement, svg_data, flags=re.IGNORECASE)
    # Replace unquoted attributes
    pattern_no_quotes = r'(fill|stroke)=' + re.escape(source) + r'(?!\w)'
    svg_data = re.sub(pattern_no_quotes, replacement, svg_data, flags=re.IGNORECASE)
    return svg_data


# ── Class Definition ─────────────────────────────────────────────────────────────────────────
class SVGLoader:
    """Utility class for loading and recoloring SVG files with caching."""
    
    # Class-level cache for all SVG operations
    _cache: dict[tuple, Union[QPixmap, QIcon]] = {}

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
            file_path (Path): Path to the SVG file.
            color (str): New fill/stroke color to apply.
            size (QSize or tuple[int, int], optional): Logical size for rendering.
                Defaults to QSize(24, 24).
            source (str, optional): Original fill/stroke color to replace.
                Defaults to "#000".
            as_icon (bool, optional): If True, returns a QIcon; otherwise, a QPixmap.
                Defaults to False.

        Returns:
            QPixmap or QIcon: The rendered and recolored SVG image, or an
            empty object on failure.
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
            
        # ── Check Cache ──
        cache_key = (str(file_path), color, logical_size.width(), logical_size.height(), source, as_icon)
        if cache_key in SVGLoader._cache:
            return SVGLoader._cache[cache_key]

        # ── Read SVG ──
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_svg = f.read()
        except Exception as e:
            DebugLogger.log(f"svg_loader: Failed to open SVG file {file_path}: {e}", "warning")
            return QIcon(str(_ERROR_ICON_PATH)) if as_icon else QPixmap(str(_ERROR_ICON_PATH))
        svg_data = raw_svg

        # ── Note ───────────────────────────────────────────────────────────── #
        # Replace the source color (both fill and stroke) with the new color
        # Use regex for potentially more robust replacement across attributes
        # ───────────────────────────────────────────────────────────────────── #

        try:
            svg_data = _replace_svg_colors(raw_svg, source, color)
        except re.error as e:  # catch regex errors
            DebugLogger.log(f"svg_loader: Regex error processing {file_path}: {e}", "warning")
            svg_data = raw_svg


        # ── Render SVG ──
        try:
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            if not renderer.isValid():
                DebugLogger.log(
                    f"svg_loader: Invalid SVG data after color replacement for {file_path}",
                    "warning"
                )
                # Continue attempt to render, might still work partially or return empty
        except Exception as e:  # Catch potential errors during QSvgRenderer creation
            DebugLogger.log(
                f"svg_loader: Failed to create QSvgRenderer for {file_path}: {e}",
                "warning"
            )
            return QIcon(str(_ERROR_ICON_PATH)) if as_icon else QPixmap(str(_ERROR_ICON_PATH))


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
            DebugLogger.log(
                f"svg_loader: Skipping render for {file_path} due to invalid SVG data",
                "warning"
            )

        # ── Clean Up ──
        painter.end()
        pixmap.setDevicePixelRatio(dpr)

        # ── Return QIcon or QPixmap ──
        result = QIcon(pixmap) if as_icon else pixmap
        
        # ── Cache Result ──
        SVGLoader._cache[cache_key] = result
        return result
    
    @classmethod
    def clear_cache(cls):
        """Clear the SVG cache. Useful for memory management or theme changes."""
        cls._cache.clear()
