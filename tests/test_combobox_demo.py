"""combobox_styles_demo.py

Material‑style combo with a **custom overlay popup** (QFrame) instead of the
native QComboBox popup. This guarantees perfect rounded corners and acts as an
overlay so the layout doesn't shift.

Run:  python combobox_styles_demo.py
"""
from __future__ import annotations

from typing import Iterable, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                               QFrame, QGridLayout, QGroupBox, QLabel,
                               QListWidget, QListWidgetItem, QMainWindow,
                               QSizePolicy, QVBoxLayout, QWidget)


# ── Overlay popup implementation ──────────────────────────────────────────────
class ComboOverlayPopup(QFrame):
    """Frameless, rounded popup with a QListWidget.

    • Uses Qt.Popup so it closes automatically on click-away / focus loss.
    • Styled with border‑radius; no square edges can peek through.
    • Emits selection via the provided callback.
    • Applies a **rounded mask on resize** to eliminate any right-edge bleed on
      some Windows/DPI combos.
    """

    def __init__(self, parent: QWidget, on_select: callable[[str, int], None]):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setObjectName("ComboOverlayPopup")
        self.on_select = on_select

        # Ensure true transparent outside the rounded panel
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.list = QListWidget(self)
        self.list.setObjectName("ComboOverlayList")
        self.list.setUniformItemSizes(True)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.setFrameShape(QFrame.NoFrame)
        self.list.viewport().setAutoFillBackground(False)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)  # inner padding to respect rounded corners
        lay.addWidget(self.list)

        # Style the popup itself (rounded panel)
        self.setStyleSheet(
            """
            #ComboOverlayPopup {
                background: #242424;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
            }
            #ComboOverlayList {
                background: transparent;
                border: none;
                outline: 0;
            }
            #ComboOverlayList::item {
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 8px;
            }
            #ComboOverlayList::item:hover { background: #333333; }
            #ComboOverlayList::item:selected { background: #2e5aa6; color: white; }
            #ComboOverlayList QScrollBar:vertical { background: transparent; width: 10px; margin: 8px 6px 8px 0; }
            #ComboOverlayList QScrollBar::handle:vertical { background: #454545; border-radius: 5px; min-height: 24px; }
            #ComboOverlayList QScrollBar::add-line:vertical,
            #ComboOverlayList QScrollBar::sub-line:vertical,
            #ComboOverlayList QScrollBar::add-page:vertical,
            #ComboOverlayList QScrollBar::sub-page:vertical { background: transparent; height: 0; width: 0; }
            """
        )

        # Close on Enter/Return/Escape from within the list
        self.list.keyPressEvent = self._wrap_keypress(self.list.keyPressEvent)

        # Make sure clicks select + close
        self.list.itemClicked.connect(self._select_from_click)

    # Keep the mask synced to size to prevent any visible square edges
    def resizeEvent(self, e):
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QPainterPath
        super().resizeEvent(e)
        r = 10.0
        # Slight inset avoids pixel rounding artifacts on some DPIs
        rect = QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7)
        path = QPainterPath()
        path.addRoundedRect(rect, r, r)
        self.setMask(path.toFillPolygon().toPolygon())

    # Populate items (idempotent)
    def set_items(self, items: Iterable[str], current_index: int) -> None:
        self.list.clear()
        for text in items:
            QListWidgetItem(text, self.list)
        if 0 <= current_index < self.list.count():
            self.list.setCurrentRow(current_index)

    def _select_from_click(self, item: QListWidgetItem) -> None:
        row = self.list.row(item)
        self.on_select(item.text(), row)
        self.close()

    def _wrap_keypress(self, original):
        def handler(event):
            key = event.key()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                item = self.list.currentItem()
                if item:
                    self._select_from_click(item)
                return
            if key == Qt.Key_Escape:
                self.close()
                return
            return original(event)
        return handler


