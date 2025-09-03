"""Example: Modern recipe routing with proper sub-view navigation

This demonstrates how to replace internal QStackedWidget navigation
with proper route-based sub-view navigation.
"""

from PySide6.QtWidgets import QVBoxLayout, QWidget
from app.ui.services.navigation_service import NavigableView, RouteRegistry, ViewType
from app.ui.components.composite.recipe_browser import RecipeBrowser
from _dev_tools import DebugLogger


# ── Recipe List View ────────────────────────────────────────────────────────────
@RouteRegistry.register("recipes", ViewType.MAIN, sidebar_visible=True)
class RecipesView(QWidget, NavigableView):
    """Main recipes view - shows the recipe browser."""
    
    def __init__(self, navigation_service=None, parent=None):
        QWidget.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)
        self.setObjectName("RecipesView")
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Recipe browser as embedded component
        self.recipe_browser = RecipeBrowser(parent=self, selection_mode=False)
        
        # Connect to navigate to recipe detail instead of internal switching
        self.recipe_browser.recipe_card_clicked.connect(self._navigate_to_recipe)
        
        layout.addWidget(self.recipe_browser)
    
    def _navigate_to_recipe(self, recipe):
        """Navigate to recipe detail using route system."""
        self.navigation_service.navigate_to("recipe_detail", {"id": recipe.id})
    
    def on_enter(self, params: dict):
        """Load recipes when view becomes active."""
        if not self.recipe_browser.recipes_loaded:
            self.recipe_browser.load_recipes()


# ── Recipe Detail View ─────────────────────────────────────────────────────────
@RouteRegistry.register("recipe_detail", ViewType.SUB, cache_instance=False)
class RecipeDetailView(QWidget, NavigableView):
    """Recipe detail view - shows full recipe information."""
    
    def __init__(self, navigation_service=None, parent=None):
        QWidget.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)
        self.setObjectName("RecipeDetailView") 
        self.current_recipe = None
        self._build_ui()
        
    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        # Will be populated when recipe loads
        
    def on_enter(self, params: dict):
        """Load recipe when route parameters change."""
        recipe_id = params.get('id')
        if recipe_id:
            self.load_recipe(recipe_id)
            
    def load_recipe(self, recipe_id: str):
        """Load and display the specified recipe."""
        # Import here to avoid circular imports
        from app.ui.views.full_recipe import FullRecipe
        from app.core.services.recipe_service import RecipeService
        
        try:
            # Load recipe data
            recipe_service = RecipeService()
            recipe = recipe_service.get_by_id(int(recipe_id))
            
            if recipe:
                # Clear existing content
                while self.layout.count():
                    child = self.layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
                # Create full recipe view
                self.full_recipe = FullRecipe(recipe, parent=self)
                
                # Connect back navigation to use route system
                if hasattr(self.full_recipe, 'back_clicked'):
                    self.full_recipe.back_clicked.connect(lambda: self.navigation_service.go_back())
                
                self.layout.addWidget(self.full_recipe)
                self.current_recipe = recipe
                
                DebugLogger.log(f"Loaded recipe: {recipe.recipe_name}", "info")
            else:
                DebugLogger.log(f"Recipe {recipe_id} not found", "error")
                
        except Exception as e:
            DebugLogger.log(f"Error loading recipe {recipe_id}: {e}", "error")


# ── Recipe Categories View ─────────────────────────────────────────────────────
@RouteRegistry.register("recipe_category", ViewType.MAIN, sidebar_visible=False)
class RecipeCategoryView(QWidget, NavigableView):
    """Recipe category view - shows recipes filtered by category."""
    
    def __init__(self, navigation_service=None, parent=None):
        QWidget.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)
        self.setObjectName("RecipeCategoryView")
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Recipe browser with category filtering
        self.recipe_browser = RecipeBrowser(parent=self, selection_mode=False)
        self.recipe_browser.recipe_card_clicked.connect(self._navigate_to_recipe)
        
        layout.addWidget(self.recipe_browser)
    
    def on_enter(self, params: dict):
        """Filter recipes by category when route changes."""
        category = params.get('category')
        if category:
            # Set category filter
            self.recipe_browser.cb_filter.setCurrentText(category.title())
            # Update page title
            self.setWindowTitle(f"{category.title()} Recipes")
    
    def _navigate_to_recipe(self, recipe):
        """Navigate to recipe detail."""
        self.navigation_service.navigate_to("recipe_detail", {"id": recipe.id})


# ── Recipe Search Results ──────────────────────────────────────────────────────
@RouteRegistry.register("recipe_search", ViewType.MAIN, sidebar_visible=False)
class RecipeSearchView(QWidget, NavigableView):
    """Recipe search results view."""
    
    def __init__(self, navigation_service=None, parent=None):
        QWidget.__init__(self, parent)
        NavigableView.__init__(self, navigation_service, parent)
        self.setObjectName("RecipeSearchView")
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        self.recipe_browser = RecipeBrowser(parent=self, selection_mode=False)
        self.recipe_browser.recipe_card_clicked.connect(self._navigate_to_recipe)
        
        layout.addWidget(self.recipe_browser)
    
    def on_enter(self, params: dict):
        """Handle search parameters."""
        search_term = params.get('q', '')
        if search_term:
            # Implement search filtering
            self.perform_search(search_term)
            self.setWindowTitle(f"Search: {search_term}")
    
    def perform_search(self, search_term: str):
        """Perform recipe search."""
        # Implementation would filter recipes based on search term
        DebugLogger.log(f"Searching recipes for: {search_term}", "info")
    
    def _navigate_to_recipe(self, recipe):
        """Navigate to recipe detail."""
        self.navigation_service.navigate_to("recipe_detail", {"id": recipe.id})


# ── Usage Examples ─────────────────────────────────────────────────────────────
def demonstrate_navigation():
    """Examples of how to use the route-based recipe navigation."""
    # Example of how navigation would work with the new system:
    
    # Navigate to main recipes view
    # navigation_service.navigate_to("recipes")
    
    # Navigate to specific recipe with parameters
    # navigation_service.navigate_to("recipe_detail", {"id": 123})
    
    # Navigate to recipe category with parameters
    # navigation_service.navigate_to("recipe_category", {"category": "desserts"})
    
    # Navigate to search results with parameters
    # navigation_service.navigate_to("recipe_search", {"q": "chocolate"})
    
    # Navigation history works automatically:
    # User can use back button: navigation_service.go_back()
    # Each view maintains its own state through NavigableView lifecycle hooks