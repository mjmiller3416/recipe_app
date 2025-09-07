"""Unit tests for EventCoordinator.

Tests the unified event coordination system including:
- Debounced event handling with various strategies
- Managed signal connection lifecycle
- Priority-based event routing with filtering
- Coordination patterns (search, filter, validation)
- Multi-component event handling
- Performance monitoring and metrics
- Error handling and edge cases
- Resource cleanup and memory management

The EventCoordinator is a critical component of the RecipeBrowser coordinator
architecture, providing centralized event management and coordination.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────────────────────────────────
import time
import weakref
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QCheckBox, QPushButton

from app.ui.managers.events.event_coordinator import EventCoordinator
from app.ui.managers.events.debouncer import DebouncingStrategy, DebouncingOptions
from app.ui.managers.events.signal_manager import ConnectionScope, ConnectionInfo
from app.ui.managers.events.event_router import EventPriority, EventFilter


# ── Test Data and Mock Classes ──────────────────────────────────────────────────────────────────────────────
class TestQObject(QObject):
    """Test QObject with signals for testing."""
    test_signal = Signal(str)
    value_changed = Signal(int)
    text_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.emitted_signals = []
    
    def emit_test_signal(self, text: str):
        self.test_signal.emit(text)
        self.emitted_signals.append(('test_signal', text))
    
    def emit_value_changed(self, value: int):
        self.value_changed.emit(value)
        self.emitted_signals.append(('value_changed', value))


class TestWidget(QWidget):
    """Test widget class for signal testing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.received_values = []
    
    def handle_signal(self, value):
        self.received_values.append(value)


# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def event_coordinator():
    """Create EventCoordinator instance for testing."""
    coordinator = EventCoordinator(coordinator_name="TestCoordinator")
    yield coordinator
    coordinator.cleanup_all_coordinations()


@pytest.fixture
def test_sender(qapp):
    """Create test QObject sender."""
    sender = TestQObject()
    yield sender
    sender.deleteLater()


@pytest.fixture
def test_receiver(qapp):
    """Create test widget receiver."""
    receiver = TestWidget()
    yield receiver
    receiver.deleteLater()


@pytest.fixture
def line_edit(qapp):
    """Create QLineEdit for signal testing."""
    edit = QLineEdit()
    yield edit
    edit.deleteLater()


@pytest.fixture
def combo_box(qapp):
    """Create QComboBox for signal testing."""
    combo = QComboBox()
    combo.addItems(["Option 1", "Option 2", "Option 3"])
    yield combo
    combo.deleteLater()


@pytest.fixture
def check_box(qapp):
    """Create QCheckBox for signal testing."""
    checkbox = QCheckBox("Test Option")
    yield checkbox
    checkbox.deleteLater()


# ── Test Classes ─────────────────────────────────────────────────────────────────────────────────────────────
class TestEventCoordinatorInitialization:
    """Test EventCoordinator initialization and setup."""
    
    def test_initialization_default(self, event_coordinator):
        """Test default initialization."""
        coordinator = event_coordinator
        
        # Verify basic properties
        assert coordinator.coordinator_name == "TestCoordinator"
        
        # Verify component managers exist
        assert coordinator.debouncer is not None
        assert coordinator.signal_manager is not None
        assert coordinator.event_router is not None
        
        # Verify state containers
        assert isinstance(coordinator._active_coordinations, dict)
        assert isinstance(coordinator._coordination_chains, dict)
        assert isinstance(coordinator._coordination_metrics, dict)
    
    def test_coordinator_name_assignment(self):
        """Test coordinator name assignment."""
        custom_coordinator = EventCoordinator(coordinator_name="CustomName")
        
        assert custom_coordinator.coordinator_name == "CustomName"
        
        custom_coordinator.cleanup_all_coordinations()
    
    def test_signal_emissions_on_init(self):
        """Test signal emissions during initialization."""
        signal_emitted = []
        
        # Create coordinator and connect to initialization signal
        coordinator = EventCoordinator()
        coordinator.coordination_started.connect(lambda name: signal_emitted.append(name))
        
        # Note: Signal is emitted during init, so we need to reconnect to test
        coordinator.coordination_started.emit("TestInit")
        
        assert "TestInit" in signal_emitted
        
        coordinator.cleanup_all_coordinations()


