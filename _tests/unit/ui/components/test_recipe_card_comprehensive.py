"""
Comprehensive UI tests for RecipeCard component using pytest-qt.

Tests the RecipeCard UI component including:
- Component initialization and rendering
- User interactions and signal emissions
- Visual state changes and updates
- Accessibility and usability features
- Integration with Qt widgets and layouts
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from faker import Faker
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from _tests.fixtures.recipe_factories import RecipeFactory
from app.core.models import Recipe
from app.ui.components.composite.recipe_card import RecipeCard

fake = Faker()


@pytest.mark.components
@pytest.mark.ui
class TestRecipeCardComponent:
    """Test cases for RecipeCard UI component."""
    
    @pytest.fixture
    def sample_recipe_data(self):
        """Sample recipe data for testing."""
        return {
            "id": 1,
            "name": "Test Pasta Recipe",
            "description": "A delicious pasta recipe for testing",
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["italian", "pasta", "quick"],
            "image_path": "/path/to/image.jpg"
        }
    
    def test_recipe_card_initialization(self, qtbot, sample_recipe_data):
        """Test recipe card initialization with data."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        assert card.recipe_data == sample_recipe_data
        assert card.recipe_id == 1
        assert card.isVisible()
        
    def test_recipe_card_display_elements(self, qtbot, sample_recipe_data):
        """Test that recipe card displays all required elements."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Find key UI elements
        title_label = card.findChild(QLabel, "recipe_title")
        description_label = card.findChild(QLabel, "recipe_description")
        
        assert title_label is not None
        assert title_label.text() == "Test Pasta Recipe"
        
        assert description_label is not None
        assert "delicious pasta recipe" in description_label.text().lower()
        
    def test_recipe_card_click_signal(self, qtbot, sample_recipe_data):
        """Test recipe card click signal emission."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Mock signal handler
        with qtbot.waitSignal(card.recipe_clicked, timeout=1000) as blocker:
            qtbot.mouseClick(card, Qt.LeftButton)
        
        # Verify signal was emitted with correct recipe ID
        assert blocker.args == [1]
        
    def test_recipe_card_hover_effects(self, qtbot, sample_recipe_data):
        """Test recipe card hover state changes."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Simulate mouse enter
        QTest.mouseMove(card)
        qtbot.wait(100)  # Allow for hover animation
        
        # Check if card has hover styling (implementation dependent)
        # This would test CSS classes or direct styling changes
        assert card.property("hovered") is True or "hover" in card.styleSheet()
        
    def test_recipe_card_context_menu(self, qtbot, sample_recipe_data):
        """Test recipe card context menu functionality."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Right-click to open context menu
        with patch.object(card, 'show_context_menu') as mock_context_menu:
            qtbot.mouseClick(card, Qt.RightButton)
            mock_context_menu.assert_called_once()
            
    def test_recipe_card_favorite_toggle(self, qtbot, sample_recipe_data):
        """Test favorite button toggle functionality."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        favorite_btn = card.findChild(QPushButton, "favorite_button")
        assert favorite_btn is not None
        
        # Test favorite toggle
        initial_state = card.is_favorited
        
        with qtbot.waitSignal(card.favorite_toggled, timeout=1000) as blocker:
            qtbot.mouseClick(favorite_btn, Qt.LeftButton)
        
        assert card.is_favorited != initial_state
        assert blocker.args == [1, card.is_favorited]
        
    def test_recipe_card_image_loading(self, qtbot, sample_recipe_data):
        """Test recipe image loading and fallback."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Test with valid image path
        assert card.image_loaded is False  # Initially not loaded
        
        # Simulate image load completion
        with patch.object(card.image_loader, 'load_image') as mock_loader:
            mock_loader.return_value = True
            card.load_recipe_image()
            
        mock_loader.assert_called_once_with(sample_recipe_data["image_path"])
        
    def test_recipe_card_with_missing_image(self, qtbot, sample_recipe_data):
        """Test recipe card behavior with missing image."""
        sample_recipe_data["image_path"] = None
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Should show default/placeholder image
        image_widget = card.findChild(QLabel, "recipe_image")
        assert image_widget is not None
        # Check for default image or placeholder
        assert image_widget.pixmap() is not None  # Should have default image
        
    def test_recipe_card_difficulty_indicator(self, qtbot, sample_recipe_data):
        """Test difficulty level visual indicator."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        difficulty_indicator = card.findChild(QLabel, "difficulty_indicator")
        assert difficulty_indicator is not None
        
        # Test different difficulty levels
        difficulties = ["Easy", "Medium", "Hard"]
        for difficulty in difficulties:
            card.update_difficulty(difficulty)
            qtbot.wait(50)  # Allow for UI update
            
            # Check visual representation (color, stars, etc.)
            assert difficulty.lower() in difficulty_indicator.styleSheet().lower() or \
                   difficulty in difficulty_indicator.text()
                   
    def test_recipe_card_time_display(self, qtbot, sample_recipe_data):
        """Test cooking time display formatting."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        time_label = card.findChild(QLabel, "time_display")
        assert time_label is not None
        
        # Should display total time (prep + cook)
        expected_total = sample_recipe_data["prep_time"] + sample_recipe_data["cook_time"]
        assert str(expected_total) in time_label.text() or \
               f"{expected_total} min" in time_label.text()
               
    def test_recipe_card_servings_display(self, qtbot, sample_recipe_data):
        """Test servings count display."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        servings_label = card.findChild(QLabel, "servings_display")
        assert servings_label is not None
        assert str(sample_recipe_data["servings"]) in servings_label.text()
        
    def test_recipe_card_tags_display(self, qtbot, sample_recipe_data):
        """Test recipe tags display."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Tags might be displayed as separate labels or in a single widget
        tags_container = card.findChild(QLabel, "tags_container") or \
                        card.findChildren(QLabel)
        
        assert tags_container is not None
        
        # Check that tags are visible somewhere
        card_text = card.get_all_text().lower()
        for tag in sample_recipe_data["tags"]:
            assert tag.lower() in card_text
            
    def test_recipe_card_accessibility(self, qtbot, sample_recipe_data):
        """Test recipe card accessibility features."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Check accessible name and description
        assert card.accessibleName() != ""
        assert card.accessibleDescription() != ""
        
        # Check keyboard navigation
        card.setFocus()
        assert card.hasFocus()
        
        # Test keyboard activation
        with qtbot.waitSignal(card.recipe_clicked, timeout=1000):
            qtbot.keyClick(card, Qt.Key_Return)
            
    def test_recipe_card_responsive_layout(self, qtbot, sample_recipe_data):
        """Test recipe card responsive layout behavior."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Test different sizes
        sizes = [(200, 150), (300, 200), (400, 250)]
        
        for width, height in sizes:
            card.resize(width, height)
            qtbot.wait(50)  # Allow for layout adjustment
            
            # Verify card adapts to size
            assert card.width() == width
            assert card.height() == height
            
            # Check that content is still visible and properly arranged
            assert card.isVisible()
            
    def test_recipe_card_selection_state(self, qtbot, sample_recipe_data):
        """Test recipe card selection state management."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Test selection
        assert card.is_selected is False
        
        card.set_selected(True)
        assert card.is_selected is True
        
        # Visual indication of selection should be present
        assert "selected" in card.styleSheet().lower() or \
               card.property("selected") is True
               
    def test_recipe_card_data_update(self, qtbot, sample_recipe_data):
        """Test recipe card data updates."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Update recipe data
        new_data = sample_recipe_data.copy()
        new_data["name"] = "Updated Recipe Name"
        new_data["difficulty"] = "Hard"
        
        card.update_recipe_data(new_data)
        
        # Verify UI reflects the updates
        title_label = card.findChild(QLabel, "recipe_title")
        assert title_label.text() == "Updated Recipe Name"
        
        difficulty_indicator = card.findChild(QLabel, "difficulty_indicator")
        assert "hard" in difficulty_indicator.text().lower() or \
               "hard" in difficulty_indicator.styleSheet().lower()
               
    def test_recipe_card_animation_states(self, qtbot, sample_recipe_data):
        """Test recipe card animation and transition states."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Test show/hide animations
        card.hide()
        assert not card.isVisible()
        
        card.show_with_animation()
        qtbot.wait(200)  # Wait for animation
        assert card.isVisible()
        
    def test_recipe_card_performance_large_content(self, qtbot):
        """Test recipe card performance with large content."""
        # Create recipe with lots of content
        large_recipe_data = {
            "id": 1,
            "name": "A" * 100,  # Very long name
            "description": "B" * 500,  # Very long description
            "prep_time": 60,
            "cook_time": 120,
            "servings": 12,
            "difficulty": "Hard",
            "tags": [f"tag{i}" for i in range(20)],  # Many tags
            "image_path": "/path/to/image.jpg"
        }
        
        # Should handle large content gracefully
        card = RecipeCard(large_recipe_data)
        qtbot.addWidget(card)
        
        assert card.isVisible()
        # Content should be truncated or scrollable
        title_label = card.findChild(QLabel, "recipe_title")
        assert title_label.text() != ""  # Should display something
        
    def test_recipe_card_error_handling(self, qtbot):
        """Test recipe card error handling with invalid data."""
        # Test with minimal/invalid data
        invalid_data = {
            "id": None,
            "name": "",
            "description": None,
            "prep_time": -1,
            "cook_time": "invalid",
            "servings": 0,
            "difficulty": "Invalid",
            "tags": None,
            "image_path": "nonexistent.jpg"
        }
        
        # Should handle gracefully without crashing
        try:
            card = RecipeCard(invalid_data)
            qtbot.addWidget(card)
            assert True  # If we get here, no crash occurred
        except Exception as e:
            pytest.fail(f"RecipeCard crashed with invalid data: {e}")
            
    def test_recipe_card_signal_connections(self, qtbot, sample_recipe_data):
        """Test recipe card signal connections and emissions."""
        card = RecipeCard(sample_recipe_data)
        qtbot.addWidget(card)
        
        # Test all custom signals exist
        assert hasattr(card, 'recipe_clicked')
        assert hasattr(card, 'favorite_toggled')
        assert hasattr(card, 'recipe_selected')
        
        # Test signal connections with mock handlers
        click_handler = Mock()
        favorite_handler = Mock()
        
        card.recipe_clicked.connect(click_handler)
        card.favorite_toggled.connect(favorite_handler)
        
        # Trigger signals
        qtbot.mouseClick(card, Qt.LeftButton)
        click_handler.assert_called_once_with(1)
        
        favorite_btn = card.findChild(QPushButton, "favorite_button")
        if favorite_btn:
            qtbot.mouseClick(favorite_btn, Qt.LeftButton)
            favorite_handler.assert_called_once()
            
    @pytest.mark.slow
    def test_recipe_card_stress_test(self, qtbot):
        """Stress test with multiple recipe cards."""
        cards = []
        
        # Create many cards
        for i in range(50):
            recipe_data = {
                "id": i,
                "name": f"Recipe {i}",
                "description": f"Description {i}",
                "prep_time": 10 + i,
                "cook_time": 20 + i,
                "servings": (i % 8) + 1,
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "tags": [f"tag{i}", f"category{i % 5}"],
                "image_path": f"/path/to/image{i}.jpg"
            }
            
            card = RecipeCard(recipe_data)
            qtbot.addWidget(card)
            cards.append(card)
            
        # Verify all cards are created and functional
        assert len(cards) == 50
        
        # Test interactions on random cards
        import random
        for _ in range(10):
            card = random.choice(cards)
            qtbot.mouseClick(card, Qt.LeftButton)
            assert card.isVisible()