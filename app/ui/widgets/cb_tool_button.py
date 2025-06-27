"""app/ui/widgets/cb_tool_button.py

Simple wrapper around :class:`CTToolButton` used for small navigation controls.
"""

from pathlib import Path

from PySide6.QtCore import QSize, Qt

from .ct_tool_button import CTToolButton


class CBToolButton(CTToolButton):
    """Compact tool button with default pointer cursor."""

    def __init__(
        self,
        file_path: Path,
        icon_size: QSize,
        button_size: QSize | None = None,
        variant: str = "default",
        parent=None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            icon_size=icon_size,
            button_size=button_size or icon_size,
            variant=variant,
            checkable=False,
            hover_effects=True,
            parent=parent,
        )
        self.setCursor(Qt.PointingHandCursor)