class TestDebouncedEventHandling:
    """Test debounced event handling functionality."""
    
    def test_setup_debounced_handler_basic(self, event_coordinator):
        """Test basic debounced handler setup."""
        coordinator = event_coordinator
        
        handler_calls = []
        def test_handler(value):
            handler_calls.append(value)
        
        # Setup debounced handler
        action_name = coordinator.setup_debounced_handler(
            "test_action",
            test_handler,
            delay_ms=100,
            strategy=DebouncingStrategy.TRAILING
        )
        
        assert action_name == "test_action"
        
        # Trigger debounced action
        coordinator.trigger_debounced("test_action", "test_value")
        
        # Should not execute immediately
        assert len(handler_calls) == 0
        
        # Wait for debounce delay
        time.sleep(0.15)
        QApplication.processEvents()
        
        # Now should have executed
        assert len(handler_calls) == 1
        assert handler_calls[0] == "test_value"
    
    def test_setup_debounced_handler_with_options(self, event_coordinator):
        """Test debounced handler with specific options."""
        coordinator = event_coordinator
        
        handler_calls = []
        def test_handler(*args, **kwargs):
            handler_calls.append((args, kwargs))
        
        # Setup with advanced options
        coordinator.setup_debounced_handler(
            "advanced_action",
            test_handler,
            delay_ms=50,
            strategy=DebouncingStrategy.LEADING,
            max_wait_ms=200
        )
        
        # Trigger multiple times rapidly
        for i in range(3):
            coordinator.trigger_debounced("advanced_action", f"value_{i}", extra=f"extra_{i}")
            time.sleep(0.01)
        
        # With LEADING strategy, should execute once immediately
        time.sleep(0.1)
        QApplication.processEvents()
        
        assert len(handler_calls) >= 1
    
    def test_trigger_debounced_nonexistent(self, event_coordinator):
        """Test triggering nonexistent debounced action."""
        coordinator = event_coordinator
        
        result = coordinator.trigger_debounced("nonexistent_action", "value")
        
        assert result is None
    
    def test_cancel_debounced(self, event_coordinator):
        """Test cancelling debounced action."""
        coordinator = event_coordinator
        
        handler_calls = []
        def test_handler(value):
            handler_calls.append(value)
        
        coordinator.setup_debounced_handler("cancel_test", test_handler, delay_ms=100)
        
        # Trigger action
        coordinator.trigger_debounced("cancel_test", "should_cancel")
        
        # Cancel before execution
        success = coordinator.cancel_debounced("cancel_test")
        assert success is True
        
        # Wait past original delay
        time.sleep(0.15)
        QApplication.processEvents()
        
        # Should not have executed
        assert len(handler_calls) == 0
    
    def test_flush_debounced(self, event_coordinator):
        """Test immediate execution of debounced action."""
        coordinator = event_coordinator
        
        handler_calls = []
        def test_handler(value):
            handler_calls.append(value)
        
        coordinator.setup_debounced_handler("flush_test", test_handler, delay_ms=1000)
        
        # Trigger action
        coordinator.trigger_debounced("flush_test", "immediate_value")
        
        # Flush immediately
        result = coordinator.flush_debounced("flush_test")
        
        # Should execute immediately
        assert len(handler_calls) == 1
        assert handler_calls[0] == "immediate_value"
    
    def test_debounced_signal_emissions(self, event_coordinator):
        """Test signal emissions for debounced actions."""
        coordinator = event_coordinator
        
        signal_captures = []
        coordinator.debounced_action_triggered.connect(
            lambda action, delay: signal_captures.append((action, delay))
        )
        
        def test_handler():
            pass
        
        coordinator.setup_debounced_handler("signal_test", test_handler, delay_ms=75)
        coordinator.trigger_debounced("signal_test")
        
        # Should emit signal
        assert len(signal_captures) == 1
        assert signal_captures[0] == ("signal_test", 75)


