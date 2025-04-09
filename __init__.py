"""
Initialization file for the app package.

This package serves as the core of the Recipe App, managing application logic, 
database interactions, UI components, and custom widgets.
"""

# Import main application components
from .application import Application

# Import database instance
import database
DB_INSTANCE = database.DB_INSTANCE

# Import widgets
from .widgets.ingredient_widget import IngredientWidget
from .widgets.combobox import CustomComboBox

