"""app/ui/widgets/circular_image.py

A QWidget that displays a QPixmap as a perfect circle, with customizable border via Q_PROPERTY.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
from PySide6.QtCore import Property, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QStyle, QStyleOption, QWidget

# ── Class Definition ────────────────────────────────────────────────────────────
class CircularImage(QWidget):
    """Displays a 1:1 QPixmap as a circle, with Q_PROPERTY border styling.

    Attributes:
        diameter (int): Diameter of the circular image.
        borderWidth (int): Width of the border around the circle.
        borderColor (QColor): Color of the border around the circle.
    """

    def __init__(self, diameter: int, parent=None):
        """Initializes the CircularImage widget.
        Args:
            diameter (int): Diameter of the circular image.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._diameter     = diameter
        self._orig_pixmap  = None
        self._scaled_pixmap= None

        # border properties
        self._border_width = 0
        self._border_color = QColor(0, 0, 0, 0)

        self.setFixedSize(diameter, diameter)
        self.setAttribute(Qt.WA_StyledBackground, True)

    # ── Properties ──
    def getBorderWidth(self) -> int:
        return self._border_width

    def setBorderWidth(self, w: int):
        self._border_width = w
        self.update()

    def getBorderColor(self) -> QColor:
        return self._border_color

    def setBorderColor(self, c):
        self._border_color = QColor(c)
        self.update()

    borderWidth = Property(int,    getBorderWidth, setBorderWidth)
    borderColor = Property(QColor, getBorderColor, setBorderColor)

    # —— Pixmap loader ——
    def setPixmap(self, pixmap: QPixmap):
        self._orig_pixmap   = pixmap
        self._scaled_pixmap = pixmap.scaled(
            self._diameter, self._diameter,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        self.update()

    # —— Paint ——
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 1) Let QSS draw the background if you have one
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        if not self._orig_pixmap:
            return

        D = self._diameter
        w = self._border_width
        half = w * 0.5

        # ── Draw the inner pixmap circle (diameter = D - w) ──
        inner_rect = QRectF(half, half, D - w, D - w)
        painter.save()
        path = QPainterPath()
        path.addEllipse(inner_rect)
        painter.setClipPath(path)

        # Scale on the fly so it always exactly fits that inner_rect:
        scaled = self._orig_pixmap.scaled(
            int(D - w), int(D - w),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        painter.drawPixmap(inner_rect.toRect(), scaled)
        painter.restore()

        # ── Stroke the full-size outer circle (diameter = D) ──
        if w > 0:
            pen = QPen(self._border_color, w)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            # since pen is centered on the path, draw at half-offset:
            painter.drawEllipse(QRectF(half, half, D - w, D - w))
