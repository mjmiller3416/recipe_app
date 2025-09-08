"""app/ui/utils/event_utils.py

Event handling utilities for signals, slots, and UI state management.
Consolidates common event patterns used across Recipe App views.

# ── Internal Index ──────────────────────────────────────────
#
# ── Signal Connection Patterns ──────────────────────────────
# connect_form_signals()       -> Connect form widget signals
# connect_button_actions()     -> Connect button click handlers
# batch_connect_signals()      -> Connect multiple signals at once
#
# ── Event Filtering & Handling ──────────────────────────────
# create_tooltip_event_filter() -> Event filter for tooltip handling
# create_focus_event_filter()  -> Event filter for focus events
# install_event_handlers()     -> Install multiple event handlers
#
# ── State Management ────────────────────────────────────────
# create_toggle_handler()      -> Create state toggle handler
# setup_conditional_visibility() -> Set up show/hide based on state
# manage_widget_state_chain()  -> Chain widget state dependencies

"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QLineEdit, QPushButton, QTextEdit, QToolTip, QWidget
from app.ui.components.widgets import Button, ComboBox


__all__ = [
    # Signal Connection Patterns
    'connect_form_signals', 'connect_button_actions', 'batch_connect_signals',

    # Event Filtering & Handling
    'create_tooltip_event_filter', 'create_focus_event_filter', 'install_event_handlers',

    # State Management
    'create_toggle_handler', 'setup_conditional_visibility', 'manage_widget_state_chain',
]


# ── Signal Connection Patterns ──────────────────────────────────────────────────────────────────────────────
def connect_form_signals(
    form_widgets: Dict[str, QWidget],
    change_handlers: Dict[str, Callable] = None,
    validation_handler: Optional[Callable] = None
) -> None:
    """
    Connect form widget signals to appropriate handlers.

    Args:
        form_widgets: Dictionary mapping field names to widgets
        change_handlers: Optional specific handlers for each field
        validation_handler: Optional validation handler for all fields

    Examples:
        widgets = {"recipe_name": name_edit, "servings": servings_edit}
        handlers = {"recipe_name": on_name_changed}
        connect_form_signals(widgets, handlers, validate_form)
    """
    if change_handlers is None:
        change_handlers = {}

    for field_name, widget in form_widgets.items():
        # Connect specific handler if provided
        if field_name in change_handlers:
            handler = change_handlers[field_name]

            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(handler)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(handler)
            elif isinstance(widget, (ComboBox)):
                widget.currentTextChanged.connect(handler)

        # Connect validation handler if provided
        if validation_handler:
            if isinstance(widget, QLineEdit):
                widget.editingFinished.connect(validation_handler)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(validation_handler)
            elif isinstance(widget, ComboBox):
                widget.currentTextChanged.connect(validation_handler)

def connect_button_actions(
    buttons: Dict[str, QPushButton],
    action_handlers: Dict[str, Callable]
) -> None:
    """
    Connect button click signals to action handlers.

    Args:
        buttons: Dictionary mapping button names to button widgets
        action_handlers: Dictionary mapping button names to handler functions

    Examples:
        buttons = {"save": save_btn, "cancel": cancel_btn}
        handlers = {"save": save_recipe, "cancel": cancel_form}
        connect_button_actions(buttons, handlers)
    """
    for button_name, handler in action_handlers.items():
        if button_name in buttons:
            buttons[button_name].clicked.connect(handler)

def batch_connect_signals(signal_connections: List[tuple]) -> None:
    """
    Connect multiple signals at once from a list of (signal, slot) tuples.

    Args:
        signal_connections: List of (signal, slot) tuples to connect

    Examples:
        connections = [
            (name_edit.textChanged, on_name_changed),
            (save_btn.clicked, save_form),
            (cancel_btn.clicked, cancel_form)
        ]
        batch_connect_signals(connections)
    """
    for signal, slot in signal_connections:
        signal.connect(slot)


# ── Event Filtering & Handling ──────────────────────────────────────────────────────────────────────────────
class TooltipEventFilter(QObject):
    """Event filter for handling tooltips on disabled widgets."""

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Show tooltip on disabled widgets.

        Args:
            obj: The object receiving the event
            event: The event itself

        Returns:
            bool: True if event was handled, False to pass through
        """
        if event.type() == QEvent.ToolTip and not obj.isEnabled():
            QToolTip.showText(event.globalPos(), obj.toolTip(), obj)
            return True
        return super().eventFilter(obj, event)

