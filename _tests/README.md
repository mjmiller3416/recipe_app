# MealGenie Test Suite

Comprehensive test suite for the MealGenie recipe management application, built with pytest, pytest-qt, factory-boy, and faker.

## 📋 Overview

This test suite provides complete coverage of the MealGenie application across all layers:

- **Models**: SQLAlchemy ORM model testing
- **Repositories**: Data access layer testing
- **Services**: Business logic layer testing  
- **UI Components**: PySide6 widget testing with pytest-qt
- **Integration**: End-to-end workflow testing
- **Performance**: Load and stress testing

## 🏗️ Architecture

```
_tests/
├── conftest.py                 # Global pytest configuration and fixtures
├── pytest.ini                 # Pytest configuration file
├── fixtures/
│   ├── recipe_factories.py    # Factory-boy factories for all models
│   ├── database_fixtures.py   # Database setup and teardown fixtures
│   └── ui_test_data.py        # UI testing utilities and mock data
├── unit/
│   ├── core/
│   │   ├── models/            # Model layer tests
│   │   ├── repositories/      # Repository layer tests
│   │   ├── services/          # Service layer tests
│   │   └── utils/             # Utility function tests
│   └── ui/
│       ├── components/        # UI component tests
│       ├── view_models/       # ViewModel tests
│       └── views/             # View tests
├── integration/               # Integration tests
└── ui/                       # UI workflow tests
```

## 🚀 Getting Started

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install pytest pytest-qt factory-boy faker
```

### Running Tests

#### Run All Tests
```bash
pytest
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only  
pytest -m integration

# UI tests only
pytest -m ui

# Model tests only
pytest -m models

# Repository tests only
pytest -m repositories

# Service tests only
pytest -m services

# Component tests only
pytest -m components
```

#### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

#### Run Slow Tests
```bash
pytest --run-slow
```

#### Skip UI Tests (for CI/CD)
```bash
pytest --no-run-ui
```

## 🏷️ Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests for isolated components
- `@pytest.mark.integration` - Integration tests between layers
- `@pytest.mark.ui` - UI tests requiring Qt application
- `@pytest.mark.slow` - Tests that take longer than normal
- `@pytest.mark.database` - Tests requiring database setup
- `@pytest.mark.models` - Model layer tests
- `@pytest.mark.repositories` - Repository layer tests
- `@pytest.mark.services` - Service layer tests
- `@pytest.mark.components` - UI component tests
- `@pytest.mark.views` - View layer tests
- `@pytest.mark.factories` - Factory-boy related tests
- `@pytest.mark.fixtures` - Tests for fixtures and test utilities

## 🧪 Test Categories

### Model Tests (`_tests/unit/core/models/`)

Tests SQLAlchemy ORM models including:
- Model creation and validation
- Relationship mappings
- Data integrity constraints
- Search and filtering capabilities
- Performance with large datasets

**Example:**
```python
def test_recipe_creation(self, db_session):
    recipe = RecipeFactory()
    db_session.add(recipe)
    db_session.commit()
    
    assert recipe.id is not None
    assert recipe.name is not None
    assert len(recipe.instructions) > 0
```

### Repository Tests (`_tests/unit/core/repositories/`)

Tests data access layer including:
- CRUD operations
- Complex queries and filtering
- Transaction handling
- Error handling and rollback
- Performance optimization

**Example:**
```python
def test_search_recipes_by_name(self, db_session):
    repo = RecipeRepository(db_session)
    recipes = [
        RecipeFactory(name="Spaghetti Carbonara"),
        RecipeFactory(name="Beef Stew"),
    ]
    db_session.add_all(recipes)
    db_session.commit()
    
    results = repo.search_by_name("spaghetti")
    assert len(results) == 1
    assert results[0].name == "Spaghetti Carbonara"
