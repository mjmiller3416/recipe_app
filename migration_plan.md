# SQLAlchemy 2.0 Migration Plan

This document provides a comprehensive, step-by-step guide for migrating the application's data layer from a legacy data access solution to the modern SQLAlchemy 2.0 ORM. This plan emphasizes the use of 2.0-style, fully-typed model definitions to improve code clarity, maintainability, and type safety.

## Phase 1: SQLAlchemy Core Setup

**Goal:** Establish the foundational, reusable components for the SQLAlchemy 2.0 implementation.

### Create Declarative Base

The first step is to create a central declarative base class. All ORM models will inherit from this class, which allows SQLAlchemy's declarative system to register the models and their associated table metadata. Create a new file: `app/core/data/sqlalchemy_base.py`.

```python
# File: app/core/data/sqlalchemy_base.py
# File: app/core/data/sqlalchemy_base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func
import datetime

class Base(DeclarativeBase):
    """
    The base class for all SQLAlchemy ORM models.

    This class provides a central point for metadata collection and can be
    used to define shared columns or table arguments. Using `DeclarativeBase`
    is the modern approach for SQLAlchemy 2.0, enabling better type checking.
    """
    # Example of a shared column that could be added to all tables:
    # created_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )
    pass
```

By using `class Base(DeclarativeBase):`, we leverage the modern, typed system of SQLAlchemy 2.0, which integrates seamlessly with static analysis tools like Mypy.

## Phase 2: Update Core Models and Relationships (SQLAlchemy 2.0 Syntax)

**Goal:** Refactor all existing data models to use the SQLAlchemy 2.0 ORM syntax with full type annotations and define the relationships between them.

### Refactor Recipe, Ingredient, and RecipeIngredient

Convert the primary models to fully-typed SQLAlchemy 2.0 ORM classes. This involves using `Mapped` to declare typed attributes and `mapped_column` to configure the underlying database column.

- **Recipe** (`app/core/models/recipe.py`): Inherit from Base, define `__tablename__`, and convert all fields to `Mapped` columns with appropriate SQL types.

- **Ingredient** (`app/core/models/ingredient.py`): Create the Ingredient model with `id`, `name`, and `category`, ensuring data types are correctly mapped.

- **RecipeIngredient** (`app/core/models/recipe_ingredient.py`): This class serves as the association object for the many-to-many relationship, linking recipes and ingredients.

### Define Relationships with Mapped

Use SQLAlchemy's `relationship()` function in conjunction with the `Mapped` type hint to create clear, typed relationships. This is a significant improvement in the 2.0 style, as it makes the nature of the relationship (e.g., a list of objects) explicit.

#### Example in Recipe model:

```python
# app/core/models/recipe.py
from typing import List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.data.sqlalchemy_base import Base

class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)

    # The relationship uses Mapped[List[...]] to clearly indicate a collection.
    # The `cascade` option ensures that RecipeIngredient objects are managed
    # automatically when they are added to or removed from this collection.
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
```

#### Example in Ingredient model:

```python
# app/core/models/ingredient.py
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.data.sqlalchemy_base import Base

class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    recipes: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
```

#### Example in RecipeIngredient association object:

```python
# app/core/models/recipe_ingredient.py
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.data.sqlalchemy_base import Base

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    # Composite primary key ensures each ingredient is listed only once per recipe.
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), primary_key=True)

    # Additional attributes on the relationship, like quantity or notes
    quantity: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships back to the parent objects
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")
```

### Refactor Remaining Models

Systematically convert all other models in the `core/models` directory to the SQLAlchemy 2.0 ORM style. Pay close attention to defining foreign keys and relationships (one-to-many, one-to-one) using the same `Mapped` and `relationship` patterns.

## Phase 3: Refactor Core Services

**Goal:** Decouple business logic from data access by updating all data-handling services to operate on SQLAlchemy Session objects instead of direct database connections or legacy methods.

### Refactor RecipeService

Modify methods like `create_recipe_with_ingredients` to accept a Session object. The service will now use the session to add, modify, and delete ORM objects. The session's "Unit of Work" pattern will handle the transaction management, automatically tracking changes and committing them in a single, atomic operation.

#### Conceptual "Before vs. After" in RecipeService:

```python 
# Before: Manual data handling
def create_recipe(name, ingredient_ids):
    db_conn.execute("INSERT INTO recipes...")
    for ingredient_id in ingredient_ids:
        db_conn.execute("INSERT INTO recipe_ingredients...")
        db_conn.commit()

    # After: Using the ORM and Session (Unit of Work)
    from sqlalchemy.orm import Session
def create_recipe(db: Session, name: str, ingredients_data: list) -> Recipe:
    new_recipe = Recipe(name=name)
    for data in ingredients_data:
        # Find ingredient or create it
        ingredient = IngredientService.get_or_create(db, name=data['name'])
        Create the association object
        recipe_ingredient = RecipeIngredient(ingredient=ingredient, quantity=data['quantity'])
        new_recipe.ingredients.append(recipe_ingredient)
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe
```

### Refactor Other Services

Apply the same pattern to IngredientService, MealService, PlannerService, and ShoppingService. All database interactions must be performed through the Session object. This centralizes transaction control and makes the services easier to test, as the session can be replaced with a test session connected to an in-memory database.

## Phase 4: Implement Pytest Coverage

**Goal:** Develop a comprehensive suite of unit and integration tests for the new SQLAlchemy implementation to ensure correctness and prevent regressions.

