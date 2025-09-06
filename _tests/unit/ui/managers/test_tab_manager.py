"""Tests for TabManager utility class.

Tests comprehensive tab management operations including:
- Tab addition, removal, and index management
- Special tab handling (+ tab)
- State tracking and signal emissions  
- Registry operations and validation
- Edge cases and error handling
"""

from unittest.mock import MagicMock, Mock

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QWidget
import pytest

from app.ui.managers.tab_manager import TabManager, TabOperation, TabState

@pytest.fixture
def qapp():
    """Provide QApplication for Qt widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def tab_widget(qapp):
    """Provide QTabWidget for testing."""
    return QTabWidget()


@pytest.fixture  
def tab_manager(tab_widget):
    """Provide TabManager instance for testing."""
    return TabManager(tab_widget)


@pytest.fixture
def sample_widget(qapp):
    """Provide sample QWidget for tab content."""
    widget = QWidget()
    widget.setObjectName("TestWidget")
    return widget


@pytest.fixture
def sample_widgets(qapp):
    """Provide multiple sample widgets."""
    widgets = []
    for i in range(3):
        widget = QWidget()
        widget.setObjectName(f"TestWidget_{i}")
        widgets.append(widget)
    return widgets


class TestTabManagerBasics:
    """Test basic TabManager functionality."""
    
    def test_initialization(self, tab_widget):
        """Test TabManager initialization."""
        manager = TabManager(tab_widget)
        
        assert manager.tab_widget is tab_widget
        assert manager.get_tab_count() == 0
        assert manager.tab_registry == {}
        assert not manager.has_special_tab()
    
    def test_add_single_tab(self, tab_manager, sample_widget):
        """Test adding a single tab."""
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        assert index == 0
        assert tab_manager.get_tab_count() == 1
        assert tab_manager.get_tab_widget(0) is sample_widget
        assert tab_manager.get_current_index() == 0
        assert tab_manager.get_tab_state(0) == TabState.ACTIVE
    
    def test_add_multiple_tabs(self, tab_manager, sample_widgets):
        """Test adding multiple tabs."""
        indices = []
        for i, widget in enumerate(sample_widgets):
            index = tab_manager.add_tab(widget, f"Tab {i}")
            indices.append(index)
        
        assert indices == [0, 1, 2]
        assert tab_manager.get_tab_count() == 3
        assert tab_manager.get_current_index() == 2  # Last added becomes current
        
        # Verify all widgets are accessible
        for i, widget in enumerate(sample_widgets):
            assert tab_manager.get_tab_widget(i) is widget
    
    def test_add_tab_validation(self, tab_manager):
        """Test tab addition validation."""
        # Test None widget
        with pytest.raises(ValueError, match="Widget cannot be None"):
            tab_manager.add_tab(None, "Test")
            
        # Test empty title
        widget = QWidget()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            tab_manager.add_tab(widget, "")
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            tab_manager.add_tab(widget, "   ")


class TestTabManagerRemoval:
    """Test tab removal functionality."""
    
    def test_remove_single_tab(self, tab_manager, sample_widget):
        """Test removing a single tab."""
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        success = tab_manager.remove_tab(index)
        
        assert success is True
        assert tab_manager.get_tab_count() == 0
        assert tab_manager.get_tab_widget(index) is None
        assert index not in tab_manager.tab_registry
    
    def test_remove_middle_tab(self, tab_manager, sample_widgets):
        """Test removing middle tab and index updates."""
        # Add three tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        # Remove middle tab (index 1)
        success = tab_manager.remove_tab(1)
        
        assert success is True
        assert tab_manager.get_tab_count() == 2
        
        # Verify index updates
        assert tab_manager.get_tab_widget(0) is sample_widgets[0]
        assert tab_manager.get_tab_widget(1) is sample_widgets[2]  # Was index 2, now 1
        assert tab_manager.get_tab_widget(2) is None  # No longer exists
    
    def test_remove_current_tab_selection(self, tab_manager, sample_widgets):
        """Test tab selection after removing current tab."""
        # Add three tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        # Current should be last added (index 2)
        assert tab_manager.get_current_index() == 2
        
        # Remove current tab
        success = tab_manager.remove_tab(2)
        
        assert success is True
        # Should auto-select previous tab (index 1, which is now the last tab)
        assert tab_manager.get_current_index() == 1
    
    def test_remove_first_tab_selection(self, tab_manager, sample_widgets):
        """Test removing first tab when it's current."""
        # Add three tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        # Set first tab as current
        tab_manager.set_current_index(0)
        assert tab_manager.get_current_index() == 0
        
        # Remove first tab
        success = tab_manager.remove_tab(0)
        
        assert success is True
        # Should auto-select new first tab (was index 1, now 0)
        assert tab_manager.get_current_index() == 0
    
    def test_remove_invalid_tab(self, tab_manager, sample_widget):
        """Test removing invalid tab indices."""
        tab_manager.add_tab(sample_widget, "Test Tab")
        
        # Test negative index
        assert tab_manager.remove_tab(-1) is False
        
        # Test out of bounds index
        assert tab_manager.remove_tab(10) is False
        
        # Test removing again after valid removal
        assert tab_manager.remove_tab(0) is True
        assert tab_manager.remove_tab(0) is False  # Already removed


