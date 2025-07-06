"""app/ui/helpers/dialog_helpers.py

Shared helpers for dialog components such as crop dialogs.
"""

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QMessageBox, QPushButton,
                               QSizePolicy, QSpacerItem)

# Minimum crop dimension required on the original image
MIN_CROP_DIM_ORIGINAL = 280

# Custom result code used by CropDialog when the user wants to choose
# a different file.
SELECT_NEW_IMAGE_CODE = QDialog.DialogCode.Rejected + 1


def load_pixmap_or_warn(path: str, parent=None) -> QPixmap:
    """Return a QPixmap from ``path`` or show a warning dialog if it fails."""
    pixmap = QPixmap(path)
    if pixmap.isNull() and parent is not None:
        QMessageBox.warning(parent, "Image Error", f"Could not load image: {path}")
    return pixmap


def build_crop_buttons() -> tuple[QPushButton, QPushButton, QPushButton, QHBoxLayout]:
    """Create Select-New, Cancel and Save buttons with standard layout."""
    btn_select_new = QPushButton("Select New Image")
    btn_select_new.setObjectName("SelectNewButton")

    btn_cancel = QPushButton("Cancel")
    btn_cancel.setObjectName("CancelButton")

    btn_save = QPushButton("Save Crop")
    btn_save.setObjectName("SaveButton")
    btn_save.setDefault(True)

    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.addWidget(btn_select_new)
    layout.addSpacerItem(
        QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    )
    layout.addWidget(btn_cancel)
    layout.addWidget(btn_save)

    return btn_select_new, btn_cancel, btn_save, layout
