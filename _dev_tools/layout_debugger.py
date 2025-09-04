"""layout_debugger.py

A drop‑in, toggleable overlay for **visualizing PySide6 layouts** at runtime.

It paints borders for:
- Top-level target widget
- Every child QWidget
- Each active QLayout (with contentsMargins visualized)
- Each QLayoutItem (items inside layouts)

Extras:
- Hover highlight (shows the widget under the cursor)
- Logs labels of hovered region via DebugLogger instead of painting
- Optional pixel grid overlay
- Screenshot capture of the target
- Global shortcuts attached to the target window

Default shortcuts (scoped to the target window):
- Ctrl+Alt+D → Toggle overlay on/off
- Ctrl+Alt+M → Toggle margins
- Ctrl+Alt+G → Toggle pixel grid
- Ctrl+Alt+H → Toggle hover highlight
- Ctrl+Alt+S → Save PNG screenshot of the target window

Usage (minimal):
    from layout_debugger import LayoutDebugger
    LayoutDebugger.install(main_window)  # adds shortcuts; overlay hidden by default
    # or programmatically toggle:
    LayoutDebugger.toggle(main_window)

Place this file anywhere importable (e.g., app/ui/debug/layout_debugger.py) and
import as needed.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass
import sys
import time
from typing import Callable, List, Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QKeySequence, QShortcut

# Import DebugLogger if available, otherwise fallback to print
try:
    from _dev_tools.debug_logger import DebugLogger  # adjust path as needed
    log = DebugLogger("LayoutDebugger")
except Exception:
    class _FallbackLogger:
        def info(self, msg: str):
            print(msg)
    log = _FallbackLogger()

Qt = QtCore.Qt
QRect = QtCore.QRect
QPoint = QtCore.QPoint
QMargins = QtCore.QMargins


@dataclass
class Region:
    rect: QRect
    kind: str
    label: str
    color: QtGui.QColor
    dash: bool = False
    thickness: int = 1
    alpha: int = 230
    fill_alpha: Optional[int] = None


def _safe_same_window(a: QtWidgets.QWidget, b: QtWidgets.QWidget) -> bool:
    try:
        return a.window() is b.window()
    except Exception:
        return False


def _map_rect_to_overlay(src_widget: QtWidgets.QWidget, overlay: QtWidgets.QWidget, rect: QRect) -> Optional[QRect]:
    if rect.isNull() or rect.isEmpty():
        return None
    try:
        tl_global = src_widget.mapToGlobal(rect.topLeft())
        tl_overlay = overlay.mapFromGlobal(tl_global)
        return QRect(tl_overlay, rect.size())
    except Exception:
        return None


def _widget_label(w: QtWidgets.QWidget) -> str:
    name = w.objectName() or "<no-name>"
    return f"{w.__class__.__name__} | {name} | {w.width()}x{w.height()}"


def _layout_label(l: QtWidgets.QLayout) -> str:
    m: QMargins = l.contentsMargins()
    return (
        f"{l.__class__.__name__} | geom {l.geometry().width()}x{l.geometry().height()} "
        f"| margins L{m.left()} T{m.top()} R{m.right()} B{m.bottom()}"
    )


def _margins_label(m: QMargins) -> str:
    return f"margins L{m.left()} T{m.top()} R{m.right()} B{m.bottom()}"


class _LayoutDebugOverlay(QtWidgets.QWidget):
    SHOW_MARGINS: bool = True
    SHOW_HOVER: bool = True
    SHOW_GRID: bool = False
    GRID_STEP: int = 8

    COLOR_WIDGET = QtGui.QColor(80, 200, 120)
    COLOR_LAYOUT = QtGui.QColor(180, 80, 200)
    COLOR_ITEM = QtGui.QColor(70, 130, 200)
    COLOR_MARGIN = QtGui.QColor(240, 180, 60)
    COLOR_HOVER = QtGui.QColor(255, 70, 70)

    def __init__(self, target: QtWidgets.QWidget):
        super().__init__(parent=target)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setGeometry(target.rect())
        self._target = target
        self._regions: List[Region] = []
        self._rebuild_scheduled = False
        self._last_hovered: Optional[str] = None
        self._install_event_filters()
        self._schedule_rebuild()
        self.raise_()
        self.show()

    def _install_event_filters(self) -> None:
        self._target.installEventFilter(self)
        for w in self._target.findChildren(QtWidgets.QWidget):
            if w is self:
                continue
            w.installEventFilter(self)

    def _remove_event_filters(self) -> None:
        try:
            self._target.removeEventFilter(self)
        except Exception:
            pass
        for w in self._target.findChildren(QtWidgets.QWidget):
            try:
                w.removeEventFilter(self)
            except Exception:
                pass

    def eventFilter(self, obj: QtCore.QObject, ev: QtCore.QEvent) -> bool:
        et = ev.type()
        relevant = {
            QtCore.QEvent.Type.Resize,
            QtCore.QEvent.Type.Move,
            QtCore.QEvent.Type.Show,
            QtCore.QEvent.Type.Hide,
            QtCore.QEvent.Type.ChildAdded,
            QtCore.QEvent.Type.ChildRemoved,
            QtCore.QEvent.Type.LayoutRequest,
            QtCore.QEvent.Type.ZOrderChange,
            QtCore.QEvent.Type.MouseMove,
        }
        if et in relevant:
            if obj is self._target and et in (QtCore.QEvent.Type.Resize, QtCore.QEvent.Type.Show):
                self.setGeometry(self._target.rect())
            if et == QtCore.QEvent.Type.MouseMove:
                self._handle_hover()
            else:
                self._schedule_rebuild()
        return False

    def _schedule_rebuild(self) -> None:
        if self._rebuild_scheduled:
            return
        self._rebuild_scheduled = True
        QtCore.QTimer.singleShot(0, self._rebuild_now)

    def _rebuild_now(self) -> None:
        self._rebuild_scheduled = False
        self._rebuild_regions()
        self.update()

    def _rebuild_regions(self) -> None:
        self._regions.clear()
        overlay = self
        root = self._target
        self._regions.append(
            Region(
                rect=QRect(QPoint(0, 0), root.size()),
                kind="widget",
                label=_widget_label(root),
                color=self.COLOR_WIDGET,
                dash=False,
                thickness=2,
            )
        )
        for w in root.findChildren(QtWidgets.QWidget):
            if w is self or not w.isVisible() or not w.parentWidget():
                continue
            if not _safe_same_window(w, overlay):
                continue
            wrect = _map_rect_to_overlay(w, overlay, w.rect())
            if wrect is not None:
                self._regions.append(
                    Region(rect=wrect, kind="widget", label=_widget_label(w), color=self.COLOR_WIDGET, alpha=180)
                )
            lay = w.layout()
            if lay is not None:
                self._append_layout_regions(lay, w)
        if root.layout() is not None:
            self._append_layout_regions(root.layout(), root)

    def _append_layout_regions(self, layout: QtWidgets.QLayout, owner: QtWidgets.QWidget) -> None:
        overlay = self
        lay_geom = layout.geometry()
        if lay_geom.isValid():
            lay_rect = _map_rect_to_overlay(owner, overlay, lay_geom)
            if lay_rect is not None:
                self._regions.append(
                    Region(rect=lay_rect, kind="layout", label=_layout_label(layout), color=self.COLOR_LAYOUT, dash=True)
                )
                if self.SHOW_MARGINS:
                    m: QMargins = layout.contentsMargins()
                    inner = QRect(lay_rect)
                    inner.adjust(m.left(), m.top(), -m.right(), -m.bottom())
                    if inner.isValid():
                        self._regions.append(
                            Region(rect=inner, kind="margins", label=_margins_label(m), color=self.COLOR_MARGIN, dash=True)
                        )
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            try:
                item_rect_owner = item.geometry()
            except Exception:
                continue
            if item_rect_owner.isValid():
                item_rect = _map_rect_to_overlay(owner, overlay, item_rect_owner)
                if item_rect is not None:
                    self._regions.append(
                        Region(rect=item_rect, kind="layout_item", label=f"item {i}", color=self.COLOR_ITEM, dash=True)
                    )

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.SHOW_GRID:
            self._paint_grid(p)
        if self.SHOW_HOVER:
            hover_rect = self._current_hover_rect()
            if hover_rect is not None:
                pen = QtGui.QPen(self.COLOR_HOVER)
                pen.setWidth(2)
                p.setPen(pen)
                p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
                p.drawRect(hover_rect.adjusted(0, 0, -1, -1))
        for r in self._regions:
            pen = QtGui.QPen(r.color)
            pen.setWidth(r.thickness)
            if r.dash:
                pen.setStyle(Qt.PenStyle.DashLine)
            col = QtGui.QColor(r.color)
            col.setAlpha(r.alpha)
            pen.setColor(col)
            p.setPen(pen)
            p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            p.drawRect(r.rect.adjusted(0, 0, -1, -1))
        p.end()

    def _paint_grid(self, p: QtGui.QPainter) -> None:
        step = max(2, int(self.GRID_STEP))
        size = self.size()
        grid_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 40))
        p.setPen(grid_pen)
        x = 0
        while x <= size.width():
            p.drawLine(x, 0, x, size.height())
            x += step
        y = 0
        while y <= size.height():
            p.drawLine(0, y, size.width(), y)
            y += step

    def _current_hover_rect(self) -> Optional[QRect]:
        try:
            gp = QtGui.QCursor.pos()
            root = self._target
            local = root.mapFromGlobal(gp)
            w = root.childAt(local)
            if w is None or w is self:
                return None
            rect = _map_rect_to_overlay(w, self, w.rect())
            return rect
        except Exception:
            return None

    def _handle_hover(self):
        gp = QtGui.QCursor.pos()
        root = self._target
        local = root.mapFromGlobal(gp)
        w = root.childAt(local)
        if w is None or w is self:
            return
        label = _widget_label(w)
        if label != self._last_hovered:
            log.info(f"Hover: {label}")
            self._last_hovered = label

    def toggle_margins(self):
        self.SHOW_MARGINS = not self.SHOW_MARGINS
        self._schedule_rebuild()

    def toggle_hover(self):
        self.SHOW_HOVER = not self.SHOW_HOVER
        self.update()

    def toggle_grid(self):
        self.SHOW_GRID = not self.SHOW_GRID
        self.update()

    def save_screenshot(self) -> str:
        pixmap = self._target.grab()
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = f"layout_debug_{ts}.png"
        pixmap.save(path)
        return path

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self._remove_event_filters()
        super().closeEvent(e)


class LayoutDebugger(QtCore.QObject):
    _PROP_KEY = "__layout_debugger_controller__"

    def __init__(self, target: QtWidgets.QWidget):
        super().__init__(parent=target)
        self._target = target
        self._overlay: Optional[_LayoutDebugOverlay] = None
        self._shortcuts: list[QShortcut] = []
        self._install_shortcuts()

    @classmethod
    def install(cls, target: QtWidgets.QWidget) -> "LayoutDebugger":
        existing: Optional[LayoutDebugger] = target.property(cls._PROP_KEY)
        if isinstance(existing, LayoutDebugger):
            return existing
        ctrl = LayoutDebugger(target)
        target.setProperty(cls._PROP_KEY, ctrl)
        return ctrl

    @classmethod
    def controller_for(cls, target: QtWidgets.QWidget) -> Optional["LayoutDebugger"]:
        obj = target.property(cls._PROP_KEY)
        return obj if isinstance(obj, LayoutDebugger) else None

    @classmethod
    def toggle(cls, target: QtWidgets.QWidget) -> None:
        ctrl = cls.install(target)
        ctrl.set_visible(not ctrl.is_visible())

    def is_visible(self) -> bool:
        return self._overlay is not None and self._overlay.isVisible()

    def set_visible(self, visible: bool) -> None:
        if visible:
            if self._overlay is None:
                self._overlay = _LayoutDebugOverlay(self._target)
            else:
                self._overlay.show()
                self._overlay.raise_()
                self._overlay._schedule_rebuild()
        else:
            if self._overlay is not None:
                self._overlay.hide()

    def destroy(self) -> None:
        if self._overlay is not None:
            self._overlay.deleteLater()
            self._overlay = None
        for sc in self._shortcuts:
            sc.setParent(None)
        self._shortcuts.clear()
        self._target.setProperty(self._PROP_KEY, None)

    def _shortcut(self, key_seq: str, slot: Callable[[], None]) -> None:
        sc = QShortcut(QKeySequence(key_seq), self._target)
        sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        sc.activated.connect(slot)
        self._shortcuts.append(sc)

    def _install_shortcuts(self) -> None:
        self._shortcut("Ctrl+Alt+D", lambda: self.set_visible(not self.is_visible()))
        self._shortcut("Ctrl+Alt+M", lambda: self._overlay and self._overlay.toggle_margins())
        self._shortcut("Ctrl+Alt+G", lambda: self._overlay and self._overlay.toggle_grid())
        self._shortcut("Ctrl+Alt+H", lambda: self._overlay and self._overlay.toggle_hover())
        self._shortcut("Ctrl+Alt+S", self._save_png)

    def _save_png(self) -> None:
        if not self._overlay:
            return
        path = self._overlay.save_screenshot()
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), f"Saved {path}")

# ──────────────────────────────────────────────────────────────────────────────
# Demo (can be removed in production)
# ──────────────────────────────────────────────────────────────────────────────

class _DemoWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Debugger Demo")
        self.resize(880, 560)

        root = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(root)
        v.setContentsMargins(16, 24, 16, 16)
        v.setSpacing(12)

        # Top row
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(10)
        for i in range(3):
            btn = QtWidgets.QPushButton(f"Button {i+1}")
            row.addWidget(btn)
        v.addLayout(row)

        # Middle grid
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(20, 8, 20, 8)
        grid.setSpacing(8)
        for r in range(3):
            for c in range(4):
                lbl = QtWidgets.QLabel(f"r{r} c{c}")
                lbl.setMinimumSize(180, 60)
                lbl.setFrameShape(QtWidgets.QFrame.Shape.Box)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(lbl, r, c)
        v.addLayout(grid)

        # Bottom group
        group = QtWidgets.QGroupBox("Group")
        gl = QtWidgets.QVBoxLayout(group)
        gl.setContentsMargins(18, 14, 18, 14)
        gl.setSpacing(6)
        gl.addWidget(QtWidgets.QLineEdit("Type here"))
        gl.addWidget(QtWidgets.QSlider(Qt.Orientation.Horizontal))
        v.addWidget(group)

        self.setCentralWidget(root)

        # Attach debugger shortcuts
        LayoutDebugger.install(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = _DemoWindow()
    w.show()
    sys.exit(app.exec())