class TestTabManagerSpecialTabs:
    """Test special tab handling (like + tab)."""
    
    def test_register_special_tab(self, tab_widget, sample_widgets):
        """Test registering special tabs."""
        manager = TabManager(tab_widget)
        
        # Add regular tabs first
        for i, widget in enumerate(sample_widgets[:2]):
            manager.add_tab(widget, f"Tab {i}")
        
        # Manually add a "+" tab like in meal planner
        plus_widget = QWidget()
        plus_widget.setObjectName("PlusTab")
        plus_index = tab_widget.addTab(plus_widget, "+")
        
        # Register as special
        manager.register_special_tab(plus_index)
        
        assert manager.has_special_tab()
        assert manager.get_tab_count() == 2  # Still only counts regular tabs
        assert manager.get_tab_widget(plus_index) is None  # Special tabs not in registry
    
    def test_add_tab_with_special_tab(self, tab_widget, sample_widgets):
        """Test adding regular tabs when special tab exists."""
        manager = TabManager(tab_widget)
        
        # Add a regular tab
        manager.add_tab(sample_widgets[0], "Regular Tab")
        
        # Manually add "+" tab at end
        plus_widget = QWidget() 
        plus_index = tab_widget.addTab(plus_widget, "+")
        manager.register_special_tab(plus_index)
        
        # Add another regular tab - should insert before special tab
        new_index = manager.add_tab(sample_widgets[1], "New Regular Tab")
        
        assert new_index == 1  # Inserted before special tab
        assert tab_widget.tabText(1) == "New Regular Tab"
        assert tab_widget.tabText(2) == "+"  # Special tab moved to end
    
    def test_cannot_remove_special_tab(self, tab_widget, sample_widget):
        """Test that special tabs cannot be removed."""
        manager = TabManager(tab_widget)
        
        # Add regular tab
        manager.add_tab(sample_widget, "Regular")
        
        # Add special tab
        plus_widget = QWidget()
        plus_index = tab_widget.addTab(plus_widget, "+")  
        manager.register_special_tab(plus_index)
        
        # Try to remove special tab
        success = manager.remove_tab(plus_index)
        
        assert success is False
        assert tab_widget.count() == 2  # Both tabs still exist
    
    def test_get_insert_index(self, tab_widget, sample_widget):
        """Test getting correct insertion index with special tabs."""
        manager = TabManager(tab_widget)
        
        # Initially, insert index should be 0
        assert manager.get_insert_index() == 0
        
        # Add regular tab
        manager.add_tab(sample_widget, "Regular")
        
        # Add special tab at end
        plus_widget = QWidget()
        plus_index = tab_widget.addTab(plus_widget, "+")
        manager.register_special_tab(plus_index)
        
        # Insert index should be before special tab
        assert manager.get_insert_index() == 1


class TestTabManagerState:
    """Test tab state management."""
    
    def test_tab_states(self, tab_manager, sample_widget):
        """Test tab state tracking."""
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        # Initial state should be ACTIVE
        assert tab_manager.get_tab_state(index) == TabState.ACTIVE
        
        # Test state changes
        assert tab_manager.set_tab_state(index, TabState.MODIFIED) is True
        assert tab_manager.get_tab_state(index) == TabState.MODIFIED
        
        assert tab_manager.set_tab_state(index, TabState.LOADING) is True  
        assert tab_manager.get_tab_state(index) == TabState.LOADING
        
        assert tab_manager.set_tab_state(index, TabState.ERROR) is True
        assert tab_manager.get_tab_state(index) == TabState.ERROR
    
    def test_invalid_state_operations(self, tab_manager):
        """Test state operations on invalid indices."""
        # Test getting state of non-existent tab
        assert tab_manager.get_tab_state(99) is None
        
        # Test setting state of non-existent tab
        assert tab_manager.set_tab_state(99, TabState.MODIFIED) is False
    
    def test_tab_title_operations(self, tab_manager, sample_widget):
        """Test tab title operations."""
        index = tab_manager.add_tab(sample_widget, "Original Title")
        
        # Test title update
        assert tab_manager.set_tab_title(index, "New Title") is True
        assert tab_manager.tab_widget.tabText(index) == "New Title"
        
        # Test invalid operations
        assert tab_manager.set_tab_title(99, "Invalid") is False
        assert tab_manager.set_tab_title(index, "") is False
        assert tab_manager.set_tab_title(index, "   ") is False