```

### Service Tests (`_tests/unit/core/services/`)

Tests business logic layer including:
- Service orchestration
- Business rule enforcement
- Data validation and transformation
- External service integration
- Error handling and recovery

**Example:**
```python
def test_create_recipe_success(self, recipe_service, mock_repo):
    recipe_data = RecipeCreateDTO(
        name="Test Recipe",
        prep_time=15,
        cook_time=30,
        servings=4
    )
    
    result = recipe_service.create_recipe(recipe_data)
    assert result is not None
    mock_repo.create.assert_called_once()
```

### UI Component Tests (`_tests/unit/ui/components/`)

Tests PySide6 UI components using pytest-qt:
- Widget initialization and rendering
- User interaction simulation
- Signal/slot connections
- Visual state changes
- Accessibility features

**Example:**
```python
def test_recipe_card_click_signal(self, qtbot, sample_recipe_data):
    card = RecipeCard(sample_recipe_data)
    qtbot.addWidget(card)
    
    with qtbot.waitSignal(card.recipe_clicked, timeout=1000) as blocker:
        qtbot.mouseClick(card, Qt.LeftButton)
    
    assert blocker.args == [1]  # Recipe ID
```

### Integration Tests (`_tests/integration/`)

Tests cross-layer functionality including:
- End-to-end workflows
- Data consistency across layers
- Performance with realistic datasets
- Error handling and recovery
- Concurrent operation simulation

**Example:**
```python
def test_complete_recipe_lifecycle(self, services):
    # Create, retrieve, update, search, delete
    recipe = recipe_service.create_recipe(recipe_data)
    retrieved = recipe_service.get_recipe(recipe.id)
    updated = recipe_service.update_recipe(recipe.id, updates)
    found = recipe_service.search_recipes("test")
    deleted = recipe_service.delete_recipe(recipe.id)
    
    assert all([recipe, retrieved, updated, found, deleted])
```

## 🏭 Factories and Test Data

### Factory-Boy Integration

The test suite uses Factory-Boy to generate realistic test data:

```python
# Create single instance
recipe = RecipeFactory()

# Create multiple instances
recipes = RecipeFactory.create_batch(10)

# Create with specific attributes
easy_recipe = RecipeFactory(difficulty="Easy", prep_time=10)

# Create with relationships
recipe_with_ingredients = RecipeWithIngredientsFactory()
```

### Available Factories

- `RecipeFactory` - Basic recipe creation
- `IngredientFactory` - Ingredient creation with categories
- `RecipeIngredientFactory` - Recipe-ingredient relationships
- `MealSelectionFactory` - Meal planning entries
- `ShoppingItemFactory` - Shopping list items
- `RecipeWithIngredientsFactory` - Recipes with associated ingredients
- `WeeklyMealPlanFactory` - Complete weekly meal plans

### Specialized Factories

- `QuickRecipeFactory` - Easy, quick recipes
- `ComplexRecipeFactory` - Hard, time-intensive recipes
- `VeganRecipeFactory` - Plant-based recipes

### Traits and Configurations

```python
# Use traits for common scenarios
vegetarian_recipe = RecipeFactory(**RecipeTraits.vegetarian())
quick_meal = RecipeFactory(**RecipeTraits.quick_meal())

# Create sample database
sample_data = create_sample_database(
    session, 
    num_recipes=100, 
    num_ingredients=50
)
```

## 🔧 Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = _tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --verbose
    --tb=short
    --color=yes
markers =
    unit: Unit tests
    integration: Integration tests
    ui: UI tests
    slow: Slow tests
    # ... more markers
```

### Global Fixtures (`conftest.py`)

Key fixtures available in all tests:

- `db_session` - Database session with automatic rollback
- `test_db_engine` - In-memory SQLite engine
- `qapp` - QApplication for UI tests
- `faker_instance` - Seeded faker for reproducible data
- `repositories` - Repository instances
- `services` - Service instances with mocked dependencies
- `temp_dir` - Temporary directory for file tests

## 📊 Test Coverage

### Running Coverage Analysis

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

- **Models**: 95%+ coverage
- **Repositories**: 90%+ coverage  
- **Services**: 85%+ coverage
- **UI Components**: 80%+ coverage
- **Integration**: 70%+ coverage

