"""Delegate responsible for drawing recipe cards in the browser grid."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem

from app.style.icon.config import Name
from app.style.icon.svg_loader import SVGLoader
from app.style.theme_controller import Theme
from app.ui.views.recipe_browser.models import RecipeListModel


class RecipeCardDelegate(QStyledItemDelegate):
    """Custom delegate that paints recipe cards using QPainter."""

    def __init__(self, parent=None, card_size: QSize | None = None):
        super().__init__(parent)
        self._card_size = card_size or QSize(280, 420)
        self._image_height = int(self._card_size.height() * 0.65)
        self._radius = 10
        self._image_radius = 8
        self._heart_size = QSize(28, 28)
        self._heart_cache: dict[tuple[bool, str], Optional[object]] = {}
        self._icon_size = QSize(20, 20)
        self._fallback_font_size = 14

    # Painting -------------------------------------------------------------
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        palette = self._palette()
        bg_color = QColor(palette.get("surface_container", "#1f1f1f"))
        hover_color = QColor(palette.get("surface_container_high", bg_color.lighter(108)))
        outline_color = QColor(palette.get("outline_variant", bg_color.lighter(120)))
        text_color = QColor(palette.get("on_surface", "#f5f5f5"))
        secondary_text = QColor(palette.get("on_surface_variant", "#c7c7c7"))

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        card_rect = opt.rect.adjusted(6, 6, -6, -6)
        background_path = QPainterPath()
        background_path.addRoundedRect(card_rect, self._radius, self._radius)

        painter.fillPath(background_path, hover_color if opt.state & QStyle.State_MouseOver else bg_color)

        if opt.state & (QStyle.State_MouseOver | QStyle.State_Selected):
            painter.setPen(outline_color)
            painter.drawPath(background_path)

        # Image
        image_rect = self._image_rect(card_rect)
        self._paint_image(painter, image_rect, index)

        # Heart overlay
        favorite = bool(index.data(RecipeListModel.FAVORITE_ROLE))
        heart_pixmap = self._heart_pixmap(favorite, palette)
        heart_rect = self._heart_rect(image_rect)
        if heart_pixmap:
            painter.drawPixmap(heart_rect, heart_pixmap)

        # Title
        y_offset = image_rect.bottom() + 10
        title_rect = QRect(card_rect.left() + 10, y_offset, card_rect.width() - 20, 48)
        base_size = self._effective_point_size(opt.font)
        title_font = QFont(opt.font)
        title_font.setPointSizeF(base_size + 2)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(text_color)
        title = index.data(RecipeListModel.TITLE_ROLE) or ""
        painter.drawText(title_rect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, title)

        # Meta row
        meta_top = title_rect.bottom() + 6
        meta_height = card_rect.bottom() - meta_top - 10
        meta_rect = QRect(card_rect.left() + 10, meta_top, card_rect.width() - 20, meta_height)
        self._paint_meta_row(painter, meta_rect, index, secondary_text, text_color, opt.font)

        painter.restore()

    def sizeHint(self, option=None, index=None) -> QSize:  # noqa: ANN001
        return QSize(self._card_size.width(), self._card_size.height())

    # Helpers --------------------------------------------------------------
    def _paint_image(self, painter: QPainter, rect: QRect, index) -> None:
        pixmap = index.data(RecipeListModel.IMAGE_ROLE)
        if pixmap is None:
            return

        painter.save()
        # scale pixmap to cover rect (keep aspect)
        scaled = pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = rect.left() + (rect.width() - scaled.width()) // 2
        y = rect.top() + (rect.height() - scaled.height()) // 2

        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect, self._image_radius, self._image_radius)
        painter.setClipPath(clip_path)
        painter.drawPixmap(QPoint(x, y), scaled)
        painter.restore()

    def _paint_meta_row(
        self,
        painter: QPainter,
        rect: QRect,
        index,
        secondary_text: QColor,
        primary_text: QColor,
        base_font: QFont,
    ) -> None:
        servings = index.data(RecipeListModel.SERVINGS_ROLE) or ""
        time_text = index.data(RecipeListModel.TIME_ROLE) or ""

        column_width = rect.width() // 2
        servings_rect = QRect(rect.left(), rect.top(), column_width, rect.height())
        time_rect = QRect(rect.left() + column_width, rect.top(), column_width, rect.height())

        base_size = self._effective_point_size(base_font)
        heading_font = QFont(base_font)
        heading_font.setPointSizeF(max(base_size - 1, 9))
        value_font = QFont(base_font)
        value_font.setPointSizeF(base_size + 1)
        value_font.setBold(True)

        painter.save()
        self._draw_meta_column(
            painter,
            servings_rect,
            "Servings",
            servings,
            icon_name=Name.SERVINGS,
            label_color=secondary_text,
            value_color=primary_text,
            heading_font=heading_font,
            value_font=value_font,
        )
        self._draw_meta_column(
            painter,
            time_rect,
            "Time",
            time_text,
            icon_name=Name.TOTAL_TIME,
            label_color=secondary_text,
            value_color=primary_text,
            heading_font=heading_font,
            value_font=value_font,
        )
        painter.restore()

    def _draw_meta_column(
        self,
        painter: QPainter,
        rect: QRect,
        label: str,
        value: str,
        icon_name: Name,
        label_color: QColor,
        value_color: QColor,
        heading_font: QFont,
        value_font: QFont,
    ) -> None:
        icon = self._meta_icon(icon_name, value_color.name())
        center_x = rect.center().x()
        y = rect.top()

        if icon:
            icon_rect = QRect(QPoint(center_x - self._icon_size.width() // 2, y), self._icon_size)
            painter.drawPixmap(icon_rect, icon)
            y = icon_rect.bottom() + 4

        painter.setPen(label_color)
        painter.setFont(heading_font)
        label_rect = QRect(rect.left(), y, rect.width(), 18)
        painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, label)

        painter.setPen(value_color)
        painter.setFont(value_font)
        value_rect = QRect(rect.left(), label_rect.bottom() + 2, rect.width(), 24)
        painter.drawText(value_rect, Qt.AlignHCenter | Qt.AlignTop, value)

    def _heart_rect(self, image_rect: QRect) -> QRect:
        margin = 12
        return QRect(
            image_rect.right() - self._heart_size.width() - margin,
            image_rect.top() + margin,
            self._heart_size.width(),
            self._heart_size.height(),
        )

    def _image_rect(self, card_rect: QRect) -> QRect:
        image_height = min(self._image_height, card_rect.height() - 120)
        return QRect(card_rect.left(), card_rect.top(), card_rect.width(), image_height)

    def _heart_pixmap(self, filled: bool, palette: dict[str, str]):
        color = palette.get("primary", "#ff4d67") if filled else palette.get("on_surface_variant", "#c7c7c7")
        cache_key = (filled, color)
        if cache_key in self._heart_cache:
            return self._heart_cache[cache_key]

        icon_name = Name.FAV_FILLED if filled else Name.FAV
        pixmap = SVGLoader.load(icon_name.value.name.path, color, size=self._heart_size)
        self._heart_cache[cache_key] = pixmap
        return pixmap

    def _meta_icon(self, icon_name: Name, color: str):
        cache_key = (icon_name.value.name.path, color)
        cache = getattr(self, "_meta_cache", {})
        if cache_key in cache:
            return cache[cache_key]
        pixmap = SVGLoader.load(icon_name.value.name.path, color, size=self._icon_size)
        cache[cache_key] = pixmap
        self._meta_cache = cache
        return pixmap

    def editorEvent(self, event, model, option, index):  # noqa: ANN001
        # Handle favorite toggling when clicking the heart region
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            card_rect = option.rect.adjusted(6, 6, -6, -6)
            heart_rect = self._heart_rect(self._image_rect(card_rect))
            if heart_rect.contains(event.pos()):
                current = bool(index.data(RecipeListModel.FAVORITE_ROLE))
                source_index = index
                # Support proxy models by mapping if available
                if hasattr(model, "mapToSource"):
                    source_index = model.mapToSource(index)
                    source_model = model.sourceModel()
                else:
                    source_model = model
                source_model.setData(source_index, not current, RecipeListModel.FAVORITE_ROLE)
                return True
        return super().editorEvent(event, model, option, index)

    def _palette(self) -> dict[str, str]:
        try:
            return Theme.get_current_color_map()
        except Exception:
            return {}

    def _effective_point_size(self, font: QFont) -> float:
        """Return a safe point size with a sensible fallback."""
        size = font.pointSizeF()
        if size <= 0:
            return float(self._fallback_font_size)
        return size