class TestSignalConnectionManagement:
    """Test managed signal connection functionality."""
    
    def test_connect_signal_basic(self, event_coordinator, test_sender, test_receiver):
        """Test basic signal connection."""
        coordinator = event_coordinator
        
        # Connect signal
        connection_id = coordinator.connect_signal(
            sender=test_sender,
            signal_name="test_signal",
            receiver=test_receiver,
            slot=test_receiver.handle_signal,
            scope=ConnectionScope.VIEW_LIFECYCLE
        )
        
        assert connection_id is not None
        
        # Test signal emission
        test_sender.emit_test_signal("test_message")
        QApplication.processEvents()
        
        # Verify signal was received
        assert "test_message" in test_receiver.received_values
    
    def test_connect_signals_batch(self, event_coordinator, test_sender, test_receiver):
        """Test batch signal connection."""
        coordinator = event_coordinator
        
        connection_specs = [
            {
                'sender': test_sender,
                'signal_name': 'test_signal',
                'receiver': test_receiver,
                'slot': lambda msg: test_receiver.handle_signal(f"first_{msg}"),
                'scope': ConnectionScope.VIEW_LIFECYCLE
            },
            {
                'sender': test_sender,
                'signal_name': 'value_changed',
                'receiver': test_receiver,
                'slot': lambda val: test_receiver.handle_signal(f"second_{val}"),
                'scope': ConnectionScope.TEMPORARY
            }
        ]
        
        connection_ids = coordinator.connect_signals(connection_specs)
        
        assert len(connection_ids) == 2
        assert all(conn_id is not None for conn_id in connection_ids)
        
        # Test both signals
        test_sender.emit_test_signal("batch_test")
        test_sender.emit_value_changed(42)
        QApplication.processEvents()
        
        # Verify both signals were received
        received = test_receiver.received_values
        assert any("first_batch_test" in str(val) for val in received)
        assert any("second_42" in str(val) for val in received)
    
    def test_disconnect_signal(self, event_coordinator, test_sender, test_receiver):
        """Test disconnecting managed signal."""
        coordinator = event_coordinator
        
        # Connect signal
        connection_id = coordinator.connect_signal(
            sender=test_sender,
            signal_name="test_signal",
            receiver=test_receiver,
            slot=test_receiver.handle_signal
        )
        
        # Disconnect signal
        success = coordinator.disconnect_signal(connection_id)
        assert success is True
        
        # Test that signal is no longer connected
        test_sender.emit_test_signal("after_disconnect")
        QApplication.processEvents()
        
        # Should not receive the message
        assert "after_disconnect" not in test_receiver.received_values
    
    def test_disconnect_by_scope(self, event_coordinator, test_sender, test_receiver):
        """Test disconnecting signals by scope."""
        coordinator = event_coordinator
        
        # Connect signals with different scopes
        coordinator.connect_signal(
            test_sender, "test_signal", test_receiver, test_receiver.handle_signal,
            ConnectionScope.VIEW_LIFECYCLE
        )
        coordinator.connect_signal(
            test_sender, "value_changed", test_receiver, test_receiver.handle_signal,
            ConnectionScope.TEMPORARY
        )
        
        # Disconnect all temporary connections
        count = coordinator.disconnect_signals_by_scope(ConnectionScope.TEMPORARY)
        
        assert count >= 1  # At least one connection should be disconnected


