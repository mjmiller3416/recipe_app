# ── required imports ─────────────────────────────────────────────────────────
import sys

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen, QShortcut
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QLayout, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

# ────────────────────────────────────────────────────────────────────────────

PEN_LAYOUT_TOP  = QPen(QColor("#55a83c"), 2, Qt.SolidLine)     # neon green
PEN_LAYOUT_NEST = QPen(QColor("#438b9a"), 2, Qt.DashLine)      # sky blue
PEN_SPACER      = QPen(QColor("#954295"), 1, Qt.DotLine)       # magenta
PEN_WIDGET      = QPen(QColor("#a27741"), 2, Qt.DashDotLine)   # orange


class LayoutDebugger(QWidget):
    """
    Transparent overlay that draws layout rects, spacers, and leaf widgets.
    Shortcuts:
        Ctrl+D  toggle overlay visibility
        L       toggle layout layer
        W       toggle widget layer
        S       toggle spacer layer
    """
    def __init__(self, target: QWidget):
        super().__init__(target)
        self._root = target

        # visibility flags
        self.show_layouts  = True
        self.show_widgets  = True
        self.show_spacers  = True
        self.show_grid_cells = True
        self.focus_widget = None

        # overlay attributes
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.raise_()
        self.show()

        # install event filter on self and all descendants
        self.installEventFilter(self)
        for w in self._root.findChildren(QWidget):
            w.installEventFilter(self)

        # ── shortcuts ───────────────────────────────────────────────────────────
        self._add_shortcut("Ctrl+D", lambda: self.setVisible(not self.isVisible()))
        self._add_shortcut("L", self._toggle_layouts)
        self._add_shortcut("W", self._toggle_widgets)
        self._add_shortcut("S", self._toggle_spacers)
        self._add_shortcut("G", self._toggle_grid_cells)
        self._add_shortcut("Escape", self._clear_focus)

    def _add_shortcut(self, key: str, slot):
        sc = QShortcut(QKeySequence(key), self._root)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(slot)

    # flags toggled by shortcuts
    def _toggle_layouts(self):
        self.show_layouts = not self.show_layouts
        print(f"[Debug] layouts  → {self.show_layouts}")
        self.update()

    def _toggle_widgets(self):
        self.show_widgets = not self.show_widgets
        print(f"[Debug] widgets  → {self.show_widgets}")
        self.update()

    def _toggle_spacers(self):
        self.show_spacers = not self.show_spacers
        print(f"[Debug] spacers  → {self.show_spacers}")
        self.update()

    def _toggle_grid_cells(self):
        self.show_grid_cells = not self.show_grid_cells
        print(f"[Debug] grid‑cells → {self.show_grid_cells}")
        self.update()

    def _clear_focus(self):
        self.focus_widget = None
        print("[Debug] focus → cleared")
        self.update()

    # keep overlay synced
    def resizeEvent(self, _): self.setGeometry(self._root.rect())

    # helper to map coordinates
    def _map_rect(self, widget: QWidget, rect: QRect) -> QRect:
        gpos = widget.mapToGlobal(rect.topLeft())
        return QRect(self.mapFromGlobal(gpos), rect.size())
    
    # helper to filter events on the target widget
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.modifiers() & Qt.ControlModifier:
                self.focus_widget = obj
                print(f"[Debug] focus → {obj.__class__.__name__}")
                self.update()
                return True          # eat the event so the app doesn't also handle it
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    #  helper: return the first layout we should start walking from
    # ------------------------------------------------------------------
    def _top_layout(self) -> QLayout | None:
        """
        Returns the layout to start debugging from.

        • If the root widget already has a layout, use that.
        • If the root is a QScrollArea / QMdiArea / etc. that wraps a single
          content widget, look at .widget() and use its layout instead.
        """
        if self.focus_widget and self.focus_widget.layout():
            return self.focus_widget.layout()

        # A normal widget with its own layout
        if self._root.layout():                                 
            return self._root.layout()

        # e.g. QScrollArea, QMdiArea – they wrap a single viewport widget
        if hasattr(self._root, "widget") and callable(self._root.widget):
            content = self._root.widget()
            if content and content.layout():
                return content.layout()

        return None

    # paint!
    def paintEvent(self, _evt):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(Qt.NoBrush)

        # ── layouts / spacers / grid ─────────────────────────────────────
        if self.show_layouts or self.show_spacers or self.show_grid_cells:
            def walk(lay, top=False):
                if not isinstance(lay, QLayout):
                    return
                
                # skip anything under a hidden widget
                parent_w = lay.parentWidget() or self._root
                if parent_w is not self._root and not parent_w.isVisible():
                    return

                # 1️⃣ Layout rectangle
                if self.show_layouts:
                    r = self._map_rect(parent_w, lay.contentsRect())
                    p.setPen(PEN_LAYOUT_TOP if top else PEN_LAYOUT_NEST)
                    p.drawRect(r)

                # 2️⃣ Grid‑cell boxes
                if self.show_grid_cells and isinstance(lay, QGridLayout):
                    for row in range(lay.rowCount()):
                        for col in range(lay.columnCount()):
                            cell_r = lay.cellRect(row, col)
                            cell   = self._map_rect(parent_w, cell_r)
                            p.setPen(QPen(QColor("#00ffaa"), 1, Qt.DotLine))
                            p.drawRect(cell)

                # 3️⃣ Recurse into child items
                for i in range(lay.count()):
                    item = lay.itemAt(i)
                    if not item:
                        continue

                    # nested layouts
                    if (sub := item.layout()):
                        walk(sub)

                    # widgets that own their own layout
                    elif (w := item.widget()) is not None:
                        layout_attr = getattr(w, "layout", None)
                        if callable(layout_attr):
                            child_lay = layout_attr()
                        elif isinstance(layout_attr, QLayout):
                            child_lay = layout_attr
                        else:
                            child_lay = None

                        if isinstance(child_lay, QLayout):
                            walk(child_lay)

                    # spacer items
                    elif self.show_spacers and isinstance(item, QSpacerItem):
                        p.setPen(PEN_SPACER)
                        p.drawRect(self._map_rect(parent_w, item.geometry()))

            if (root_lay := self._top_layout()):
                walk(root_lay, top=True)

        # ── draw widgets (independent) ────────────────────────────────────────
        if self.show_widgets:
            p.setPen(PEN_WIDGET)
            for w in self._root.findChildren(QWidget):
                # figure out if this widget “has a layout”
                layout_attr = getattr(w, "layout", None)
                if callable(layout_attr):
                    has_layout = isinstance(layout_attr(), QLayout)
                else:
                    has_layout = isinstance(layout_attr, QLayout)

                # skip invisible or layout‑owning widgets
                if not w.isVisible() or has_layout:
                    continue

                ov = QRect(self.mapFromGlobal(w.mapToGlobal(QPoint(0, 0))), w.size())
                p.drawRect(ov)

        # ── focus widget (independent) ─────────────────────────────────
        if self.focus_widget:
            p.setPen(QPen(QColor("#00ff00"), 1, Qt.SolidLine))
            r = self._map_rect(self.focus_widget, self.focus_widget.rect())
            p.drawRect(r)

        p.end()

