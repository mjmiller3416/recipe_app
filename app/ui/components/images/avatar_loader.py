"""app/ui/components/images/avatar_loader.py

A widget for uploading and displaying a circular user avatar
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
import shutil
import uuid

from PySide6.QtCore import QEvent, QSize, Qt, Slot
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from _data_files.user_settings import UserSettings
from app.config import AppPaths
from app.core.utils.image_utils import img_create_temp_path, img_validate_path
from app.style import Theme
from app.style.animation.animator import Animator
from app.style.icon.config import Name, Type
from app.style.theme.config import Qss
from app.ui.components.widgets import Button
from app.ui.utils.layout_utils import CornerAnchor
from ..widgets.image import CircularImage

# ── Avatar Loader ────────────────────────────────────────────────────────────────────────────
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
        self.setObjectName("AvatarLoader")

        # register for component-specific styling
        Theme.register_widget(self, Qss.AVATAR_LOADER)

        # fix the widget's size to the diameter you want:
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
        self.main_layout.addWidget(self.avatar_display, alignment=Qt.AlignCenter)

        # edit button
        self.edit_button = Button(
            label=" Edit",
            type=Type.DEFAULT,
            parent=self
        )
        self.edit_button.setIcon(Name.EDIT)
        self.edit_button.setIconSize(20, 20)
        self.edit_button.setStateDefault("primary")
        self.edit_button.setObjectName("AvatarEditButton")
        # self.edit_button.setVisible(True)  # hidden until hover

        self.anchor = CornerAnchor(
            anchor_widget=self.avatar_display,
            target_widget=self.edit_button,
            corner="bottom-left",
            x_offset=0,
            y_offset=0,
        )

        self.edit_button.adjustSize()
        self.edit_button.raise_()

    def _connect_signals(self):
        """Connect signals to slots."""
        self.edit_button.clicked.connect(self._on_edit_clicked)

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
                temp = img_create_temp_path("avatar_crop", ".png")
                cropped.save(str(temp), "PNG", -1)
                self.set_avatar_from_path(str(temp))

    def load_avatar(self):
        """Load from settings or placeholder."""
        avatar_filename = self.settings.get("avatar_path")
        path = str(AppPaths.ICONS_DIR / "user_placeholder.svg")
        if avatar_filename:
            avatar_path = AppPaths.USER_PROFILE_DIR / avatar_filename
            if img_validate_path(avatar_path):
                path = str(avatar_path)

        self.avatar_display.setImagePath(path)

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
        self.avatar_display.setImagePath(str(perm_path))

    # ── Event Handlers ─────────────────────────────────────────────────────────────
    def enterEvent(self, event: QEvent):
        """Handle mouse hover to show edit indication.

        Args:
            event (QEvent): The enter event.
        """
        # fade widget using Animator
        self.fade_animation = Animator.fade_widget(self, duration=200, start=1.0, end=0.7)
        self.fade_animation.start()
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """Handle mouse leaving to restore normal appearance.

        Args:
            event (QEvent): The leave event.
        """
        # restore opacity using Animator
        self.fade_animation = Animator.fade_widget(self, duration=200, start=0.7, end=1.0)
        self.fade_animation.start()
        return super().leaveEvent(event)
