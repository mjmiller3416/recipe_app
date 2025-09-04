"""
Pytest configuration and shared fixtures for the MealGenie test suite.

Provides global test configuration including:
- Database setup and teardown fixtures
- Qt application initialization for UI tests
- Common test utilities and helper functions
- Shared mock objects and test data
- Test environment configuration and cleanup
- Pytest plugins and custom markers
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, Mock, patch

import factory
import pytest
from faker import Faker
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.base import Base
from app.core.database.db import DatabaseManager
from app.core.models import *
from app.core.repositories import *
from app.core.services import *


@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    """Global faker instance with seed for reproducible tests."""
    fake = Faker()
    fake.seed_instance(42)
    return fake


@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory SQLite database engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a database session for each test with automatic rollback."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_manager(test_db_engine) -> DatabaseManager:
    """Create a test database manager instance."""
    return DatabaseManager(connection_string="sqlite:///:memory:")


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Set test-friendly application properties
    app.setApplicationName("MealGenie Test")
    app.setOrganizationName("Test")
    
    yield app
    
    # Clean up any remaining widgets
    app.closeAllWindows()
    
    # Process events to ensure cleanup
    QTimer.singleShot(0, app.quit)
    app.processEvents()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def mock_image_path(temp_dir) -> Path:
    """Create a mock image file for testing."""
    image_path = temp_dir / "test_image.jpg"
    image_path.write_bytes(b"fake_image_data")
    return image_path


@pytest.fixture
def sample_recipe_data(faker_instance) -> dict[str, Any]:
    """Generate sample recipe data for testing."""
    return {
        "name": faker_instance.sentence(nb_words=3)[:-1],
        "description": faker_instance.paragraph(nb_sentences=2),
        "prep_time": faker_instance.random_int(min=5, max=60),
        "cook_time": faker_instance.random_int(min=10, max=120),
        "servings": faker_instance.random_int(min=1, max=8),
        "instructions": [faker_instance.sentence() for _ in range(3)],
        "tags": faker_instance.words(nb=3),
        "notes": faker_instance.paragraph(nb_sentences=1),
        "difficulty": faker_instance.random_element(elements=("Easy", "Medium", "Hard"))
    }


@pytest.fixture
def sample_ingredient_data(faker_instance) -> dict[str, Any]:
    """Generate sample ingredient data for testing."""
    return {
        "name": faker_instance.word(),
        "category": faker_instance.random_element(
            elements=("Vegetables", "Fruits", "Proteins", "Grains", "Dairy")
        ),
        "unit": faker_instance.random_element(elements=("cups", "tbsp", "tsp", "lbs", "oz"))
    }


@pytest.fixture
def repositories(db_session):
    """Create repository instances with test database session."""
    return {
        "recipe": RecipeRepository(db_session),
        "ingredient": IngredientRepository(db_session),
        "shopping": ShoppingRepository(db_session),
        "planner": PlannerRepository(db_session),
    }


@pytest.fixture
def services(repositories):
    """Create service instances with test repositories."""
    return {
        "recipe": RecipeService(repositories["recipe"], repositories["ingredient"]),
        "ingredient": IngredientService(repositories["ingredient"]),
        "shopping": ShoppingService(repositories["shopping"]),
        "planner": PlannerService(repositories["planner"], repositories["recipe"]),
    }


@pytest.fixture
def mock_settings():
    """Mock settings service for testing."""
    mock = Mock()
    mock.get_setting.return_value = None
    mock.set_setting.return_value = None
    mock.get_theme.return_value = "light"
    return mock


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock = Mock()
    mock.generate_recipe.return_value = {
        "name": "Test Recipe",
        "description": "A test recipe",
        "ingredients": ["1 cup test ingredient"],
        "instructions": ["Test instruction"]
    }
    return mock


# Factory setup
factory.Faker._DEFAULT_LOCALE = 'en_US'


# Utility functions for tests
def create_test_recipe(session: Session, **overrides) -> Recipe:
    """Create a test recipe with optional overrides."""
    from _tests.fixtures.recipe_factories import RecipeFactory
    return RecipeFactory.create(**overrides)


def create_test_ingredient(session: Session, **overrides) -> Ingredient:
    """Create a test ingredient with optional overrides."""
    from _tests.fixtures.recipe_factories import IngredientFactory
    return IngredientFactory.create(**overrides)


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with additional settings."""
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Disable Qt logging during tests
    os.environ['QT_LOGGING_RULES'] = '*.debug=false'


def pytest_runtest_setup(item):
    """Set up each test run."""
    # Mark slow tests
    if "slow" in item.keywords and not item.config.getoption("--run-slow", default=False):
        pytest.skip("Slow test skipped (use --run-slow to run)")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--run-ui",
        action="store_true", 
        default=True,
        help="Run UI tests (default: True)"
    )