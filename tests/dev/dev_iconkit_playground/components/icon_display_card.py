"""tests/dev/dev_iconkit_playground/components/icon_display_card.py

Displays a QLabel + QPushButton + QToolButton version of a themed icon variant.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.iconkit.icon_widgets.ct_button import ButtonIcon
from app.ui.iconkit.icon_widgets.ct_icon import Icon
from app.ui.iconkit.icon_widgets.ct_tool_button import ToolButtonIcon


class IconDisplayCard(QWidget):
    def __init__(self, file_name: str, size: QSize, variant: str):
        super().__init__()
        self.setObjectName(f"card_{file_name}_{variant}")

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        label = QLabel(f"<b>Variant:</b> {variant}")
        layout.addWidget(label)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(20)

        # QLabel + Icon (static)
        lbl_icon = Icon(file_name, size, variant)
        lbl_icon.setToolTip("Icon (QLabel)")
        icon_row.addWidget(lbl_icon)

        # QPushButton + Icon
        btn_icon = ButtonIcon(file_name, size, variant, label="PushBtn", hover_effects=True)
        btn_icon.setToolTip("ButtonIcon (QPushButton)")
        icon_row.addWidget(btn_icon)

        # QToolButton + Icon
        tool_btn_icon = ToolButtonIcon(file_name, size, variant, hover_effects=True)
        tool_btn_icon.setToolTip("ToolButtonIcon (QToolButton)")
        icon_row.addWidget(tool_btn_icon)

        layout.addLayout(icon_row)