# ────────────────────────────────────────────────────────────────────────────
#  Demo window with nested layouts, spacers, widgets
# ────────────────────────────────────────────────────────────────────────────
class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Overlay Demo – Ctrl+D toggles")

        # top‑level vertical layout
        v_main = QVBoxLayout(self)
        v_main.setContentsMargins(10, 10, 10, 10)
        v_main.setSpacing(20)

        # --- row 1: simple HBox ------------------------------------------------
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Row 1 – Label A"))
        row1.addWidget(QPushButton("Button B"))
        row1.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row1.addWidget(QLabel("Label C"))
        v_main.addLayout(row1)

        # --- row 2: grid with spacers & nested vbox ---------------------------
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QPushButton("G(0,0)"), 0, 0)
        grid.addWidget(QLabel("G(0,1)"), 0, 1)
        grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 0, 2, 2, 1)

        # nested vbox inside the grid
        v_nested = QVBoxLayout()
        v_nested.addWidget(QLabel("Nested VBox ‑ Label"))
        v_nested.addWidget(QPushButton("Nested VBox ‑ Button"))
        grid.addLayout(v_nested, 1, 0, 1, 2)
        v_main.addLayout(grid)

        # --- row 3: full‑width widget (for variety) ---------------------------
        big_label = QLabel("Row 3 – Full‑width QLabel")
        big_label.setStyleSheet("background:#222;color:#fff;padding:8px;")
        v_main.addWidget(big_label)

        # overlay on top of everything
        self.overlay = LayoutDebugger(self)

        self.resize(800, 600)


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w   = DemoWindow()
    w.show()
    sys.exit(app.exec())