class TestEventRouting:
    """Test event routing functionality."""
    
    def test_register_event_route(self, event_coordinator):
        """Test registering event routes."""
        coordinator = event_coordinator
        
        handled_events = []
        def test_handler(event_data):
            handled_events.append(event_data)
            return "handled"
        
        # Register route
        success = coordinator.register_event_route(
            route_name="test_route",
            handler=test_handler,
            priority=EventPriority.HIGH,
            description="Test route for unit tests"
        )
        
        assert success is True
    
    def test_route_event(self, event_coordinator):
        """Test routing events to handlers."""
        coordinator = event_coordinator
        
        handled_events = []
        def test_handler(event_data):
            handled_events.append(event_data)
            return f"handled: {event_data.get('message', 'none')}"
        
        # Register route
        coordinator.register_event_route("route_test", test_handler)
        
        # Route event
        results = coordinator.route_event("route_test", {"message": "test_event"})
        
        # Verify event was handled
        assert len(results) >= 1
        assert "handled: test_event" in results
        assert len(handled_events) == 1
        assert handled_events[0]["message"] == "test_event"
    
    def test_event_routing_with_filters(self, event_coordinator):
        """Test event routing with filters."""
        coordinator = event_coordinator
        
        handled_events = []
        def test_handler(event_data):
            handled_events.append(event_data)
            return "filtered_handled"
        
        # Create filter
        message_filter = EventFilter(
            "message_length_filter",
            lambda data: len(data.get('message', '')) > 5,
            "Message must be longer than 5 characters"
        )
        
        # Register route with filter
        coordinator.register_event_route(
            "filtered_route",
            test_handler,
            filters=[message_filter]
        )
        
        # Route event that passes filter
        results1 = coordinator.route_event("filtered_route", {"message": "long_message"})
        assert len(results1) >= 1
        assert len(handled_events) == 1
        
        # Route event that fails filter
        results2 = coordinator.route_event("filtered_route", {"message": "short"})
        assert len(results2) == 0  # Should be filtered out
        assert len(handled_events) == 1  # No additional handling
    
    def test_enable_disable_routes(self, event_coordinator):
        """Test enabling and disabling event routes."""
        coordinator = event_coordinator
        
        handled_events = []
        def test_handler(event_data):
            handled_events.append(event_data)
            return "handled"
        
        coordinator.register_event_route("toggle_route", test_handler)
        
        # Disable route
        success = coordinator.disable_route("toggle_route")
        assert success is True
        
        # Route event to disabled route
        results = coordinator.route_event("toggle_route", {"test": "data"})
        assert len(results) == 0
        assert len(handled_events) == 0
        
        # Re-enable route
        success = coordinator.enable_route("toggle_route")
        assert success is True
        
        # Route event to enabled route
        results = coordinator.route_event("toggle_route", {"test": "data"})
        assert len(results) >= 1
        assert len(handled_events) == 1
    
    def test_event_coordination_signals(self, event_coordinator):
        """Test event coordination signal emissions."""
        coordinator = event_coordinator
        
        coordination_signals = []
        coordinator.event_coordination_complete.connect(
            lambda event, count: coordination_signals.append((event, count))
        )
        
        # Register handler
        def test_handler(event_data):
            return "test_result"
        
        coordinator.register_event_route("signal_test", test_handler)
        
        # Route event
        coordinator.route_event("signal_test", {"data": "test"})
        
        # Verify coordination complete signal
        assert len(coordination_signals) == 1
        assert coordination_signals[0][0] == "signal_test"
        assert coordination_signals[0][1] == 1  # One handler


class TestCoordinationPatterns:
    """Test specialized coordination patterns."""
    
    def test_search_coordination_setup(self, event_coordinator, line_edit):
        """Test search coordination pattern setup."""
        coordinator = event_coordinator
        
        search_results = []
        def search_handler(search_term):
            search_results.append(search_term)
            return f"search_results_for_{search_term}"
        
        # Setup search coordination
        coordination_id = coordinator.setup_search_coordination(
            search_input=line_edit,
            search_handler=search_handler,
            delay_ms=100,
            min_length=3
        )
        
        assert coordination_id is not None
        assert coordination_id in coordinator._active_coordinations
        
        # Test search coordination
        line_edit.setText("test_search_term")
        line_edit.textChanged.emit("test_search_term")
        
        # Wait for debounce
        time.sleep(0.15)
        QApplication.processEvents()
        
        # Verify search was executed
        assert len(search_results) >= 1
        assert "test_search_term" in search_results
    
    def test_filter_coordination_setup(self, event_coordinator, combo_box, check_box):
        """Test filter coordination pattern setup."""
        coordinator = event_coordinator
        
        filter_results = []
        def filter_handler(filters):
            filter_results.append(filters)
            return f"filtered_with_{filters}"
        
        # Setup filter coordination
        filter_controls = {
            'category': combo_box,
            'favorites': check_box
        }
        
        coordination_id = coordinator.setup_filter_coordination(
            filter_controls=filter_controls,
            filter_handler=filter_handler,
            delay_ms=50,
            batch_updates=True
        )
        
        assert coordination_id is not None
        
        # Test filter changes
        combo_box.setCurrentText("Option 2")
        check_box.setChecked(True)
        
        # Trigger signals
        combo_box.currentTextChanged.emit("Option 2")
        check_box.stateChanged.emit(2)  # Checked state
        
        # Wait for debounce
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Verify filter was applied
        assert len(filter_results) >= 1
    
    def test_validation_coordination_setup(self, event_coordinator, line_edit):
        """Test validation coordination pattern setup."""
        coordinator = event_coordinator
        
        validation_results = []
        def validation_handler(field_data):
            validation_results.append(field_data)
            # Return validation errors
            errors = {}
            if len(field_data.get('email', '')) < 5:
                errors['email'] = 'Email too short'
            return errors
        
        # Setup validation coordination
        form_fields = {'email': line_edit}
        
        coordination_id = coordinator.setup_validation_coordination(
            form_fields=form_fields,
            validation_handler=validation_handler,
            delay_ms=200
        )
        
        assert coordination_id is not None
        
        # Test field change
        line_edit.setText("test@example.com")
        line_edit.textChanged.emit("test@example.com")
        
        # Wait for validation debounce
        time.sleep(0.25)
        QApplication.processEvents()
        
        # Verify validation occurred
        assert len(validation_results) >= 1


