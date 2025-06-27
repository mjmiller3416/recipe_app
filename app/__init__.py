# app/__init__.py

"""Main application package for the Meal Planner."""

__version__ = "1.0.0"
__app_name__ = "Meal Planner"


from app.core.utils import startup_timer
print(f"Initializing {__app_name__} v{__version__}")