class FocusEventFilter(QObject):
    """Event filter for handling focus events."""

    def __init__(self, focus_in_handler: Optional[Callable] = None,
                 focus_out_handler: Optional[Callable] = None):
        super().__init__()
        self.focus_in_handler = focus_in_handler
        self.focus_out_handler = focus_out_handler

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Handle focus in/out events.

        Args:
            obj: The object receiving the event
            event: The event itself

        Returns:
            bool: True if event was handled, False to pass through
        """
        if event.type() == QEvent.FocusIn and self.focus_in_handler:
            self.focus_in_handler(obj)
        elif event.type() == QEvent.FocusOut and self.focus_out_handler:
            self.focus_out_handler(obj)

        return super().eventFilter(obj, event)

def create_tooltip_event_filter() -> TooltipEventFilter:
    """
    Create a tooltip event filter for disabled widgets.

    Returns:
        TooltipEventFilter: Event filter instance

    Examples:
        tooltip_filter = create_tooltip_event_filter()
        disabled_widget.installEventFilter(tooltip_filter)
    """
    return TooltipEventFilter()

def create_focus_event_filter(
    focus_in_handler: Optional[Callable] = None,
    focus_out_handler: Optional[Callable] = None
) -> FocusEventFilter:
    """
    Create a focus event filter with custom handlers.

    Args:
        focus_in_handler: Handler for focus in events
        focus_out_handler: Handler for focus out events

    Returns:
        FocusEventFilter: Event filter instance

    Examples:
        focus_filter = create_focus_event_filter(
            lambda w: print(f"{w} gained focus"),
            lambda w: print(f"{w} lost focus")
        )
        widget.installEventFilter(focus_filter)
    """
    return FocusEventFilter(focus_in_handler, focus_out_handler)

def install_event_handlers(
    widgets: List[QWidget],
    event_filters: List[QObject]
) -> None:
    """
    Install multiple event handlers on a list of widgets.

    Args:
        widgets: List of widgets to install filters on
        event_filters: List of event filter objects

    Examples:
        filters = [create_tooltip_event_filter(), create_focus_event_filter()]
        install_event_handlers([widget1, widget2], filters)
    """
    for widget in widgets:
        for event_filter in event_filters:
            widget.installEventFilter(event_filter)


# ── State Management ────────────────────────────────────────────────────────────────────────────────────────
def create_toggle_handler(
    target_widgets: List[QWidget],
    property_name: str = "checked",
    state_values: tuple = (True, False)
) -> Callable:
    """
    Create a handler function that toggles widget states.

    Args:
        target_widgets: Widgets to toggle state on
        property_name: Property to toggle (checked, enabled, visible, etc.)
        state_values: Tuple of (active_state, inactive_state)

    Returns:
        Callable: Handler function that toggles the state

    Examples:
        toggle_visibility = create_toggle_handler([widget1, widget2], "visible")
        toggle_button.clicked.connect(toggle_visibility)
    """
    def toggle_handler():
        for widget in target_widgets:
            if hasattr(widget, property_name):
                current_value = getattr(widget, property_name)()
                new_value = state_values[1] if current_value == state_values[0] else state_values[0]
                getattr(widget, f"set{property_name.capitalize()}")(new_value)

    return toggle_handler

def setup_conditional_visibility(
    trigger_widget: QWidget,
    target_widgets: List[QWidget],
    show_condition: Callable[[Any], bool]
) -> None:
    """
    Set up conditional visibility based on trigger widget state.

    Args:
        trigger_widget: Widget whose state triggers visibility changes
        target_widgets: Widgets whose visibility will be controlled
        show_condition: Function that determines if targets should be visible

    Examples:
        # Show side dishes when main dish is selected
        setup_conditional_visibility(
            main_dish_combo,
            side_dish_widgets,
            lambda value: bool(value.strip())
        )
    """
    def update_visibility():
        # Get the appropriate value based on widget type
        if isinstance(trigger_widget, QLineEdit):
            value = trigger_widget.text()
        elif isinstance(trigger_widget, ComboBox):
            value = trigger_widget.currentText()
        else:
            value = None

        should_show = show_condition(value)

        for widget in target_widgets:
            widget.setVisible(should_show)

    # Connect to appropriate signal based on trigger widget type
    if isinstance(trigger_widget, QLineEdit):
        trigger_widget.textChanged.connect(update_visibility)
    elif isinstance(trigger_widget, ComboBox):
        trigger_widget.currentTextChanged.connect(update_visibility)

    # Set initial state
    update_visibility()

def manage_widget_state_chain(
    state_chain: List[Dict[str, Any]]
) -> None:
    """
    Manage a chain of widget state dependencies.

    Args:
        state_chain: List of state dependency definitions

    Examples:
        chain = [
            {
                "trigger": main_dish_combo,
                "targets": [side_dish1_combo, side_dish2_combo],
                "condition": lambda v: bool(v.strip()),
                "property": "enabled"
            },
            {
                "trigger": save_button,
                "targets": [form_widgets],
                "condition": lambda: validate_form(),
                "property": "enabled"
            }
        ]
        manage_widget_state_chain(chain)
    """
    for state_rule in state_chain:
        trigger = state_rule["trigger"]
        targets = state_rule["targets"]
        condition = state_rule["condition"]
        property_name = state_rule.get("property", "enabled")

        def create_handler(tgts, cond, prop):
            def handler():
                # Evaluate condition
                if callable(cond):
                    should_enable = cond()
                else:
                    should_enable = bool(cond)

                # Apply to targets
                for target in tgts:
                    if hasattr(target, f"set{prop.capitalize()}"):
                        getattr(target, f"set{prop.capitalize()}")(should_enable)
            return handler

        handler = create_handler(targets, condition, property_name)

        # Connect to appropriate trigger signal
        if isinstance(trigger, QLineEdit):
            trigger.textChanged.connect(handler)
        elif isinstance(trigger, ComboBox):
            trigger.currentTextChanged.connect(handler)
        elif isinstance(trigger, Button):
            trigger.clicked.connect(handler)

        # Set initial state
        handler()