## 🚦 Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=app --no-run-ui
```

## 🔍 Debugging Tests

### Running Individual Tests

```bash
# Run specific test file
pytest _tests/unit/core/models/test_recipe.py

# Run specific test class
pytest _tests/unit/core/models/test_recipe.py::TestRecipeModel

# Run specific test method
pytest _tests/unit/core/models/test_recipe.py::TestRecipeModel::test_recipe_creation

# Run with verbose output
pytest -v -s _tests/unit/core/models/test_recipe.py::TestRecipeModel::test_recipe_creation
```

### Debugging UI Tests

```bash
# Keep Qt widgets open for inspection
pytest --qt-keep-widgets-open

# Show Qt widget tree
pytest --qt-show-widget-tree
```

### Using Debugger

```python
def test_debug_example(self):
    import pdb; pdb.set_trace()  # Breakpoint
    # Test code here
```

## 📈 Performance Testing

### Slow Test Markers

Tests marked with `@pytest.mark.slow` test performance with large datasets:

```python
@pytest.mark.slow
def test_performance_large_dataset(self, db_session):
    # Create 1000 recipes
    recipes = RecipeFactory.create_batch(1000)
    # Test search performance
    results = repo.search_by_name("test")
    assert len(results) > 0
```

### Running Performance Tests

```bash
# Run only slow tests
pytest -m slow

# Run with timing
pytest --durations=10
```

## 🛠️ Best Practices

### Writing Effective Tests

1. **Use descriptive test names**:
   ```python
   def test_recipe_creation_with_valid_data_succeeds(self):
       # Clear what the test does
   ```

2. **Follow AAA pattern** (Arrange, Act, Assert):
   ```python
   def test_example(self):
       # Arrange
       recipe = RecipeFactory()
       
       # Act  
       result = service.process_recipe(recipe)
       
       # Assert
       assert result.is_valid
   ```

3. **Use factories for test data**:
   ```python
   # Good
   recipe = RecipeFactory(difficulty="Easy")
   
   # Avoid
   recipe = Recipe(name="Test", difficulty="Easy", ...)
   ```

4. **Mock external dependencies**:
   ```python
   @patch('app.external.service.api_call')
   def test_with_mocked_api(self, mock_api):
       mock_api.return_value = {"status": "success"}
       # Test code
   ```

5. **Test both success and failure cases**:
   ```python
   def test_create_recipe_success(self):
       # Test successful creation
   
   def test_create_recipe_validation_error(self):
       # Test validation failure
   ```

### UI Testing Best Practices

1. **Use qtbot for widget management**:
   ```python
   def test_widget(self, qtbot):
       widget = MyWidget()
       qtbot.addWidget(widget)  # Automatic cleanup
   ```

2. **Wait for signals**:
   ```python
   with qtbot.waitSignal(widget.clicked, timeout=1000):
       qtbot.mouseClick(widget, Qt.LeftButton)
   ```

3. **Test user interactions**:
   ```python
   qtbot.keyClick(widget, Qt.Key_Return)
   qtbot.mouseClick(button, Qt.LeftButton)
   ```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [PySide6 Testing Guide](https://doc.qt.io/qtforpython/overviews/qttest-overview.html)

## 🤝 Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate pytest markers
3. Use factories for test data generation
4. Include both positive and negative test cases
5. Mock external dependencies appropriately
6. Update this documentation if adding new test categories

## 🐛 Troubleshooting

### Common Issues

1. **Qt Application not available**:
   ```python
   # Ensure qapp fixture is used
   def test_ui_component(self, qtbot, qapp):
       # Test code
   ```

2. **Database session issues**:
   ```python
   # Use db_session fixture, not direct session creation
   def test_model(self, db_session):
       # Test code
   ```

3. **Factory import errors**:
   ```python
   # Import from fixtures module
   from _tests.fixtures.recipe_factories import RecipeFactory
   ```

4. **Signal timeout errors**:
   ```python
   # Increase timeout for slow operations
   with qtbot.waitSignal(signal, timeout=5000):
       # Trigger signal
   ```

For additional help, check the test output logs and ensure all dependencies are properly installed.