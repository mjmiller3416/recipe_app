from pathlib import Path
from PySide6.QtCore import QSize
from app.config import AppIcon, ICON_SIZE
from app.ui.components.widgets.button.button import Button
from app.theme_manager.icon.loader import IconLoader

class PillButton(Button):
    def __init__(
        self,
        icon_or_path: AppIcon | str | Path,
        icon_size: QSize = ICON_SIZE,
        variant: str = "DEFAULT",
        height: int = 32,
        label: str = "",
        checkable: bool = False,
        hover_effects: bool = False,
        parent=None
    ):
        """
        Pill-style button: fully rounded corners,
        themed background & text, with optional icon.
        """
        super().__init__(
            icon_or_path,
            icon_size,
            variant,
            height,
            label,
            checkable,
            hover_effects,
            parent
        )

        # initial pill styling
        self._apply_pill_style(IconLoader.get_palette)

        # re-register so our refresh_theme gets called
        IconLoader.register(self)

    def _apply_pill_style(self, palette: dict) -> None:
        radius = int(self.height() / 2)

        # border-radius = half height, some horizontal padding
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: {radius}px;
                padding: 0 12px;
            }}
        """)

    def refresh_theme(self, palette: dict) -> None:
        # update icon first
        super().refresh_theme(palette)
        # then re-apply pill colors
        self._apply_pill_style(palette)
