"""app/ui/components/images/avatar_loader.py

A widget for uploading and displaying a circular user avatar
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import shutil
import tempfile
import uuid
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve, QEvent, QPropertyAnimation,
    QSize, Qt, Slot
)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QGraphicsOpacityEffect,
    QToolButton, QVBoxLayout, QWidget
)

from app.config import AppPaths
from ..widgets.circular_image import CircularImage
from app.theme_manager.icon import Icon
from data_files.user_settings import UserSettings
from app.theme_manager.icon.config import AppIcon

# ── Constants ───────────────────────────────────────────────────────────────────
TEMP_IMAGE_DIR = Path(tempfile.gettempdir()) / "app_avatar_crops"
TEMP_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# ── Class Definition ────────────────────────────────────────────────────────────
class AvatarLoader(QWidget):
    """
    A widget for uploading and displaying a circular user avatar,
    now using CircularImage for perfect circles + QSS borders.
    """

    def __init__(self, size: QSize = QSize(96, 96), parent=None):
        """Initializes the AvatarLoader widget.
        Args:
            size (QSize, optional): Diameter of the avatar circle. Defaults to QSize(96, 96).
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._size = size
        self.settings = UserSettings()

        # fix the widget’s size to the diameter you want:
        self.setFixedSize(self._size)
        self._setup_ui()
        self._connect_signals()
        self.load_avatar()

    def _setup_ui(self):
        """Set up the UI components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # create the circular avatar display
        diameter = self._size.width()
        self.avatar_display = CircularImage(diameter=diameter)
        self.avatar_display.setObjectName("AvatarImage")
        self.main_layout.addWidget(self.avatar_display)

        # add opacity effect for hover animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # create the edit button overlay
        self.edit_button = QToolButton(self)
        self.edit_button.setFixedSize(self._size)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.setToolTip("Edit Avatar")
        self.edit_button.setStyleSheet("background-color: transparent; border: none;")

        self.edit_icon = Icon(AppIcon.EDIT, size=QSize(24, 24))
        self.edit_icon.setVisible(False)

        self.edit_button.raise_()
        self.edit_icon.raise_()

    def _connect_signals(self):
        """Connect signals to slots."""
        self.edit_button.clicked.connect(self._on_edit_clicked)

    def load_avatar(self):
        """Load from settings or placeholder."""
        avatar_filename = self.settings.get("avatar_path")
        path = str(AppPaths.ICONS_DIR / "user_placeholder.svg")
        if avatar_filename:
            avatar_path = AppPaths.USER_PROFILE_DIR / avatar_filename
            if avatar_path.exists():
                path = str(avatar_path)

        pix = QPixmap(path)
        self.avatar_display.setPixmap(pix)

    @Slot()
    def _on_edit_clicked(self):
        """Handle avatar edit button click."""
        from app.ui.components.dialogs import CropDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Avatar Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return

        dialog = CropDialog(file_path, self)
        if dialog.exec():
            cropped = dialog.get_final_cropped_pixmap()
            if not cropped.isNull():
                temp = TEMP_IMAGE_DIR / f"avatar_crop_{uuid.uuid4().hex}.png"
                cropped.save(str(temp), "PNG", -1)
                self.set_avatar_from_path(str(temp))

    def set_avatar_from_path(self, temp_file_path: str):
        """Persist new avatar, update display.

        Args:
            temp_file_path (str): Path to the cropped avatar image.
        """
        profile_dir = AppPaths.USER_PROFILE_DIR
        profile_dir.mkdir(parents=True, exist_ok=True)

        perm_filename = f"avatar_{uuid.uuid4().hex}.png"
        perm_path = profile_dir / perm_filename
        shutil.copy(temp_file_path, perm_path)

        self.settings.set("avatar_path", perm_filename)
        self.avatar_display.setPixmap(QPixmap(str(perm_path)))

    # ── Event Handlers ─────────────────────────────────────────────────────────────
    def resizeEvent(self, event):
        """Ensure overlay widgets are centered.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self.edit_button.setGeometry(0, 0, self.width(), self.height())
        self.edit_icon.move(
            (self.width() - self.edit_icon.width()) // 2,
            (self.height() - self.edit_icon.height()) // 2
        )

    def enterEvent(self, event: QEvent):
        """Handle mouse hover to show edit indication.

        Args:
            event (QEvent): The enter event.
        """
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.7)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.start()
        self.edit_icon.setVisible(True)
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """Handle mouse leaving to restore normal appearance.

        Args:
            event (QEvent): The leave event.
        """
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setStartValue(self.opacity_effect.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.start()
        self.edit_icon.setVisible(False)
        return super().leaveEvent(event)
