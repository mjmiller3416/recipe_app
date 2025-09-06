"""Integration example for TabManager utility in meal_planner.py

This example demonstrates how to refactor the meal_planner.py file to use
the new TabManager utility, eliminating repetitive tab management logic.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QTabWidget, QWidget

from _dev_tools import DebugLogger
from app.ui.utils import TabManager, TabState

class MealPlannerRefactoredExample:
    """
    Example showing how MealPlanner would be refactored to use TabManager.
    
    This eliminates the following repetitive code from the original:
    - Manual tab_map dictionary management (lines 226, 331, 458-464)
    - Complex index update logic in _delete_meal_tab() (lines 446-487)
    - Tab insertion and mapping in _add_meal_tab() (lines 330-332)
    - Manual tab selection after deletion logic (lines 447-469)
    """
    
    def __init__(self):
        # Original scattered initialization
        # self.tab_map = {}  # ELIMINATED - now handled by TabManager
        
        # Create tab widget and manager
        self.meal_tabs = self._create_meal_tabs_widget()
        self.tab_manager = TabManager(self.meal_tabs)
        
        # Connect TabManager signals for enhanced functionality
        self.tab_manager.tab_added.connect(self._on_tab_added)
        self.tab_manager.tab_removed.connect(self._on_tab_removed)
        self.tab_manager.tab_activated.connect(self._on_tab_activated)
        self.tab_manager.tab_state_changed.connect(self._on_tab_state_changed)
        
        # Register special "+" tab  
        self._setup_special_add_tab()
        
    def _create_meal_tabs_widget(self) -> QTabWidget:
        """Create and configure the meal tabs widget - unchanged."""
        tabs = QTabWidget()
        tabs.setTabsClosable(False)
        tabs.setMovable(True)
        tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Connect signals - TabManager handles currentChanged internally
        tabs.tabBarClicked.connect(self._handle_tab_click)
        tabs.customContextMenuRequested.connect(self._show_context_menu)
        
        return tabs
    
    def _setup_special_add_tab(self):
        """Setup the special '+' tab for adding new meals."""
        # Create and add the "+" tab
        self._new_meal_tab()
        
        # Register it as special so TabManager doesn't manage it
        plus_tab_index = self.meal_tabs.count() - 1
        self.tab_manager.register_special_tab(plus_tab_index)
    
    # ── REFACTORED: Simplified Tab Addition ────────────────────────────────────
    def _add_meal_tab(self, meal_id: int = None):
        """
        REFACTORED: Simplified tab addition using TabManager.
        
        Before: 16 lines of manual index management and mapping
        After: 8 lines with automatic management
        """
        # Create meal widget (unchanged)
        meal_widget_vm = MealWidgetViewModel(self.planner_service, self.recipe_service)
        widget = MealWidget(meal_widget_vm)
        
        if meal_id:
            widget.load_meal(meal_id)
        
        # Connect signals (unchanged)
        selection_handler = self._create_recipe_selection_callback(widget)
        widget.recipe_selection_requested.connect(selection_handler)
        
        # SIMPLIFIED: TabManager handles insertion index and mapping automatically
        self.tab_manager.add_tab(widget, "Custom Meal")
        # Note: TabManager automatically inserts before special tabs and sets as current
    
    # ── REFACTORED: Dramatically Simplified Tab Deletion ──────────────────────
    def _delete_meal_tab(self, tab_index: int):
        """
        REFACTORED: Dramatically simplified tab deletion using TabManager.
        
        Before: 42 lines of complex index management and mapping updates
        After: 15 lines with automatic cleanup
        """
        # Get widget and meal ID for database cleanup
        meal_widget = self.tab_manager.get_tab_widget(tab_index)
        if not meal_widget:
            return
            
        # Delete from database if saved meal (unchanged)
        meal_id = meal_widget.get_meal_id()
        if meal_id:
            if not self.planner_view_model.delete_meal_selection(meal_id):
                DebugLogger.log(f"Failed to delete meal with ID {meal_id} from database", "error")
                return
            DebugLogger.log(f"Successfully deleted saved meal with ID {meal_id}", "info")
        else:
            DebugLogger.log("Removing unsaved meal tab", "info")
        
        # SIMPLIFIED: TabManager handles all index management and selection automatically
        self.tab_manager.remove_tab(tab_index)
        # Note: TabManager automatically handles new tab selection and index updates
    
    # ── REFACTORED: Enhanced Context Menu Operations ───────────────────────────
    def _get_valid_tab_index(self, position) -> int | None:
        """
        REFACTORED: Simplified using TabManager's validation.
        
        Before: Manual validation against tab_map and special tab logic
        After: Use TabManager's built-in validation
        """
        tab_bar = self.meal_tabs.tabBar()
        tab_index = tab_bar.tabAt(position)
        
        # Use TabManager to check validity (handles special tabs automatically)
        if self.tab_manager.get_tab_widget(tab_index) is not None:
            return tab_index
        return None
    
    # ── REFACTORED: Simplified Tab State Access ────────────────────────────────
    def _get_active_meal_ids(self) -> list[int]:
        """
        REFACTORED: Simplified using TabManager registry.
        
        Before: Manual iteration over self.tab_map
        After: Use TabManager's registry
        """
        ids = []
        for widget in self.tab_manager.tab_registry.values():
            meal_id = widget.get_meal_id()
            if meal_id:
                ids.append(meal_id)
        return ids
    
    def saveMealPlan(self):
        """
        REFACTORED: Simplified using TabManager registry.
        
        Before: Manual iteration over self.tab_map
        After: Use TabManager's registry
        """
        # Save all individual meals using TabManager registry
        for widget in self.tab_manager.tab_registry.values():
            widget.save_meal()
        
        # Save meal plan with collected IDs
        saved_ids = self._get_active_meal_ids()
        success = self.planner_view_model.save_meal_plan(saved_ids)
        
        if success:
            DebugLogger.log("[MealPlanner] Meal plan saved successfully", "info")
        else:
            DebugLogger.log("[MealPlanner] Failed to save meal plan", "error")
    
    # ── NEW: Enhanced Tab State Management ──────────────────────────────────────
    def _on_tab_added(self, index: int, widget: QWidget):
        """Handle tab addition events."""
        DebugLogger.log(f"Tab added at index {index}", "info")
        # Additional logic like updating UI state, notifications, etc.
    
    def _on_tab_removed(self, index: int, widget: QWidget):
        """Handle tab removal events.""" 
        DebugLogger.log(f"Tab removed from index {index}", "info")
        # Additional logic like cleanup, state updates, etc.
    
    def _on_tab_activated(self, index: int, widget: QWidget):
        """Handle tab activation events."""
        DebugLogger.log(f"Tab activated: index {index}", "info")
        # Update meal widget state, refresh data, etc.
    
    def _on_tab_state_changed(self, index: int, state: str):
        """Handle tab state changes."""
        DebugLogger.log(f"Tab {index} state changed to {state}", "info")
        # Update UI indicators, enable/disable actions, etc.
    
    # ── NEW: Enhanced Tab Operations ────────────────────────────────────────────
    def mark_tab_modified(self, index: int):
        """Mark a tab as having unsaved changes."""
        self.tab_manager.set_tab_state(index, TabState.MODIFIED)
        # Could update tab title to show * indicator
        
    def mark_tab_loading(self, index: int):
        """Mark a tab as loading data."""
        self.tab_manager.set_tab_state(index, TabState.LOADING)
        # Could show loading indicator in tab
        
    def update_tab_title_with_meal_name(self, index: int, meal_name: str):
        """Update tab title with actual meal name."""
        self.tab_manager.set_tab_title(index, meal_name)
        
    # ── Unchanged Methods ───────────────────────────────────────────────────────
    # These methods remain the same but now work with TabManager:
    
    def _handle_tab_click(self, index: int):
        """Handle when the '+' tab is clicked - unchanged logic."""
        if index == self.meal_tabs.count() - 1:  # Still works with special tab
            self._add_meal_tab()
    
    def _new_meal_tab(self):
        """Add the '+' tab - unchanged."""
        # ... same implementation as before
        pass
        
    def _show_context_menu(self, position):
        """Show context menu - unchanged.""" 
        # ... same implementation as before
        pass


# ── Integration Benefits Summary ────────────────────────────────────────────────

"""
BENEFITS OF TABMANAGER INTEGRATION:

1. **Code Reduction**: 
   - Eliminates ~60 lines of repetitive tab management code
   - Reduces _delete_meal_tab() from 42 lines to 15 lines
   - Simplifies _add_meal_tab() from 16 lines to 8 lines

2. **Automatic Index Management**:
   - No more manual tab_map dictionary management
   - Automatic index updates after tab operations  
   - Built-in special tab support (+ tab)

3. **Enhanced State Tracking**:
   - Tab state enumeration (ACTIVE, MODIFIED, LOADING, ERROR)
   - Signal emissions for state changes
   - Centralized tab registry access

4. **Error Prevention**:
   - Built-in validation for tab operations
   - Automatic handling of edge cases
   - Consistent behavior across operations

5. **Future Extensibility**:
   - Easy to add new tab states and behaviors
   - Reusable across other tabbed interfaces
   - Signal-based architecture for loose coupling

6. **Maintainability**:
   - Single source of truth for tab management
   - Consistent API across all tab operations
   - Better separation of concerns
"""