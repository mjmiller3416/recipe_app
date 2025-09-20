"""app/ui/views/dashboard/dashboard.py

Dashboard view providing quick access to core features and displaying
relevant information about meal planning, recipes, and shopping lists.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from datetime import datetime, timedelta
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QSizePolicy,
                               QVBoxLayout, QWidget)

from _dev_tools import DebugLogger
from app.core.database.db import DatabaseSession
from app.core.dtos.recipe_dtos import RecipeFilterDTO
from app.core.models import Recipe
from app.core.services import PlannerService, RecipeService, ShoppingService
from app.style.icon.config import Name, Type
from app.ui.components.composite.recipe_card import (MediumRecipeCard, SmallRecipeCard,
                                                      create_recipe_card, LayoutSize)
from app.ui.components.layout.card import Card
from app.ui.components.layout.flow_layout import FlowLayoutContainer
from app.ui.components.widgets.button import Button
from app.ui.components.widgets.separator import Separator
from app.ui.utils import create_two_column_layout
from app.ui.views.base import BaseView


# ── Dashboard ────────────────────────────────────────────────────────────────────────────────
class Dashboard(BaseView):
    """Main dashboard view providing overview and quick access to features."""

    def __init__(self, parent=None, navigation_service=None):
        super().__init__(parent)

        DebugLogger.log("Initializing Dashboard page", "info")
        self.setObjectName("Dashboard")

        # Store navigation service
        self.navigation_service = navigation_service

        # Initialize services
        self.recipe_service = RecipeService()
        self.planner_service = PlannerService()
        self.shopping_service = ShoppingService()

        # Data containers
        self.meal_plan_data = []
        self.recent_recipes = []
        self.shopping_summary = None
        self.stats_data = {}

        # Build UI
        self._build_ui()

        # Load initial data
        self._load_dashboard_data()

    def _build_ui(self):
        """Build the dashboard UI layout."""
        # Quick Actions at the top
        self._create_quick_actions()

        # Add spacing
        self.content_layout.addSpacing(20)

        # Statistics cards
        self._create_stats_section()

        # Add spacing
        self.content_layout.addSpacing(20)

        # Main content area with two columns
        self._create_main_content()

        # Add spacing
        self.content_layout.addSpacing(20)

        # Recent recipes section at the bottom
        self._create_recent_recipes()

        # Add stretch to push content to top
        self.content_layout.addStretch()

    def _create_quick_actions(self):
        """Create the quick actions section with navigation buttons."""
        # Create card for quick actions
        card = Card(card_type="Primary")
        card.setHeader("Quick Actions")
        card.setSubHeader("Jump to your most used features")

        # Create button container
        button_container = QWidget()
        button_layout = QGridLayout(button_container)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(10, 10, 10, 10)

        # Plan This Week button
        btn_plan = Button(
            label="Plan This Week",
            type=Type.PRIMARY
        )
        btn_plan.setIcon(Name.MEAL_PLANNER)
        btn_plan.setIconSize(24, 24)
        btn_plan.clicked.connect(lambda: self._navigate_to("meal_planner"))
        button_layout.addWidget(btn_plan, 0, 0)

        # Add Recipe button
        btn_add = Button(
            label="Add Recipe",
            type=Type.SECONDARY
        )
        btn_add.setIcon(Name.ADD)
        btn_add.setIconSize(24, 24)
        btn_add.clicked.connect(lambda: self._navigate_to("add_recipe"))
        button_layout.addWidget(btn_add, 0, 1)

        # Shopping List button
        btn_shopping = Button(
            label="Shopping List",
            type=Type.SECONDARY
        )
        btn_shopping.setIcon(Name.SHOPPING_LIST)
        btn_shopping.setIconSize(24, 24)
        btn_shopping.clicked.connect(lambda: self._navigate_to("shopping_list"))
        button_layout.addWidget(btn_shopping, 1, 0)

        # Browse Recipes button
        btn_browse = Button(
            label="Browse Recipes",
            type=Type.SECONDARY
        )
        btn_browse.setIcon(Name.SEARCH)
        btn_browse.setIconSize(24, 24)
        btn_browse.clicked.connect(lambda: self._navigate_to("browse_recipes"))
        button_layout.addWidget(btn_browse, 1, 1)

        # Add button container to card
        card.addWidget(button_container)

        # Add card to layout
        self.content_layout.addWidget(card)

    def _create_stats_section(self):
        """Create statistics cards showing recipe collection stats."""
        # Create container for stats
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        # Total Recipes card
        total_card = self._create_stat_card(
            "Total Recipes",
            str(self.stats_data.get("total_recipes", 0)),
            Name.BROWSE_RECIPES
        )
        stats_layout.addWidget(total_card)

        # Favorites card
        fav_card = self._create_stat_card(
            "Favorites",
            str(self.stats_data.get("favorites", 0)),
            Name.FAV_FILLED
        )
        stats_layout.addWidget(fav_card)

        # This Week card
        week_card = self._create_stat_card(
            "Added This Week",
            str(self.stats_data.get("this_week", 0)),
            Name.SPARKLES_FILLED
        )
        stats_layout.addWidget(week_card)

        # Average Time card
        avg_time = self.stats_data.get("avg_time", 0)
        time_str = f"{avg_time} min" if avg_time > 0 else "N/A"
        time_card = self._create_stat_card(
            "Avg. Cook Time",
            time_str,
            Name.TOTAL_TIME
        )
        stats_layout.addWidget(time_card)

        # Add container to main layout
        self.content_layout.addWidget(stats_container)

    def _create_stat_card(self, title: str, value: str, icon: Name) -> Card:
        """Create a single statistics card."""
        card = Card(card_type="Secondary")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setFixedHeight(120)

        # Create vertical layout for content
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)

        # Title label
        title_label = QLabel(title)
        title_label.setProperty("font", "Caption")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Value label (big number)
        value_label = QLabel(value)
        value_label.setProperty("font", "Title")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)

        card.addWidget(content)
        return card

    def _create_main_content(self):
        """Create the main content area with meal plan and shopping summary."""
        # Meal Plan Preview
        meal_card = self._create_meal_plan_preview()

        # Shopping List Summary
        shopping_card = self._create_shopping_summary()

        # Create two column layout with the cards
        columns_layout = create_two_column_layout(
            left_widgets=[meal_card],
            right_widgets=[shopping_card],
            spacing=20
        )

        # Create container for the layout
        columns_container = QWidget()
        columns_container.setLayout(columns_layout)

        self.content_layout.addWidget(columns_container)

    def _create_meal_plan_preview(self) -> Card:
        """Create meal plan preview card."""
        card = Card(card_type="Primary")
        card.setHeader("This Week's Meals")
        card.setSubHeader("Your planned meals for the week")

        if not self.meal_plan_data:
            # Empty state
            empty_label = QLabel("No meals planned yet")
            empty_label.setProperty("font", "Body")
            empty_label.setAlignment(Qt.AlignCenter)
            card.addWidget(empty_label)
        else:
            # Display meal cards
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for i, recipe_id in enumerate(self.meal_plan_data[:5]):  # Show max 5
                if recipe_id:
                    recipe = self._get_recipe_by_id(recipe_id)
                    if recipe:
                        # Create container for day + recipe
                        meal_container = QWidget()
                        meal_layout = QVBoxLayout(meal_container)
                        meal_layout.setSpacing(5)

                        # Day label
                        day_label = QLabel(days[i % 7])
                        day_label.setProperty("font", "Subtitle")
                        meal_layout.addWidget(day_label)

                        # Recipe card
                        recipe_card = SmallRecipeCard()
                        recipe_card.setRecipe(recipe)
                        recipe_card.setMaximumHeight(120)
                        meal_layout.addWidget(recipe_card)

                        card.addWidget(meal_container)

                        # Add separator except for last item
                        if i < len(self.meal_plan_data) - 1 and i < 4:
                            card.addWidget(Separator())

        # Add "View Full Plan" button
        btn_view_plan = Button(
            label="View Full Plan",
            type=Type.SECONDARY
        )
        btn_view_plan.clicked.connect(lambda: self._navigate_to("meal_planner"))
        card.addWidget(btn_view_plan)

        return card

    def _create_shopping_summary(self) -> Card:
        """Create shopping list summary card."""
        card = Card(card_type="Primary")
        card.setHeader("Shopping List")
        card.setSubHeader("Items you need to buy")

        if self.shopping_summary:
            total = self.shopping_summary.get("total_items", 0)
            checked = self.shopping_summary.get("checked_items", 0)
            categories = self.shopping_summary.get("categories", [])

            if total == 0:
                # Empty state
                empty_label = QLabel("Shopping list is empty")
                empty_label.setProperty("font", "Body")
                empty_label.setAlignment(Qt.AlignCenter)
                card.addWidget(empty_label)
            else:
                # Summary info
                summary_label = QLabel(f"Total Items: {total} ({checked} checked)")
                summary_label.setProperty("font", "Subtitle")
                card.addWidget(summary_label)

                # Add separator
                card.addWidget(Separator())

                # Category breakdown (top 5)
                if categories:
                    cat_label = QLabel("By Category:")
                    cat_label.setProperty("font", "Caption")
                    card.addWidget(cat_label)

                    for cat_name, count in list(categories.items())[:5]:
                        cat_item = QLabel(f"  • {cat_name}: {count} items")
                        cat_item.setProperty("font", "Body")
                        card.addWidget(cat_item)
        else:
            # No data state
            empty_label = QLabel("Unable to load shopping list")
            empty_label.setProperty("font", "Body")
            empty_label.setAlignment(Qt.AlignCenter)
            card.addWidget(empty_label)

        # Add "View Full List" button
        btn_view_list = Button(
            label="View Full List",
            type=Type.SECONDARY
        )
        btn_view_list.clicked.connect(lambda: self._navigate_to("shopping_list"))
        card.addWidget(btn_view_list)

        return card

    def _create_recent_recipes(self):
        """Create recent recipes section."""
        card = Card(card_type="Primary")
        card.setHeader("Recent Recipes")
        card.setSubHeader("Recently added to your collection")

        if not self.recent_recipes:
            # Empty state
            empty_label = QLabel("No recipes yet. Add your first recipe to get started!")
            empty_label.setProperty("font", "Body")
            empty_label.setAlignment(Qt.AlignCenter)
            card.addWidget(empty_label)
        else:
            # Create flow layout for recipe cards
            flow_container = FlowLayoutContainer()
            flow_container.setSpacing(15)
            flow_container.setLayoutMargins(10, 10, 10, 10)

            # Add recipe cards
            for recipe in self.recent_recipes[:6]:  # Show max 6
                recipe_card = MediumRecipeCard()
                recipe_card.setRecipe(recipe)
                recipe_card.setFixedSize(280, 420)
                flow_container.addWidget(recipe_card)

            card.addWidget(flow_container)

        # Add "View All" button
        btn_view_all = Button(
            label="View All Recipes",
            type=Type.SECONDARY
        )
        btn_view_all.clicked.connect(lambda: self._navigate_to("browse_recipes"))
        card.addWidget(btn_view_all)

        self.content_layout.addWidget(card)

    def _load_dashboard_data(self):
        """Load all data needed for dashboard display."""
        try:
            with DatabaseSession() as session:
                # Initialize services with session
                recipe_service = RecipeService(session)
                planner_service = PlannerService(session)
                shopping_service = ShoppingService(session)

                # Load meal plan
                self.meal_plan_data = planner_service.load_saved_meal_ids()
                DebugLogger.log(f"Loaded {len(self.meal_plan_data)} meal IDs", "info")

                # Load recent recipes
                filter_dto = RecipeFilterDTO(
                    sort_by="created_at",
                    sort_order="desc",
                    limit=6
                )
                self.recent_recipes = recipe_service.list_filtered(filter_dto)
                DebugLogger.log(f"Loaded {len(self.recent_recipes)} recent recipes", "info")

                # Load shopping list summary
                shopping_list = shopping_service.get_shopping_list()
                if shopping_list:
                    self.shopping_summary = {
                        "total_items": shopping_list.total_items,
                        "checked_items": shopping_list.checked_items,
                        "categories": shopping_list.categories or {}
                    }

                # Calculate statistics
                self._calculate_statistics(recipe_service)

        except Exception as e:
            DebugLogger.log(f"Error loading dashboard data: {e}", "error")
            # Initialize with empty data
            self.meal_plan_data = []
            self.recent_recipes = []
            self.shopping_summary = None
            self.stats_data = {}

    def _calculate_statistics(self, recipe_service: RecipeService):
        """Calculate recipe statistics."""
        try:
            # Get all recipes
            all_recipes_dto = RecipeFilterDTO()
            all_recipes = recipe_service.list_filtered(all_recipes_dto)

            # Total recipes
            self.stats_data["total_recipes"] = len(all_recipes)

            # Favorites
            fav_dto = RecipeFilterDTO(is_favorite=True)
            favorites = recipe_service.list_filtered(fav_dto)
            self.stats_data["favorites"] = len(favorites)

            # This week's recipes
            week_ago = datetime.now() - timedelta(days=7)
            week_count = sum(1 for r in all_recipes
                           if r.created_at and r.created_at >= week_ago)
            self.stats_data["this_week"] = week_count

            # Average cooking time
            cook_times = [r.total_time for r in all_recipes if r.total_time and r.total_time > 0]
            if cook_times:
                self.stats_data["avg_time"] = int(sum(cook_times) / len(cook_times))
            else:
                self.stats_data["avg_time"] = 0

        except Exception as e:
            DebugLogger.log(f"Error calculating statistics: {e}", "error")
            self.stats_data = {
                "total_recipes": 0,
                "favorites": 0,
                "this_week": 0,
                "avg_time": 0
            }

    def _get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        try:
            with DatabaseSession() as session:
                recipe_service = RecipeService(session)
                return recipe_service.get_recipe(recipe_id)
        except Exception as e:
            DebugLogger.log(f"Error fetching recipe {recipe_id}: {e}", "error")
            return None

    def _navigate_to(self, page_name: str):
        """Navigate to a specific page."""
        if self.navigation_service:
            self.navigation_service.switch_to(page_name)
        else:
            DebugLogger.log(f"Navigation service not available for {page_name}", "warning")

    def _refresh_dashboard(self):
        """Refresh dashboard data and update UI."""
        DebugLogger.log("Refreshing dashboard data", "info")

        # Reload data
        self._load_dashboard_data()

        # Clear existing UI
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Rebuild UI with fresh data
        self._build_ui()

    def showEvent(self, event):
        """Refresh dashboard when shown."""
        super().showEvent(event)
        self._refresh_dashboard()