### Create conftest.py for Test Fixtures

Set up a reusable pytest fixture that provides a clean, in-memory SQLite database session for each test function. This ensures that tests run in isolation and do not depend on an external database or interfere with each other.

```python
# File: tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.data.sqlalchemy_base import Base

# Use an in-memory SQLite database for fast, isolated testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Pytest fixture to provide a test database session.
    'scope="function"' ensures that the database is created and destroyed
    for each individual test function, guaranteeing isolation.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

### Create Model Tests

Write tests for each SQLAlchemy model to verify that instances can be created, saved to the database, and retrieved correctly. These tests confirm that the model definitions and mappings are valid.

#### Example Model Test:

```python
from tests.conftest import db_session
from app.core.models import Ingredient

def test_create_ingredient(db_session: Session):
    ingredient = Ingredient(name="Flour")
    db_session.add(ingredient)
    db_session.commit()
    assert ingredient.id is not None
    retrieved = db_session.get(Ingredient, ingredient.id)
    assert retrieved.name == "Flour"
```

### Create Service Tests

Write tests for the business logic within each service. These tests will use the `db_session` fixture to simulate a real database environment, allowing you to verify that services correctly manipulate data according to application rules.

## Phase 5: Set Up Alembic and Generate Initial Migration

**Goal:** Configure the Alembic database migration tool to manage schema changes and generate the initial migration script based on the new 2.0 models.

### Configure Alembic (alembic.ini and env.py)

Create the `alembic.ini` configuration file in the project root. In the `app/core/data/migrations/env.py` script, it is critical to point Alembic to the metadata object of your Base class. This is how Alembic discovers your models to compare them against the database schema.

```python
# In app/core/data/migrations/env.py
# Add your models' Base object to the target metadata
from app.core.data.sqlalchemy_base import Base
target_metadata = Base.metadata

# Also ensure all models are imported so they are registered with the metadata
# from app.core import models
```

### Generate Initial Migration Script

Use Alembic's autogenerate command to create the first migration. Alembic will inspect your models and generate a Python script that contains the necessary `op.create_table()` calls to build the schema from scratch.

```bash
alembic revision --autogenerate -m "Initial migration with SQLAlchemy 2.0 models"
```

### Review and Apply Initial Migration

Crucially, always review the autogenerated script. While powerful, autogenerate may not always capture complex constraints or custom types perfectly. Once you have verified the script is correct, apply it to your development database to create the new schema.

```bash
alembic upgrade head
```

## Phase 6: Data Migration

**Goal:** Carefully migrate all existing data from the old database into the new, SQLAlchemy-managed database schema.

### Create a Robust Data Migration Script

Write a standalone Python script that connects to both the old and new databases. This script will read data in batches from the old source, transform it to fit the new SQLAlchemy model structures, and use a SQLAlchemy session to insert it into the new database.

#### Conceptual Example with Relationship Handling:

```python 
from app.core.models import Recipe, Ingredient, RecipeIngredient
from sqlalchemy.orm import Session

# Connect to both databases
old_db_conn = ... 
new_db_engine = create_engine(...)
new_db_session = Session(new_db_engine)

# 1. Migrate independent tables first (e.g., Ingredients)
old_ingredients = get_all_ingredients_from_old_db(old_db_conn)
for old_ingredient in old_ingredients:
    new_ingredient = Ingredient(**old_ingredient.dict())
    new_db_session.add(new_ingredient)
new_db_session.commit() # Commit ingredients so they get IDs

# 2. Migrate dependent tables (e.g., Recipes and their links)
old_recipes = get_all_recipes_from_old_db(old_db_conn)
for old_recipe in old_recipes:
    new_recipe = Recipe(name=old_recipe.name)
    # Look up newly created ingredients and create association objects
    for old_ingredient_link in old_recipe.ingredients:
        ingredient = new_db_session.execute(
        select(Ingredient).where(Ingredient.name == old_ingredient_link.name)
        ).scalar_one()
        new_recipe.ingredients.append(RecipeIngredient(ingredient=ingredient, quantity=old_ingredient_link.quantity))
    new_db_session.add(new_recipe)

new_db_session.commit()
new_db_session.close()
```

### Run the Script in a Controlled Environment

Execute the migration script against a staging or backup of the production database first. For large datasets, run the script in batches and verify each batch to minimize risk and memory usage.

### Verify Data Integrity

Perform rigorous checks to ensure all data has been migrated correctly. Write queries to compare row counts, check for nulls where they shouldn't be, and validate that relationships have been re-established correctly in the new schema.

## Phase 7: Cleanup

**Goal:** Remove all obsolete code, files, and configurations related to the previous data access layer to finalize the migration and reduce technical debt.

### Remove Old Base Models and Data Utilities

Delete any old base model files (e.g., `app/core/data/base_model.py`) and any custom data access utility functions or classes that were made obsolete by the SQLAlchemy services. Use a project-wide search to hunt down any remaining usages.

### Remove Old Migration Files

If you had a previous, non-Alembic migration system (e.g., a directory of raw SQL files), archive and delete them to prevent confusion. Alembic will now be the single source of truth for schema changes.

### Clean Up Imports and Configurations

Carefully review all refactored files and remove any unused imports related to the old data layer. Check configuration files for any database connection strings or settings that are no longer needed.

### Update Documentation

Update the project's `README.md`, architectural diagrams, and any other developer documentation to reflect the new SQLAlchemy-based data access layer. Ensure that instructions for setting up a development environment now include running Alembic migrations.