"""app/ui/utils/layout_utils.py

Layout utilities for common UI patterns in the Recipe App.
Consolidates repeated layout setup, scroll areas, and widget positioning logic.

# ── Internal Index ──────────────────────────────────────────
#
# ── Scroll Area Setup ───────────────────────────────────────
# create_scroll_area()          -> Create standardized scroll area
# create_scroll_content_widget() -> Create scroll content with layout
# setup_main_scroll_layout()    -> Complete main scroll pattern
#
# ── Grid Layout Setup ───────────────────────────────────────
# create_form_grid_layout()     -> Standardized form grid layout
# set_fixed_height_for_layout_widgets() -> Set fixed height for widgets
#
# ── Advanced Layout Utils ───────────────────────────────────
# create_fixed_wrapper()        -> Wrap widgets with fixed width
# make_overlay()                -> Stack widgets with overlay positioning
#
# ── Position & Anchoring ────────────────────────────────────
# CornerAnchor                  -> Class for corner widget anchoring
# center_on_screen()            -> Center widget on screen

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Iterable, Union

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QLayout, QScrollArea, QVBoxLayout, QWidget)

__all__ = [
    # Scroll Area Setup
    'create_scroll_area', 'create_scroll_content_widget', 'setup_main_scroll_layout',

    # Grid Layout Setup
    'create_form_grid_layout', 'create_labeled_form_grid', 'set_fixed_height_for_layout_widgets',

    # Advanced Layout Utils
    'create_fixed_wrapper', 'make_overlay', 'create_two_column_layout', 'create_two_row_layout',

    # Position & Anchoring
    'CornerAnchor', 'center_on_screen',
]


# ── Scroll Area Setup ───────────────────────────────────────────────────────────────────────────────────────
def create_scroll_area(
    content_widget: QWidget = None,
    vertical_policy: Qt.ScrollBarPolicy = Qt.ScrollBarAsNeeded,
    horizontal_policy: Qt.ScrollBarPolicy = Qt.ScrollBarAsNeeded,
    frame_shape: QFrame.Shape = QFrame.NoFrame,
    widget_resizable: bool = True
) -> tuple[QScrollArea, QWidget]:
    """
    Create a standardized scroll area with content widget.

    Args:
        content_widget: Widget to place in scroll area (creates new if None)
        vertical_policy: Vertical scroll bar policy
        horizontal_policy: Horizontal scroll bar policy
        frame_shape: Frame shape for scroll area
        widget_resizable: Whether the widget should be resizable

    Returns:
        tuple[QScrollArea, QWidget]: (scroll_area, content_widget)

    Examples:
        scroll, content = create_scroll_area()
        scroll, content = create_scroll_area(my_widget, Qt.ScrollBarAlwaysOff)
    """
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(widget_resizable)
    scroll_area.setVerticalScrollBarPolicy(vertical_policy)
    scroll_area.setHorizontalScrollBarPolicy(horizontal_policy)
    scroll_area.setFrameShape(frame_shape)

    if content_widget is None:
        content_widget = QWidget()

    scroll_area.setWidget(content_widget)
    return scroll_area, content_widget

def create_scroll_content_widget(
    object_name: str = "ScrollContent",
    margins: tuple[int, int, int, int] = (140, 40, 140, 40),
    spacing: int = 30,
    layout_type: str = "vertical"
) -> tuple[QWidget, QLayout]:
    """
    Create a standardized scroll content widget with layout.

    Args:
        object_name: Object name for the content widget
        margins: Layout margins (left, top, right, bottom)
        spacing: Layout spacing
        layout_type: "vertical" or "horizontal"

    Returns:
        tuple[QWidget, QLayout]: (content_widget, layout)

    Examples:
        content, layout = create_scroll_content_widget("MyContent", (20, 20, 20, 20))
        content, layout = create_scroll_content_widget(layout_type="horizontal")
    """
    content_widget = QWidget()
    content_widget.setObjectName(object_name)

    if layout_type == "horizontal":
        layout = QHBoxLayout(content_widget)
    else:
        layout = QVBoxLayout(content_widget)

    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)

    return content_widget, layout

def setup_main_scroll_layout(
    parent_widget: QWidget,
    content_object_name: str = "ScrollContent",
    margins: tuple[int, int, int, int] = (140, 40, 140, 40),
    spacing: int = 30
) -> tuple[QVBoxLayout, QScrollArea, QWidget, QVBoxLayout]:
    """
    Set up complete main scroll layout pattern used across views.

    Args:
        parent_widget: Parent widget to add layout to
        content_object_name: Object name for scroll content
        margins: Content margins (left, top, right, bottom)
        spacing: Content spacing

    Returns:
        tuple: (main_layout, scroll_area, scroll_content, scroll_layout)

    Examples:
        main, scroll, content, layout = setup_main_scroll_layout(self)
        main, scroll, content, layout = setup_main_scroll_layout(
            self, "AddRecipeContent", (100, 20, 100, 20)
        )
    """
    # Main vertical layout for the entire widget
    main_layout = QVBoxLayout(parent_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # Create scroll area
    scroll_area, scroll_content = create_scroll_area()

    # Setup scroll content with layout
    scroll_content.setObjectName(content_object_name)
    scroll_layout = QVBoxLayout(scroll_content)
    scroll_layout.setSpacing(spacing)
    scroll_layout.setContentsMargins(*margins)

    main_layout.addWidget(scroll_area)

    return main_layout, scroll_area, scroll_content, scroll_layout


# ── Grid Layout Setup ───────────────────────────────────────────────────────────────────────────────────────
def create_form_grid_layout(
    parent_widget: QWidget,
    margins: tuple[int, int, int, int] = (10, 10, 10, 10),
    spacing: int = 10
) -> QGridLayout:
    """
    Create a standardized grid layout for forms.

    Args:
        parent_widget: Parent widget for the layout
        margins: Layout margins (left, top, right, bottom)
        spacing: Layout spacing

    Returns:
        QGridLayout: Configured grid layout for forms

    Examples:
        layout = create_form_grid_layout(self)
        layout = create_form_grid_layout(form_widget, (20, 15, 20, 15), 12)
    """
    layout = QGridLayout(parent_widget)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout

def create_labeled_form_grid(
    parent_widget: QWidget,
    field_configs: dict,
    fixed_height: int = 60,
    margins: tuple[int, int, int, int] = (10, 10, 10, 10),
    spacing: int = 10
) -> tuple:
    """
    Create a complete form grid with labels and widgets using field configuration.

    Args:
        parent_widget: Parent widget for the layout
        field_configs: Dict mapping field names to config dicts with keys:
            - widget_type: "line_edit", "combo_box", "text_edit"
            - label: Label text
            - placeholder: Placeholder text (optional)
            - object_name: Object name for widget (optional)
            - context: Context property for styling (optional)
            - list_items: Items for combo box (if widget_type is combo_box)
            - row: Grid row position
            - col: Grid column position
            - row_span: Row span (default 1)
            - col_span: Column span (default 1)
        fixed_height: Fixed height for input widgets
        margins: Layout margins
        spacing: Layout spacing

    Returns:
        tuple: (grid_layout, widgets_dict, labels_dict)

    Examples:
        field_config = {
            "recipe_name": {
                "widget_type": "line_edit",
                "label": "Recipe Name",
                "placeholder": "e.g. Spaghetti Carbonara",
                "object_name": "RecipeNameLineEdit",
                "row": 0, "col": 0, "col_span": 2
            },
            "meal_type": {
                "widget_type": "combo_box",
                "label": "Meal Type",
                "placeholder": "Select meal type",
                "list_items": ["Breakfast", "Lunch", "Dinner"],
                "context": "recipe_form",
                "row": 2, "col": 0
            }
        }
        layout, widgets, labels = create_labeled_form_grid(self, field_config)
    """
    from PySide6.QtWidgets import QLineEdit, QTextEdit

    from app.ui.components.widgets import ComboBox

    # Create base grid layout
    layout = create_form_grid_layout(parent_widget, margins, spacing)

    widgets = {}
    labels = {}

    for field_name, config in field_configs.items():
        # Extract configuration
        widget_type = config.get("widget_type", "line_edit")
        label_text = config.get("label", field_name.replace("_", " ").title())
        placeholder = config.get("placeholder", "")
        object_name = config.get("object_name", f"{field_name.title().replace('_', '')}Widget")
        context = config.get("context")
        row = config.get("row", 0)
        col = config.get("col", 0)
        row_span = config.get("row_span", 1)
        col_span = config.get("col_span", 1)

        # Create label
        label = QLabel(label_text, parent_widget)
        labels[field_name] = label

        # Create widget based on type
        if widget_type == "line_edit":
            widget = QLineEdit(parent_widget)
            if placeholder:
                widget.setPlaceholderText(placeholder)
        elif widget_type == "combo_box":
            list_items = config.get("list_items", [])
            widget = ComboBox(list_items=list_items, placeholder=placeholder, parent=parent_widget)
            if context:
                widget.setProperty("context", context)
        elif widget_type == "text_edit":
            widget = QTextEdit(parent_widget)
            if placeholder:
                widget.setPlaceholderText(placeholder)
        else:
            raise ValueError(f"Unknown widget_type: {widget_type}")

        widget.setObjectName(object_name)
        widgets[field_name] = widget

        # Add to grid layout - label above widget
        layout.addWidget(label, row, col, 1, col_span)
        layout.addWidget(widget, row + 1, col, row_span, col_span)

    # Apply fixed height to input widgets (skip labels)
    set_fixed_height_for_layout_widgets(layout, fixed_height, skip=(QLabel,))

    return layout, widgets, labels

def set_fixed_height_for_layout_widgets(
    layout: QLayout,
    height: int,
    skip: tuple[type[QWidget], ...] = (QLabel,)
) -> None:
    """
    Set a fixed height for all widgets in a layout, skipping specified widget types.

    Args:
        layout: The layout containing widgets
        height: The fixed height to apply
        skip: Widget classes to skip (default: QLabel)

    Examples:
        set_fixed_height_for_layout_widgets(form_layout, 60)
        set_fixed_height_for_layout_widgets(layout, 40, (QLabel, QPushButton))
    """
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()

        if widget is None or isinstance(widget, skip):
            continue

        widget.setFixedHeight(height)


# ── Advanced Layout Utils ───────────────────────────────────────────────────────────────────────────────────
def create_fixed_wrapper(
    widgets: Union[QWidget, Iterable[QWidget]],
    fixed_width: int,
    alignment: Qt.Alignment = Qt.AlignCenter,
    direction: str = "horizontal",
    margins: tuple[int, int, int, int] = (0, 0, 0, 0)
) -> QWidget:
    """
    Wrap one or more widgets inside a QWidget with fixed width and layout.

    Args:
        widgets: Widget(s) to wrap (single widget or iterable)
        fixed_width: Fixed width for the wrapper
        alignment: Alignment for each widget inside the layout
        direction: 'horizontal' or 'vertical'
        margins: Margins for the layout (left, top, right, bottom)

    Returns:
        QWidget: Wrapper widget with layout and given contents

    Examples:
        wrapper = create_fixed_wrapper(button, 200)
        wrapper = create_fixed_wrapper([btn1, btn2], 300, Qt.AlignLeft, "vertical")
    """
    wrapper = QWidget()
    wrapper.setObjectName("FixedWrapper")
    wrapper.setFixedWidth(fixed_width)

    LayoutClass = QVBoxLayout if direction == "vertical" else QHBoxLayout
    layout = LayoutClass(wrapper)
    layout.setContentsMargins(*margins)

    # apply layout-wide alignment only if horizontal
    if direction == "horizontal":
        layout.setAlignment(alignment)

    # add each widget with its own alignment
    if isinstance(widgets, QWidget):
        layout.addWidget(widgets, alignment=alignment)
    else:
        for w in widgets:
            layout.addWidget(w, alignment=alignment)

    return wrapper

def make_overlay(
    base_widget: QWidget,
    overlay_widget: QWidget,
    margins: tuple[int, int, int, int] = (0, 8, 8, 0),
    align: Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignRight
) -> QWidget:
    """
    Stack overlay_widget on top of base_widget at the given alignment.

    Args:
        base_widget: The base widget to overlay on
        overlay_widget: The widget to overlay on top of the base
        margins: Padding around the overlay (left, top, right, bottom)
        align: Alignment for the overlay widget

    Returns:
        QWidget: Container with overlaid widgets

    Examples:
        container = make_overlay(main_content, floating_button)
        container = make_overlay(image, badge, (5, 5, 5, 5), Qt.AlignBottom | Qt.AlignLeft)
    """
    container = QWidget()
    grid = QGridLayout(container)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(0)

    # put the base in cell (0,0)
    grid.addWidget(base_widget, 0, 0)

    # wrap the overlay in its own widget to get padding
    pad = QWidget()
    pad.setObjectName("OverlayPadding")
    pad.setAttribute(Qt.WA_TranslucentBackground)
    vlyt = QVBoxLayout(pad)
    vlyt.setContentsMargins(*margins)
    vlyt.setSpacing(0)
    vlyt.addWidget(overlay_widget)

    # stack that padded overlay over the base
    grid.addWidget(pad, 0, 0, alignment=align)

    return container

def create_two_row_layout(
    top_widgets: list[QWidget] = None,
    bottom_widgets: list[QWidget] = None,
    top_weight: int = 1,
    bottom_weight: int = 1,
    spacing: int = 30,
    margins: tuple[int, int, int, int] = (0, 0, 0, 0),
    alignment: Qt.AlignmentFlag = Qt.AlignLeft
) -> QVBoxLayout:
    """
    Create a standardized two-row layout with configurable weights and content.

    Args:
        top_widgets: List of widgets for the top row (creates empty row if None)
        bottom_widgets: List of widgets for the bottom row (creates empty row if None)
        top_weight: Stretch factor for top row (default: 1)
        bottom_weight: Stretch factor for bottom row (default: 1)
        spacing: Vertical spacing between rows (default: 30)
        margins: Layout margins (left, top, right, bottom)
        alignment: Horizontal alignment for row widgets (default: Qt.AlignLeft)

    Returns:
        QVBoxLayout: Configured two-row layout with widgets added

    Examples:
        # Equal height rows
        layout = create_two_row_layout([widget1], [widget2, widget3])

        # Top 1/3, Bottom 2/3 height
        layout = create_two_row_layout([top_widget], [bottom1, bottom2], 1, 2)

        # Custom spacing and alignment
        layout = create_two_row_layout(
            [header_card], [content_card, footer_card],
            spacing=40, alignment=Qt.AlignCenter
        )
    """
    # Create main vertical layout
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(*margins)
    main_layout.setSpacing(spacing)

    # Create top row widget
    top_row = QWidget()
    top_layout = QHBoxLayout(top_row)
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(20)  # Horizontal spacing within row

    # Add widgets to top row
    if top_widgets:
        for widget in top_widgets:
            top_layout.addWidget(widget)
    else:
        # Add stretch if no widgets to prevent row collapse
        top_layout.addStretch()

    # Create bottom row widget
    bottom_row = QWidget()
    bottom_layout = QHBoxLayout(bottom_row)
    bottom_layout.setContentsMargins(0, 0, 0, 0)
    bottom_layout.setSpacing(20)  # Horizontal spacing within row

    # Add widgets to bottom row
    if bottom_widgets:
        for widget in bottom_widgets:
            bottom_layout.addWidget(widget)
    else:
        # Add stretch if no widgets to prevent row collapse
        bottom_layout.addStretch()

    # Add rows to main layout with weights and alignment
    main_layout.addWidget(top_row, top_weight, alignment)
    main_layout.addWidget(bottom_row, bottom_weight, alignment)

    return main_layout

def create_two_column_layout(
    left_widgets: list[QWidget] = None,
    right_widgets: list[QWidget] = None,
    left_weight: int = 1,
    right_weight: int = 1,
    spacing: int = 30,
    margins: tuple[int, int, int, int] = (0, 0, 0, 0),
    alignment: Qt.AlignmentFlag = Qt.AlignTop,
    match_heights: bool = False
) -> QHBoxLayout:
    """
    Create a unified two-column layout with automatic Card elevation preservation.

    This function intelligently handles both Card widgets (preserving shadow effects) and
    regular widgets. When Card widgets are detected, they are added directly to avoid
    shadow clipping. Regular widgets use container columns for better control.

    Args:
        left_widgets: List of widgets for the left column (creates empty column if None)
        right_widgets: List of widgets for the right column (creates empty column if None)
        left_weight: Stretch factor for left column (default: 1)
        right_weight: Stretch factor for right column (default: 1)
        spacing: Horizontal spacing between columns (default: 30)
        margins: Layout margins (left, top, right, bottom)
        alignment: Vertical alignment for column widgets (default: Qt.AlignTop)
        match_heights: Whether cards should match each other's height (default: True)

    Returns:
        QHBoxLayout: Configured two-column layout with widgets added

    Examples:
        # Single Card per column (optimal - direct addition)
        layout = create_unified_two_column_layout([card1], [card2])

        # Multiple Cards per column (preserves shadows)
        layout = create_unified_two_column_layout([card1, card2], [card3, card4])

        # Mixed Cards and regular widgets
        layout = create_unified_two_column_layout([card1], [widget1, widget2])

        # Regular widgets only
        layout = create_unified_two_column_layout([widget1], [widget2, widget3])

        # Custom proportions (left 1/3, right 2/3)
        layout = create_unified_two_column_layout([card1], [card2], 1, 2)
    """
    from app.ui.components.layout.card import BaseCard

    # Create main horizontal layout
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(*margins)
    main_layout.setSpacing(spacing)

    # Check if we have any Card widgets that need special handling
    left_has_cards = left_widgets and any(isinstance(w, BaseCard) for w in left_widgets)
    right_has_cards = right_widgets and any(isinstance(w, BaseCard) for w in right_widgets)

    # Optimal case: both sides have exactly one Card widget
    if (left_widgets and len(left_widgets) == 1 and isinstance(left_widgets[0], BaseCard) and
        right_widgets and len(right_widgets) == 1 and isinstance(right_widgets[0], BaseCard)):

        left_card = left_widgets[0]
        right_card = right_widgets[0]

        # Configure card expansion based on weights
        if left_weight > 0:
            left_card.expandWidth(True)
        if right_weight > 0:
            right_card.expandWidth(True)

        if match_heights:
            left_card.expandHeight(True)
            right_card.expandHeight(True)

        main_layout.addWidget(left_card, left_weight, alignment)
        main_layout.addWidget(right_card, right_weight, alignment)

        return main_layout

    # Handle complex cases with mixed widgets or multiple widgets per column
    _add_column_widgets(main_layout, left_widgets, left_weight, alignment, left_has_cards, match_heights)
    _add_column_widgets(main_layout, right_widgets, right_weight, alignment, right_has_cards, match_heights)

    return main_layout

def _add_column_widgets(
    main_layout: QHBoxLayout,
    widgets: list[QWidget],
    weight: int,
    alignment: Qt.AlignmentFlag,
    has_cards: bool,
    match_heights: bool
):
    """
    Helper function to add widgets to a column, handling Cards appropriately.

    Args:
        main_layout: The main horizontal layout to add to
        widgets: List of widgets for this column
        weight: Stretch factor for this column
        alignment: Vertical alignment for widgets
        has_cards: Whether this column contains Card widgets
        match_heights: Whether cards should expand to match heights
    """
    from app.ui.components.layout.card import BaseCard

    if not widgets:
        # Add stretch for empty column
        main_layout.addStretch(weight)
        return

    if len(widgets) == 1:
        widget = widgets[0]

        # Single Card widget - add directly (preserves shadows)
        if isinstance(widget, BaseCard):
            if weight > 0:
                widget.expandWidth(True)
            if match_heights:
                widget.expandHeight(True)
            main_layout.addWidget(widget, weight, alignment)
        else:
            # Single regular widget - add directly
            main_layout.addWidget(widget, weight, alignment)
    else:
        # Multiple widgets - need a layout container
        if has_cards:
            # Cards present - use minimal VBoxLayout (no wrapper widget to avoid shadow clipping)
            column_layout = QVBoxLayout()
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(20)

            for widget in widgets:
                if isinstance(widget, BaseCard):
                    if weight > 0:
                        widget.expandWidth(True)
                    if match_heights:
                        widget.expandHeight(True)
                column_layout.addWidget(widget)

            main_layout.addLayout(column_layout, weight)
        else:
            # Only regular widgets - use container widget for better control
            column = QWidget()
            column_layout = QVBoxLayout(column)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(20)

            for widget in widgets:
                column_layout.addWidget(widget)

            main_layout.addWidget(column, weight, alignment)


# ── Position & Anchoring ────────────────────────────────────────────────────────────────────────────────────
class CornerAnchor(QObject):
    """Utility class for anchoring widgets to corners of other widgets."""

    def __init__(self, anchor_widget, target_widget,
                 corner="bottom-left", x_offset=0, y_offset=0):
        """
        Initialize corner anchor positioning.

        Args:
            anchor_widget: Widget to anchor to
            target_widget: Widget to position
            corner: Corner position ("top-left", "top-right", "bottom-left", "bottom-right")
            x_offset: Horizontal offset from corner
            y_offset: Vertical offset from corner

        Examples:
            anchor = CornerAnchor(button, tooltip, "top-right", -5, -5)
            anchor = CornerAnchor(image, badge, "bottom-right")
        """
        super().__init__()
        self.anchor = anchor_widget
        self.target = target_widget
        self.corner = corner
        self.x_offset = x_offset
        self.y_offset = y_offset

        # watch for resize events on anchor's parent
        self.anchor.parent().installEventFilter(self)

        # delay the initial position update until layout is applied
        QTimer.singleShot(0, self.update_position)

        # make sure the target floats above
        self.target.raise_()

    def update_position(self):
        """Update the position of the target widget based on anchor position."""
        anchor_pos = self.anchor.mapToParent(self.anchor.rect().topLeft())
        anchor_size = self.anchor.size()
        target_size = self.target.size()

        match self.corner:
            case "top-left":
                x = anchor_pos.x()
                y = anchor_pos.y()
            case "top-right":
                x = anchor_pos.x() + anchor_size.width() - target_size.width()
                y = anchor_pos.y()
            case "bottom-left":
                x = anchor_pos.x()
                y = anchor_pos.y() + anchor_size.height() - target_size.height()
            case "bottom-right":
                x = anchor_pos.x() + anchor_size.width() - target_size.width()
                y = anchor_pos.y() + anchor_size.height() - target_size.height()
            case _:
                raise ValueError(f"Unsupported corner: {self.corner}")

        self.target.move(x + self.x_offset, y + self.y_offset)

    def eventFilter(self, obj, event):
        """Handle resize events to update position."""
        if obj == self.anchor.parent() and event.type() == QEvent.Resize:
            QTimer.singleShot(0, self.update_position)
        return super().eventFilter(obj, event)

def center_on_screen(widget: QWidget):
    """
    Center the widget on the screen.

    Args:
        widget: Widget to center on screen

    Examples:
        center_on_screen(dialog)
        center_on_screen(main_window)
    """
    screen = QGuiApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = widget.frameGeometry()

    # calculate center position
    center_x = (screen_geometry.width() - window_geometry.width()) // 2
    center_y = (screen_geometry.height() - window_geometry.height()) // 2

    # move widget to center
    widget.move(center_x, center_y)
