"""app/ui/utils/meal_planner_config.py

Configuration constants for MealPlanner components.
Centralizes all magic numbers and configuration values used across meal planning UI.
"""

from PySide6.QtCore import QSize

class MealPlannerConfig:
    """Configuration class for meal planner constants and settings."""
    
    # Recipe slot configuration
    SIDE_SLOT_COUNT = 3
    
    # Tab management constants
    ADD_TAB_INDEX_OFFSET = 1
    MAX_TABS = 10
    
    # UI sizing constants
    TAB_ICON_SIZE = QSize(32, 32)
    LAYOUT_SPACING = 15
    
    # Tooltip messages
    ADD_TAB_TOOLTIP = "Add Meal"
    DISABLED_SIDE_SLOT_TOOLTIP = "Select a main dish first"
    
    # Tab operations
    NEW_MEAL_TAB_TITLE = "Custom Meal"
    
    # Signal blocking constants
    SIGNAL_BLOCK_TIMEOUT_MS = 100