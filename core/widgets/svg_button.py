from core.helpers.qt_imports import (QIcon, QPainter, QPixmap, QPushButton,
                                     QRectF, QSize, QStyle, QSvgRenderer, Qt)
from core.helpers.ui_helpers import (draw_svg_icon_with_text_alignment,
                                     get_colored_svg_renderer)


class SVGButton(QPushButton):
    def __init__(self, svg_path: str, color: str = "#03B79E", text: str = "",
                 parent=None, icon_size: QSize = QSize(24, 24)):
        super().__init__(text, parent)

        self.setObjectName("SVGButton")
        self.svg_path = svg_path
        self.color = color
        self.icon_size = icon_size
        self.svg_renderer = get_colored_svg_renderer(svg_path, color)

        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(False)
        self.setMinimumHeight(max(40, icon_size.height()))

        self.setStyleSheet(f"padding-left: 12 px;")

    def paintEvent(self, event):
        if not self.svg_renderer.isValid():
            return super().paintEvent(event)

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            option = self._create_style_option()
            self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)

            draw_svg_icon_with_text_alignment(
                painter=painter,
                text=self.text(),
                font_metrics=self.fontMetrics(),
                icon_size=self.icon_size,
                svg_renderer=self.svg_renderer,
                widget_width=self.width(),
                widget_height=self.height()
            )

    def _create_style_option(self):
        from PySide6.QtWidgets import QStyleOptionButton
        option = QStyleOptionButton()
        option.initFrom(self)
        option.text = self.text()

        # Trick Qt into reserving icon space
        transparent_icon = QPixmap(self.icon_size)
        transparent_icon.fill(Qt.transparent)
        option.icon = QIcon(transparent_icon)
        option.iconSize = self.icon_size  # 👈 this is the key piece you’re missing

        return option

    def sizeHint(self):
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        total_width = self.icon_size.width() + text_width + 24  # A little padding
        return QSize(total_width, max(40, self.icon_size.height() + 16))

    def set_color(self, color: str):
        """
        Updates the icon color and repaints the button.
        """
        self.color = color
        self.svg_renderer = get_colored_svg_renderer(self.svg_path, self.color)
        self.update()
