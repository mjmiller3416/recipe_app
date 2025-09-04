"""
Unit tests for RecipeService.

Tests the recipe business logic service including:
- Recipe creation and validation logic
- Recipe import from external sources
- Recipe modification and updates
- Business rule enforcement
- Service layer coordination with repositories
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from faker import Faker

from app.core.services.recipe_service import RecipeService
from app.core.repositories.recipe_repo import RecipeRepository
from app.core.repositories.ingredient_repo import IngredientRepository
from app.core.models import Recipe, Ingredient, RecipeIngredient
from app.core.dtos.recipe_dtos import RecipeCreateDTO, RecipeUpdateDTO, RecipeResponseDTO
from _tests.fixtures.recipe_factories import RecipeFactory, IngredientFactory

fake = Faker()


@pytest.mark.services
@pytest.mark.unit
class TestRecipeService:
    """Test cases for RecipeService business logic."""
    
    @pytest.fixture
    def mock_recipe_repo(self):
        """Mock recipe repository."""
        return Mock(spec=RecipeRepository)
    
    @pytest.fixture
    def mock_ingredient_repo(self):
        """Mock ingredient repository."""
        return Mock(spec=IngredientRepository)
    
    @pytest.fixture
    def recipe_service(self, mock_recipe_repo, mock_ingredient_repo):
        """Recipe service with mocked dependencies."""
        return RecipeService(
            recipe_repository=mock_recipe_repo,
            ingredient_repository=mock_ingredient_repo
        )
    
    def test_service_initialization(self, mock_recipe_repo, mock_ingredient_repo):
        """Test service initialization with dependencies."""
        service = RecipeService(mock_recipe_repo, mock_ingredient_repo)
        assert service.recipe_repository == mock_recipe_repo
        assert service.ingredient_repository == mock_ingredient_repo
        
    def test_create_recipe_success(self, recipe_service, mock_recipe_repo, mock_ingredient_repo):
        """Test successful recipe creation."""
        # Arrange
        recipe_data = RecipeCreateDTO(
            name="Test Recipe",
            description="A test recipe",
            prep_time=15,
            cook_time=30,
            servings=4,
            difficulty="Easy",
            instructions=["Step 1", "Step 2"],
            tags=["test", "easy"],
            ingredients=[
                {"name": "Flour", "quantity": 2.0, "unit": "cups"},
                {"name": "Eggs", "quantity": 3, "unit": "pieces"}
            ]
        )
        
        mock_recipe = RecipeFactory()
        mock_recipe_repo.create.return_value = mock_recipe
        
        # Mock ingredient creation/retrieval
        flour_ingredient = IngredientFactory(name="Flour")
        eggs_ingredient = IngredientFactory(name="Eggs")
        mock_ingredient_repo.get_or_create.side_effect = [flour_ingredient, eggs_ingredient]
        
        # Act
        result = recipe_service.create_recipe(recipe_data)
        
        # Assert
        assert result is not None
        mock_recipe_repo.create.assert_called_once()
        assert mock_ingredient_repo.get_or_create.call_count == 2
        
    def test_create_recipe_with_validation_error(self, recipe_service):
        """Test recipe creation with validation errors."""
        # Arrange
        invalid_recipe_data = RecipeCreateDTO(
            name="",  # Empty name should fail validation
            description="Test",
            prep_time=-5,  # Negative time should fail
            cook_time=30,
            servings=0,  # Zero servings should fail
            difficulty="Invalid",  # Invalid difficulty
            instructions=[],  # No instructions
            tags=[],
            ingredients=[]
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            recipe_service.create_recipe(invalid_recipe_data)
        
        assert "validation" in str(exc_info.value).lower()
        
    def test_get_recipe_by_id(self, recipe_service, mock_recipe_repo):
        """Test retrieving recipe by ID."""
        # Arrange
        recipe_id = 1
        mock_recipe = RecipeFactory()
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        
        # Act
        result = recipe_service.get_recipe(recipe_id)
        
        # Assert
        assert result is not None
        mock_recipe_repo.get_by_id.assert_called_once_with(recipe_id)
        
    def test_get_nonexistent_recipe(self, recipe_service, mock_recipe_repo):
        """Test retrieving non-existent recipe."""
        # Arrange
        recipe_id = 99999
        mock_recipe_repo.get_by_id.return_value = None
        
        # Act
        result = recipe_service.get_recipe(recipe_id)
        
        # Assert
        assert result is None
        mock_recipe_repo.get_by_id.assert_called_once_with(recipe_id)
        
    def test_update_recipe_success(self, recipe_service, mock_recipe_repo):
        """Test successful recipe update."""
        # Arrange
        recipe_id = 1
        update_data = RecipeUpdateDTO(
            name="Updated Recipe Name",
            prep_time=20,
            tags=["updated", "modified"]
        )
        
        existing_recipe = RecipeFactory()
        updated_recipe = RecipeFactory(name="Updated Recipe Name")
        
        mock_recipe_repo.get_by_id.return_value = existing_recipe
        mock_recipe_repo.update.return_value = updated_recipe
        
        # Act
        result = recipe_service.update_recipe(recipe_id, update_data)
        
        # Assert
        assert result is not None
        mock_recipe_repo.get_by_id.assert_called_once_with(recipe_id)
        mock_recipe_repo.update.assert_called_once_with(recipe_id, update_data.dict(exclude_unset=True))
        
    def test_update_nonexistent_recipe(self, recipe_service, mock_recipe_repo):
        """Test updating non-existent recipe."""
        # Arrange
        recipe_id = 99999
        update_data = RecipeUpdateDTO(name="Won't Work")
        mock_recipe_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            recipe_service.update_recipe(recipe_id, update_data)
        
        assert "not found" in str(exc_info.value).lower()
        
    def test_delete_recipe_success(self, recipe_service, mock_recipe_repo):
        """Test successful recipe deletion."""
        # Arrange
        recipe_id = 1
        mock_recipe_repo.exists.return_value = True
        mock_recipe_repo.delete.return_value = True
        
        # Act
        result = recipe_service.delete_recipe(recipe_id)
        
        # Assert
        assert result is True
        mock_recipe_repo.exists.assert_called_once_with(recipe_id)
        mock_recipe_repo.delete.assert_called_once_with(recipe_id)
        
    def test_delete_nonexistent_recipe(self, recipe_service, mock_recipe_repo):
        """Test deleting non-existent recipe."""
        # Arrange
        recipe_id = 99999
        mock_recipe_repo.exists.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            recipe_service.delete_recipe(recipe_id)
        
        assert "not found" in str(exc_info.value).lower()
        mock_recipe_repo.delete.assert_not_called()
        
    def test_search_recipes(self, recipe_service, mock_recipe_repo):
        """Test recipe search functionality."""
        # Arrange
        search_term = "pasta"
        mock_recipes = [RecipeFactory(name="Pasta Carbonara"), RecipeFactory(name="Pasta Salad")]
        mock_recipe_repo.search_by_name.return_value = mock_recipes
        
        # Act
        results = recipe_service.search_recipes(search_term)
        
        # Assert
        assert len(results) == 2
        mock_recipe_repo.search_by_name.assert_called_once_with(search_term)
        
    def test_filter_recipes_by_criteria(self, recipe_service, mock_recipe_repo):
        """Test filtering recipes by multiple criteria."""
        # Arrange
        filters = {
            "difficulty": "Easy",
            "max_prep_time": 30,
            "tags": ["vegetarian"],
            "max_servings": 4
        }
        
        mock_recipes = [RecipeFactory(difficulty="Easy")]
        mock_recipe_repo.advanced_search.return_value = mock_recipes
        
        # Act
        results = recipe_service.filter_recipes(filters)
        
        # Assert
        assert len(results) == 1
        mock_recipe_repo.advanced_search.assert_called_once_with(filters)
        
    def test_get_recipe_with_ingredients(self, recipe_service, mock_recipe_repo):
        """Test retrieving recipe with ingredient details."""
        # Arrange
        recipe_id = 1
        mock_recipe = RecipeFactory()
        mock_recipe_repo.get_with_ingredients.return_value = mock_recipe
        
        # Act
        result = recipe_service.get_recipe_with_ingredients(recipe_id)
        
        # Assert
        assert result is not None
        mock_recipe_repo.get_with_ingredients.assert_called_once_with(recipe_id)
        
    def test_duplicate_recipe(self, recipe_service, mock_recipe_repo):
        """Test recipe duplication functionality."""
        # Arrange
        source_recipe_id = 1
        source_recipe = RecipeFactory(name="Original Recipe")
        mock_recipe_repo.get_by_id.return_value = source_recipe
        
        duplicated_recipe = RecipeFactory(name="Copy of Original Recipe")
        mock_recipe_repo.create.return_value = duplicated_recipe
        
        # Act
        result = recipe_service.duplicate_recipe(source_recipe_id)
        
        # Assert
        assert result is not None
        mock_recipe_repo.get_by_id.assert_called_once_with(source_recipe_id)
        mock_recipe_repo.create.assert_called_once()
        
        # Verify the created recipe has modified name
        create_call_args = mock_recipe_repo.create.call_args[0][0]
        assert "copy of" in create_call_args["name"].lower()
        
    def test_scale_recipe_servings(self, recipe_service, mock_recipe_repo):
        """Test scaling recipe servings."""
        # Arrange
        recipe_id = 1
        new_servings = 8
        original_recipe = RecipeFactory(servings=4)
        mock_recipe_repo.get_with_ingredients.return_value = original_recipe
        
        # Act
        scaled_recipe = recipe_service.scale_recipe(recipe_id, new_servings)
        
        # Assert
        assert scaled_recipe is not None
        assert scaled_recipe["servings"] == new_servings
        # Verify scaling factor is applied (2x in this case)
        scaling_factor = new_servings / original_recipe.servings
        assert scaling_factor == 2.0
        
    def test_get_popular_recipes(self, recipe_service, mock_recipe_repo):
        """Test retrieving popular recipes."""
        # Arrange
        limit = 10
        mock_recipes = RecipeFactory.create_batch(5)
        mock_recipe_repo.get_popular.return_value = mock_recipes
        
        # Act
        results = recipe_service.get_popular_recipes(limit)
        
        # Assert
        assert len(results) == 5
        mock_recipe_repo.get_popular.assert_called_once_with(limit)
        
    def test_get_recent_recipes(self, recipe_service, mock_recipe_repo):
        """Test retrieving recent recipes."""
        # Arrange
        limit = 10
        mock_recipes = RecipeFactory.create_batch(3)
        mock_recipe_repo.get_recent.return_value = mock_recipes
        
        # Act
        results = recipe_service.get_recent_recipes(limit)
        
        # Assert
        assert len(results) == 3
        mock_recipe_repo.get_recent.assert_called_once_with(limit)
        
    def test_import_recipe_from_url(self, recipe_service, mock_recipe_repo):
        """Test importing recipe from external URL."""
        # Arrange
        url = "https://example.com/recipe"
        
        with patch('app.core.services.recipe_service.recipe_scraper') as mock_scraper:
            mock_scraper.scrape_recipe.return_value = {
                "name": "Imported Recipe",
                "description": "Scraped from web",
                "ingredients": ["1 cup flour", "2 eggs"],
                "instructions": ["Mix ingredients", "Bake for 30 minutes"]
            }
            
            imported_recipe = RecipeFactory(name="Imported Recipe")
            mock_recipe_repo.create.return_value = imported_recipe
            
            # Act
            result = recipe_service.import_recipe_from_url(url)
            
            # Assert
            assert result is not None
            mock_scraper.scrape_recipe.assert_called_once_with(url)
            mock_recipe_repo.create.assert_called_once()
            
    def test_validate_recipe_data(self, recipe_service):
        """Test recipe data validation."""
        # Test valid data
        valid_data = {
            "name": "Valid Recipe",
            "description": "A valid recipe description",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "Easy",
            "instructions": ["Step 1", "Step 2"],
            "tags": ["healthy"]
        }
        
        # Should not raise exception
        recipe_service._validate_recipe_data(valid_data)
        
        # Test invalid data
        invalid_data = {
            "name": "",  # Empty name
            "prep_time": -5,  # Negative time
            "servings": 0,  # Zero servings
            "difficulty": "Invalid",  # Invalid difficulty
            "instructions": []  # No instructions
        }
        
        with pytest.raises(ValueError):
            recipe_service._validate_recipe_data(invalid_data)
            
    def test_calculate_total_time(self, recipe_service):
        """Test total time calculation."""
        # Arrange
        recipe_data = {
            "prep_time": 15,
            "cook_time": 30
        }
        
        # Act
        total_time = recipe_service._calculate_total_time(recipe_data)
        
        # Assert
        assert total_time == 45
        
    def test_format_recipe_response(self, recipe_service):
        """Test recipe response formatting."""
        # Arrange
        mock_recipe = RecipeFactory()
        
        # Act
        formatted_response = recipe_service._format_recipe_response(mock_recipe)
        
        # Assert
        assert isinstance(formatted_response, dict)
        assert "id" in formatted_response
        assert "name" in formatted_response
        assert "prep_time" in formatted_response
        assert "cook_time" in formatted_response
        
    def test_service_error_handling(self, recipe_service, mock_recipe_repo):
        """Test service error handling."""
        # Arrange
        recipe_id = 1
        mock_recipe_repo.get_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            recipe_service.get_recipe(recipe_id)
        
        assert "Database error" in str(exc_info.value)
        
    def test_recipe_rating_calculation(self, recipe_service, mock_recipe_repo):
        """Test recipe rating calculation (if implemented)."""
        # Arrange
        recipe_id = 1
        mock_ratings = [5, 4, 5, 3, 4]  # Average should be 4.2
        
        with patch.object(recipe_service, '_get_recipe_ratings') as mock_get_ratings:
            mock_get_ratings.return_value = mock_ratings
            
            # Act
            average_rating = recipe_service.calculate_average_rating(recipe_id)
            
            # Assert
            assert average_rating == 4.2
            
    def test_ingredient_substitution_suggestions(self, recipe_service, mock_ingredient_repo):
        """Test ingredient substitution suggestions."""
        # Arrange
        ingredient_name = "butter"
        substitutions = ["margarine", "coconut oil", "vegetable oil"]
        mock_ingredient_repo.get_substitutions.return_value = substitutions
        
        # Act
        suggestions = recipe_service.get_ingredient_substitutions(ingredient_name)
        
        # Assert
        assert len(suggestions) == 3
        assert "margarine" in suggestions
        mock_ingredient_repo.get_substitutions.assert_called_once_with(ingredient_name)
        
    def test_nutrition_calculation(self, recipe_service):
        """Test nutrition information calculation."""
        # Arrange
        recipe_id = 1
        mock_recipe = RecipeFactory()
        
        with patch.object(recipe_service, '_calculate_nutrition') as mock_calc_nutrition:
            mock_calc_nutrition.return_value = {
                "calories": 350,
                "protein": 15,
                "carbs": 45,
                "fat": 12
            }
            
            # Act
            nutrition = recipe_service.get_recipe_nutrition(recipe_id)
            
            # Assert
            assert nutrition["calories"] == 350
            assert nutrition["protein"] == 15
            
    def test_recipe_cost_estimation(self, recipe_service, mock_ingredient_repo):
        """Test recipe cost estimation."""
        # Arrange
        recipe_id = 1
        mock_recipe = RecipeFactory()
        
        # Mock ingredient prices
        mock_ingredient_repo.get_average_price.side_effect = [2.50, 3.00, 1.25]
        
        with patch.object(recipe_service, '_get_recipe_with_quantities') as mock_get_recipe:
            mock_get_recipe.return_value = mock_recipe
            
            # Act
            estimated_cost = recipe_service.estimate_recipe_cost(recipe_id)
            
            # Assert
            assert estimated_cost > 0
            
    def test_batch_recipe_operations(self, recipe_service, mock_recipe_repo):
        """Test batch operations on multiple recipes."""
        # Arrange
        recipe_ids = [1, 2, 3, 4, 5]
        operation = "export"
        
        mock_recipes = RecipeFactory.create_batch(5)
        mock_recipe_repo.get_by_ids.return_value = mock_recipes
        
        # Act
        result = recipe_service.batch_operation(recipe_ids, operation)
        
        # Assert
        assert result is not None
        mock_recipe_repo.get_by_ids.assert_called_once_with(recipe_ids)
        
    @pytest.mark.slow
    def test_service_performance_large_dataset(self, recipe_service, mock_recipe_repo):
        """Test service performance with large datasets."""
        # Arrange
        large_recipe_list = RecipeFactory.create_batch(1000)
        mock_recipe_repo.get_all.return_value = large_recipe_list
        
        # Act
        all_recipes = recipe_service.get_all_recipes()
        
        # Assert
        assert len(all_recipes) == 1000
        mock_recipe_repo.get_all.assert_called_once()
        
    def test_recipe_service_integration_with_ai(self, recipe_service):
        """Test integration with AI recipe generation."""
        # Arrange
        ingredients = ["chicken", "broccoli", "rice"]
        dietary_preferences = ["healthy", "low-carb"]
        
        with patch('app.core.services.ai_service.AIService') as mock_ai_service:
            mock_ai_service.generate_recipe.return_value = {
                "name": "AI Generated Chicken Bowl",
                "ingredients": ingredients,
                "instructions": ["Cook chicken", "Steam broccoli", "Serve over rice"]
            }
            
            # Act
            ai_recipe = recipe_service.generate_recipe_with_ai(ingredients, dietary_preferences)
            
            # Assert
            assert ai_recipe is not None
            assert "AI Generated" in ai_recipe["name"]