# ── Combo that uses the overlay popup ─────────────────────────────────────────
class OverlayCombo(QComboBox):
    """QComboBox that replaces the native popup with a custom overlay frame."""

    def __init__(self, *, x_offset: int = 0, y_offset: int = 6, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._popup: Optional[ComboOverlayPopup] = None

    def _ensure_popup(self) -> ComboOverlayPopup:
        if self._popup is None:
            # Parent to the window so it overlays and doesn't affect layout
            root = self.window()
            self._popup = ComboOverlayPopup(root, self._on_popup_select)
        return self._popup

    def _on_popup_select(self, text: str, index: int) -> None:
        # Sync both display and signals
        self.setCurrentIndex(index)
        # Emit the same signals QComboBox normally would
        self.activated.emit(index)
        self.textActivated.emit(text)
        self.currentIndexChanged.emit(index)
        self.currentTextChanged.emit(text)

    def showPopup(self) -> None:  # type: ignore[override]
        # Build & populate popup
        popup = self._ensure_popup()
        items = [self.itemText(i) for i in range(self.count())]
        popup.set_items(items, self.currentIndex())

        # Size: match combo width; height based on visible rows
        w = max(self.width(), 240)
        row_h = self.fontMetrics().height() + 14  # padding in list item
        max_rows = min(6, max(3, self.count()))
        h = 8 + max_rows * (row_h + 2) + 8  # inner margins + row margins
        popup.resize(w, h)

        # Position: bottom-left of the combo, in global coords
        gpos = self.mapToGlobal(self.rect().bottomLeft())
        popup.move(gpos.x() + self._x_offset, gpos.y() + self._y_offset)

        popup.show()
        # Focus the list for immediate keyboard nav
        QTimer.singleShot(0, popup.list.setFocus)

    def hidePopup(self) -> None:  # type: ignore[override]
        if self._popup:
            self._popup.close()
(QComboBox):
    """QComboBox that replaces the native popup with a custom overlay frame."""

    def __init__(self, *, x_offset: int = 0, y_offset: int = 6, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._popup: Optional[ComboOverlayPopup] = None

    def _ensure_popup(self) -> ComboOverlayPopup:
        if self._popup is None:
            # Parent to the window so it overlays and doesn't affect layout
            root = self.window()
            self._popup = ComboOverlayPopup(root, self._on_popup_select)
        return self._popup

    def _on_popup_select(self, text: str, index: int) -> None:
        # Sync both display and signals
        self.setCurrentIndex(index)
        # Emit the same signals QComboBox normally would
        self.activated.emit(index)
        self.textActivated.emit(text)
        self.currentIndexChanged.emit(index)
        self.currentTextChanged.emit(text)

    def showPopup(self) -> None:  # type: ignore[override]
        # Build & populate popup
        popup = self._ensure_popup()
        items = [self.itemText(i) for i in range(self.count())]
        popup.set_items(items, self.currentIndex())

        # Size: match combo width; height based on visible rows
        w = max(self.width(), 240)
        row_h = self.fontMetrics().height() + 14  # padding in list item
        max_rows = min(6, max(3, self.count()))
        h = 8 + max_rows * (row_h + 2) + 8  # inner margins + row margins
        popup.resize(w, h)

        # Position: bottom-left of the combo, in global coords
        gpos = self.mapToGlobal(self.rect().bottomLeft())
        popup.move(gpos.x() + self._x_offset, gpos.y() + self._y_offset)

        popup.show()
        # Focus the list for immediate keyboard nav
        QTimer.singleShot(0, popup.list.setFocus)

    def hidePopup(self) -> None:  # type: ignore[override]
        if self._popup:
            self._popup.close()


# ── Helper --------------------------------------------------------------------

def make_combo(items: Iterable[str], *, editable: bool = False) -> QComboBox:
    cb = OverlayCombo()
    cb.addItems(list(items))
    cb.setEditable(editable)
    cb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    cb.setMinimumWidth(260)
    cb.setObjectName("ComboMaterial")
    return cb


# ── QSS for the base combobox (overlay popup styles live in the class) ───────
QSS = r"""
#ComboMaterial {
    background: #1f1f1f;
    color: #eaeaea;
    border: 1px solid #3a3a3a;
    border-radius: 10px;
    padding: 6px 28px 6px 12px;
}
#ComboMaterial:hover { border-color: #4a4a4a; }
#ComboMaterial:focus { border-color: #6aa9ff; outline: none; }
#ComboMaterial:disabled { color: #9a9a9a; background: #2a2a2a; border-color: #333; }
#ComboMaterial::drop-down {
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 28px; border-left: 1px solid #3a3a3a; border-top-right-radius: 10px; border-bottom-right-radius: 10px;
}
#ComboMaterial::down-arrow { width: 10px; height: 10px; margin-right: 8px; }
"""


class ComboStylesWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QComboBox – Custom Overlay Popup Demo")
        self.resize(640, 380)
        self.setFont(QFont("Segoe UI", 10))

        central = QWidget(self)
        self.setCentralWidget(central)
        grid = QGridLayout(central)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        box = QGroupBox("Material (left‑aligned overlay popup, rounded)")
        lay = QGridLayout(box)

        normal = make_combo(["Alfalfa", "Basil", "Chives", "Dill"], editable=False)

        lay.addWidget(QLabel("Normal"), 0, 0)
        lay.addWidget(normal)

        grid.addWidget(box, 0, 0)

        self.setStyleSheet(QSS)


def main() -> None:
    app = QApplication([])
    app.setStyle("Fusion")
    win = ComboStylesWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
