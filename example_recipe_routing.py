"""Example: Modern recipe routing with proper sub-view navigation

This demonstrates how to replace internal QStackedWidget navigation
with proper route-based sub-view navigation.
"""

from PySide6.QtWidgets import QVBoxLayout
from app.ui.services.navigation_views import MainView
from app.ui.services.navigation_registry import NavigationRegistry, ViewType
from app.ui.components.composite.recipe_browser import RecipeBrowser
from _dev_tools import DebugLogger


# ── Recipe List View ────────────────────────────────────────────────────────────
@NavigationRegistry.register("/recipes", ViewType.MAIN, title="Recipes")
class RecipesView(MainView):
    """Main recipes view - shows the recipe browser."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.navigate_to(f"/recipes/detail/{recipe.id}")
    
    def after_navigate_to(self, path: str, params: dict):
        """Load recipes when view becomes active."""
        if not self.recipe_browser.recipes_loaded:
            self.recipe_browser.load_recipes()


# ── Recipe Detail View ─────────────────────────────────────────────────────────
@NavigationRegistry.register("/recipes/detail/{id}", ViewType.MAIN, title="Recipe Detail")
class RecipeDetailView(MainView):
    """Recipe detail view - shows full recipe information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeDetailView") 
        self.current_recipe = None
        self._build_ui()
        
    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        # Will be populated when recipe loads
        
    def on_route_changed(self, path: str, params: dict):
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
                    self.full_recipe.back_clicked.connect(self.go_back)
                
                self.layout.addWidget(self.full_recipe)
                self.current_recipe = recipe
                
                DebugLogger.log(f"Loaded recipe: {recipe.recipe_name}", "info")
            else:
                DebugLogger.log(f"Recipe {recipe_id} not found", "error")
                
        except Exception as e:
            DebugLogger.log(f"Error loading recipe {recipe_id}: {e}", "error")


# ── Recipe Categories View ─────────────────────────────────────────────────────
@NavigationRegistry.register("/recipes/category/{category}", ViewType.MAIN, title="Recipe Category")
class RecipeCategoryView(MainView):
    """Recipe category view - shows recipes filtered by category."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeCategoryView")
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Recipe browser with category filtering
        self.recipe_browser = RecipeBrowser(parent=self, selection_mode=False)
        self.recipe_browser.recipe_card_clicked.connect(self._navigate_to_recipe)
        
        layout.addWidget(self.recipe_browser)
    
    def on_route_changed(self, path: str, params: dict):
        """Filter recipes by category when route changes."""
        category = params.get('category')
        if category:
            # Set category filter
            self.recipe_browser.cb_filter.setCurrentText(category.title())
            # Update page title
            self.setWindowTitle(f"{category.title()} Recipes")
    
    def _navigate_to_recipe(self, recipe):
        """Navigate to recipe detail."""
        self.navigate_to(f"/recipes/detail/{recipe.id}")


# ── Recipe Search Results ──────────────────────────────────────────────────────
@NavigationRegistry.register("/recipes/search", ViewType.MAIN, title="Search Results")
class RecipeSearchView(MainView):
    """Recipe search results view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecipeSearchView")
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        self.recipe_browser = RecipeBrowser(parent=self, selection_mode=False)
        self.recipe_browser.recipe_card_clicked.connect(self._navigate_to_recipe)
        
        layout.addWidget(self.recipe_browser)
    
    def on_route_changed(self, path: str, params: dict):
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
        self.navigate_to(f"/recipes/detail/{recipe.id}")


# ── Usage Examples ─────────────────────────────────────────────────────────────
def demonstrate_navigation():
    """Examples of how to use the route-based recipe navigation."""
    from app.ui.services.navigation_service_v2 import navigate_to
    
    # Navigate to main recipes view
    navigate_to("/recipes")
    
    # Navigate to specific recipe
    navigate_to("/recipes/detail/123")
    
    # Navigate to recipe category  
    navigate_to("/recipes/category/desserts")
    
    # Navigate to search results
    navigate_to("/recipes/search", {"q": "chocolate"})
    
    # Navigation history works automatically:
    # User can use back button to go: Search → Category → Recipe List
    # Each view maintains its own state