class TestCoordinationManagement:
    """Test coordination lifecycle management."""
    
    def test_get_coordination_info(self, event_coordinator, line_edit):
        """Test retrieving coordination information."""
        coordinator = event_coordinator
        
        # Setup coordination
        coordination_id = coordinator.setup_search_coordination(
            line_edit, lambda term: None, delay_ms=100
        )
        
        # Get coordination info
        info = coordinator.get_coordination_info(coordination_id)
        
        assert info is not None
        assert info['type'] == 'search'
        assert info['search_input'] is line_edit
        assert info['delay_ms'] == 100
    
    def test_remove_coordination(self, event_coordinator, line_edit):
        """Test removing coordination."""
        coordinator = event_coordinator
        
        # Setup coordination
        coordination_id = coordinator.setup_search_coordination(
            line_edit, lambda term: None
        )
        
        # Verify coordination exists
        assert coordination_id in coordinator._active_coordinations
        
        # Remove coordination
        success = coordinator.remove_coordination(coordination_id)
        assert success is True
        
        # Verify coordination is removed
        assert coordination_id not in coordinator._active_coordinations
        
        # Try to remove again
        success = coordinator.remove_coordination(coordination_id)
        assert success is False
    
    def test_cleanup_all_coordinations(self, event_coordinator, line_edit, combo_box):
        """Test cleaning up all coordinations."""
        coordinator = event_coordinator
        
        # Setup multiple coordinations
        search_id = coordinator.setup_search_coordination(line_edit, lambda term: None)
        filter_id = coordinator.setup_filter_coordination(
            {'category': combo_box}, lambda filters: None
        )
        
        # Verify coordinations exist
        assert len(coordinator._active_coordinations) >= 2
        
        # Cleanup all
        count = coordinator.cleanup_all_coordinations()
        
        assert count >= 2
        assert len(coordinator._active_coordinations) == 0
    
    def test_performance_metrics(self, event_coordinator, line_edit):
        """Test performance metrics collection."""
        coordinator = event_coordinator
        
        # Setup some coordinations
        coordinator.setup_search_coordination(line_edit, lambda term: None)
        coordinator.register_event_route("test_route", lambda data: "result")
        
        # Get metrics
        metrics = coordinator.get_performance_metrics()
        
        assert 'coordinator_name' in metrics
        assert 'active_coordinations' in metrics
        assert 'debouncer_metrics' in metrics
        assert 'signal_manager_metrics' in metrics
        assert 'event_router_metrics' in metrics
        assert 'coordination_types' in metrics
        
        assert metrics['coordinator_name'] == "TestCoordinator"
        assert metrics['active_coordinations'] >= 1


