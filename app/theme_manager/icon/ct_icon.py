"""app/theme_manager/icon/ct_icon.py

Module providing CTIcon widget for theme-aware SVG icons.

CTIcon is a QLabel-based widget that renders an SVG icon and adapts
to theme changes automatically.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

from app.config import AppIcon
from app.theme_manager.icon.loader import IconLoader
from app.theme_manager.icon.factory import IconFactory


# ── Class Definition ────────────────────────────────────────────────────────────
class CTIcon(QLabel):
    """
    QLabel widget that displays a themed SVG icon.
    Automatically updates when the application theme changes.
    """

    def __init__(
        self,
        icon_or_path: AppIcon | str | Path,
        icon_size: QSize | None = None,
        variant: str | None = None,
        parent=None
    ):
        """
        Args:
            icon_or_path (AppIcon | str | Path): AppIcon enum or path to the SVG icon file.
            icon_size (QSize): The size of the icon.
            variant (str, optional): The variant of the icon. Defaults to "DEFAULT".
            parent: The parent widget. Defaults to None.
        """
        from app.config.app_icon import AppIcon, ICON_SPECS
        # support passing AppIcon enum directly
        if isinstance(icon_or_path, AppIcon):
            spec = ICON_SPECS[icon_or_path]
            file_path = spec.path
            icon_size = spec.size
            variant = spec.variant
        else:
            file_path = icon_or_path
            # icon_size and variant must be provided when using a raw path
            if icon_size is None:
                raise ValueError("icon_size must be provided when using a file path")
            variant = variant or "DEFAULT"

        super().__init__(parent)

        self.file_path = file_path
        self.size = icon_size
        # Normalize variant: uppercase if string, leave dict as-is
        if isinstance(variant, str):
            self.variant = variant.upper()
        else:
            self.variant = variant

        self.setFixedSize(self.size)
        self.setStyleSheet("background-color: transparent;")
        self.setObjectName(Path(file_path).stem)

        IconLoader().register(self)  # auto-tracked for theme refresh
        self.refresh_theme(IconLoader().palette)

    def refresh_theme(self, palette: dict):
        """Refreshes the displayed icon with current theme colors."""
        themed_icon = IconFactory(self.file_path, self.size, self.variant)
        self.setPixmap(themed_icon.pixmap())