class TestTabManagerSignals:
    """Test TabManager signal emissions."""
    
    def test_tab_added_signal(self, tab_manager, sample_widget):
        """Test tab_added signal emission."""
        signal_spy = Mock()
        tab_manager.tab_added.connect(signal_spy)
        
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        signal_spy.assert_called_once_with(index, sample_widget)
    
    def test_tab_removed_signal(self, tab_manager, sample_widget):
        """Test tab_removed signal emission.""" 
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        signal_spy = Mock()
        tab_manager.tab_removed.connect(signal_spy)
        
        tab_manager.remove_tab(index)
        
        signal_spy.assert_called_once_with(index, sample_widget)
    
    def test_tab_state_changed_signal(self, tab_manager, sample_widget):
        """Test tab_state_changed signal emission."""
        index = tab_manager.add_tab(sample_widget, "Test Tab")
        
        signal_spy = Mock()
        tab_manager.tab_state_changed.connect(signal_spy)
        
        tab_manager.set_tab_state(index, TabState.MODIFIED)
        
        signal_spy.assert_called_once_with(index, TabState.MODIFIED.value)
    
    def test_mapping_updated_signal(self, tab_manager, sample_widgets):
        """Test tab_mapping_updated signal emission."""
        signal_spy = Mock()
        tab_manager.tab_mapping_updated.connect(signal_spy)
        
        # Adding tab should emit mapping update
        tab_manager.add_tab(sample_widgets[0], "Tab 1")
        
        assert signal_spy.call_count >= 1
        
        # Removing tab should also emit mapping update  
        tab_manager.remove_tab(0)
        
        assert signal_spy.call_count >= 2


class TestTabManagerRegistry:
    """Test tab registry operations."""
    
    def test_registry_access(self, tab_manager, sample_widgets):
        """Test registry read-only access."""
        # Add some tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        registry = tab_manager.tab_registry
        
        # Should be a copy, not reference
        assert registry is not tab_manager._tab_registry
        assert len(registry) == 3
        
        # Verify contents
        for i, widget in enumerate(sample_widgets):
            assert registry[i] is widget
    
    def test_get_valid_indices(self, tab_manager, sample_widgets):
        """Test getting valid tab indices."""
        # Add regular tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        # Add special tab
        plus_widget = QWidget()
        plus_index = tab_manager.tab_widget.addTab(plus_widget, "+")
        tab_manager.register_special_tab(plus_index)
        
        valid_indices = tab_manager.get_valid_indices()
        
        assert len(valid_indices) == 3
        assert set(valid_indices) == {0, 1, 2}
        assert plus_index not in valid_indices
    
    def test_update_mapping(self, tab_manager, sample_widgets):
        """Test manual mapping update."""
        # Add tabs normally
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        original_count = tab_manager.get_tab_count()
        
        # Simulate external tab addition (bypassing TabManager)
        external_widget = QWidget()
        tab_manager.tab_widget.addTab(external_widget, "External")
        
        # TabManager shouldn't know about it yet
        assert tab_manager.get_tab_count() == original_count
        
        # Update mapping to sync
        tab_manager.update_mapping()
        
        # Now TabManager should include the external tab
        assert tab_manager.get_tab_count() == original_count + 1


class TestTabManagerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_tab_widget_operations(self, tab_manager):
        """Test operations on empty tab widget."""
        # All operations should handle empty state gracefully
        assert tab_manager.get_tab_count() == 0
        assert tab_manager.get_current_index() >= -1  # Qt returns -1 for empty
        assert tab_manager.get_tab_widget(0) is None
        assert tab_manager.remove_tab(0) is False
        assert tab_manager.get_valid_indices() == []
    
    def test_current_index_operations(self, tab_manager, sample_widgets):
        """Test current index operations."""
        # Add tabs
        for i, widget in enumerate(sample_widgets):
            tab_manager.add_tab(widget, f"Tab {i}")
        
        # Test valid current index changes
        assert tab_manager.set_current_index(0) is True
        assert tab_manager.get_current_index() == 0
        
        assert tab_manager.set_current_index(2) is True
        assert tab_manager.get_current_index() == 2
        
        # Test invalid current index changes
        assert tab_manager.set_current_index(-1) is False
        assert tab_manager.set_current_index(99) is False
    
    def test_none_tab_widget_initialization(self):
        """Test initialization with None tab widget."""
        # Should not crash, but TabManager will have limited functionality
        manager = TabManager(None)
        assert manager.tab_widget is None
        assert manager.get_tab_count() == 0