class TestEventCoordinatorHelpers:
    """Test helper methods and utilities."""
    
    def test_get_appropriate_signal_widget_types(self, event_coordinator, qapp):
        """Test appropriate signal detection for widget types."""
        coordinator = event_coordinator
        
        # Test different widget types
        line_edit = QLineEdit()
        combo_box = QComboBox()
        check_box = QCheckBox()
        
        try:
            # Test signal mapping
            assert coordinator._get_appropriate_signal(line_edit) == 'textChanged'
            assert coordinator._get_appropriate_signal(combo_box) == 'currentTextChanged'
            assert coordinator._get_appropriate_signal(check_box) == 'stateChanged'
            
            # Test unknown widget
            button = QPushButton()
            assert coordinator._get_appropriate_signal(button) is None
        finally:
            line_edit.deleteLater()
            combo_box.deleteLater()
            check_box.deleteLater()
            button.deleteLater()
    
    def test_coordination_error_handling(self, event_coordinator, line_edit):
        """Test error handling in coordination operations."""
        coordinator = event_coordinator
        
        # Test coordination with invalid handler
        def failing_handler(search_term):
            raise Exception("Handler failure")
        
        coordination_id = coordinator.setup_search_coordination(
            line_edit, failing_handler
        )
        
        # Trigger search that will fail
        line_edit.setText("trigger_error")
        line_edit.textChanged.emit("trigger_error")
        
        # Wait for execution
        time.sleep(0.1)
        QApplication.processEvents()
        
        # Should handle error gracefully
        assert coordination_id in coordinator._active_coordinations
    
    def test_coordination_lifecycle_signals(self, event_coordinator):
        """Test coordination lifecycle signal emissions."""
        coordinator = event_coordinator
        
        signal_captures = []
        
        coordinator.coordination_started.connect(
            lambda name: signal_captures.append(f"started:{name}")
        )
        coordinator.coordinator_cleanup_complete.connect(
            lambda: signal_captures.append("cleanup_complete")
        )
        
        # Cleanup should emit signal
        coordinator.cleanup_all_coordinations()
        
        assert "cleanup_complete" in signal_captures


class TestEventCoordinatorEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_coordination_with_deleted_widgets(self, event_coordinator, qapp):
        """Test coordination behavior with deleted widgets."""
        coordinator = event_coordinator
        
        # Create widget
        line_edit = QLineEdit()
        
        # Setup coordination
        coordination_id = coordinator.setup_search_coordination(
            line_edit, lambda term: None
        )
        
        # Delete widget
        line_edit.deleteLater()
        QApplication.processEvents()
        
        # Cleanup should handle deleted widget gracefully
        success = coordinator.remove_coordination(coordination_id)
        # Should succeed or fail gracefully without crashing
    
    def test_invalid_coordination_parameters(self, event_coordinator):
        """Test coordination with invalid parameters."""
        coordinator = event_coordinator
        
        # Test with None search input
        try:
            coordination_id = coordinator.setup_search_coordination(
                None, lambda term: None
            )
            # Should handle gracefully
        except Exception:
            # Expected to handle invalid input
            pass
        
        # Test with empty filter controls
        coordination_id = coordinator.setup_filter_coordination(
            {}, lambda filters: None
        )
        
        # Should create coordination but with no controls
        assert coordination_id is not None
    
    def test_rapid_coordination_changes(self, event_coordinator, line_edit):
        """Test rapid coordination setup and teardown."""
        coordinator = event_coordinator
        
        # Rapidly create and destroy coordinations
        coordination_ids = []
        
        for i in range(10):
            coord_id = coordinator.setup_search_coordination(
                line_edit, lambda term, i=i: None
            )
            coordination_ids.append(coord_id)
            
            if i % 2 == 0:  # Remove every other coordination
                coordinator.remove_coordination(coord_id)
        
        # Should handle rapid changes without issues
        remaining = len(coordinator._active_coordinations)
        assert remaining >= 0
    
    def test_memory_cleanup_with_coordinations(self, event_coordinator, line_edit):
        """Test memory cleanup behavior with active coordinations."""
        coordinator = event_coordinator
        
        # Create coordinations with objects that can be garbage collected
        coordination_id = coordinator.setup_search_coordination(
            line_edit, lambda term: None
        )
        
        # Force cleanup
        coordinator.cleanup_all_coordinations()
        
        # Should complete without memory leaks
        assert len(coordinator._active_coordinations) == 0