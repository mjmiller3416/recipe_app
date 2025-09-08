#!/usr/bin/env python3
"""
Management script for MealGenie.
"""
import subprocess
import sys
from pathlib import Path


try:
    import typer
except ImportError:
    print("Error: typer is not installed. Please run: pip install typer", file=sys.stderr)
    sys.exit(1)

app = typer.Typer(help="Management script for MealGenie.")
db_app = typer.Typer(help="Database management commands.")
app.add_typer(db_app, name="db")

# Add scripts directory to path for mock data imports
sys.path.insert(0, str(Path(__file__).parent / "_scripts"))

@db_app.command("migrate")
def migrate():
    """
    Apply database migrations using Alembic.
    """
    here = Path(__file__).parent.resolve()
    alembic_ini = here / "alembic.ini"
    if not alembic_ini.exists():
        typer.echo(f"Could not find alembic.ini at {alembic_ini}", err=True)
        raise typer.Exit(code=1)
    cmd = ["alembic", "upgrade", "head", "--config", str(alembic_ini)]
    typer.echo(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error running alembic: {e}", err=True)
        raise typer.Exit(code=e.returncode)

@db_app.command("seed")
def seed_db(
    recipes: int = typer.Option(25, help="Number of mock recipes to create"),
    realistic: bool = typer.Option(True, help="Use realistic fake data (requires faker)"),
    clear_first: bool = typer.Option(False, "--clear", help="Clear existing recipes first"),
    images: bool = typer.Option(True, "--images/--no-images", help="Add random image paths from recipe_images directory (default: True)")
):
    """
    Populate database with mock recipe data for development and testing.
    """
    try:
        from _scripts.mock_data import clear_all_recipes, get_recipe_count, seed_recipes
    except ImportError as e:
        typer.echo(f"Error importing mock data module: {e}", err=True)
        typer.echo("Make sure all dependencies are installed and the database is configured.", err=True)
        raise typer.Exit(code=1)

    # Show current state
    current_count = get_recipe_count()
    typer.echo(f"Current recipes in database: {current_count}")

    # Clear existing data if requested
    if clear_first:
        if current_count > 0:
            confirm = typer.confirm(f"This will delete all {current_count} existing recipes. Continue?")
            if not confirm:
                typer.echo("Seeding cancelled.")
                return
            clear_all_recipes()
        else:
            typer.echo("No recipes to clear.")

    # Seed with new data
    images_msg = " with images" if images else ""
    typer.echo(f"Creating {recipes} mock recipes{images_msg}...")
    try:
        seed_recipes(count=recipes, realistic=realistic, use_images=images)
        new_count = get_recipe_count()
        typer.echo(f"Database now contains {new_count} recipes")
    except Exception as e:
        typer.echo(f"Error seeding database: {e}", err=True)
        raise typer.Exit(code=1)

@db_app.command("reset")
def reset_db(
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt"),
    seed_after: bool = typer.Option(False, "--seed", help="Add sample data after reset"),
    images: bool = typer.Option(False, "--images", help="Include images when seeding (only if --seed is used)")
):
    """
    Reset database to clean state (drops all recipe data).
    """
    try:
        from _scripts.mock_data import clear_all_recipes, get_recipe_count, seed_recipes
    except ImportError as e:
        typer.echo(f"Error importing mock data module: {e}", err=True)
        raise typer.Exit(code=1)

    # Check if database has any data in any table
    try:
        from app.core.database.db import DatabaseSession
        from app.core.models.ingredient import Ingredient
        from app.core.models.meal_selection import MealSelection
        from app.core.models.recipe import Recipe
        from app.core.models.recipe_history import RecipeHistory
        from app.core.models.recipe_ingredient import RecipeIngredient
        from app.core.models.saved_meal_state import SavedMealState
        from app.core.models.shopping_item import ShoppingItem
        from app.core.models.shopping_state import ShoppingState
        
        with DatabaseSession() as session:
            total_count = (
                session.query(Recipe).count() +
                session.query(Ingredient).count() +
                session.query(RecipeIngredient).count() +
                session.query(MealSelection).count() +
                session.query(RecipeHistory).count() +
                session.query(SavedMealState).count() +
                session.query(ShoppingItem).count() +
                session.query(ShoppingState).count()
            )
            current_count = session.query(Recipe).count()
            
        if total_count == 0:
            typer.echo("Database is already empty.")
            if not seed_after:
                return
    except Exception as e:
        typer.echo(f"Error checking database: {e}", err=True)
        raise typer.Exit(code=1)

    # Confirm destructive operation
    if not confirm and total_count > 0:
        proceed = typer.confirm(f"This will delete ALL database data ({current_count} recipes, {total_count} total records). Continue?")
        if not proceed:
            typer.echo("Database reset cancelled.")
            return

    # Clear the database - all tables to prevent orphaned relationships
    if total_count > 0:
        try:
            with DatabaseSession() as session:
                # Delete in order to respect foreign key constraints
                session.query(ShoppingItem).delete()
                session.query(ShoppingState).delete()
                session.query(SavedMealState).delete()
                session.query(MealSelection).delete()
                session.query(RecipeHistory).delete()
                session.query(RecipeIngredient).delete()
                session.query(Recipe).delete()
                session.query(Ingredient).delete()
                session.commit()
                
            typer.echo(f"Cleared all database tables")
        except Exception as e:
            typer.echo(f"Error clearing database: {e}", err=True)
            raise typer.Exit(code=1)

    # Optionally seed with sample data
    if seed_after:
        images_msg = " with images" if images else ""
        typer.echo(f"Adding sample data{images_msg}...")
        seed_recipes(count=10, realistic=True, use_images=images)
        new_count = get_recipe_count()
        typer.echo(f"Database reset and seeded with {new_count} sample recipes")
    else:
        typer.echo("Database reset completed - all recipes removed")

@db_app.command("status")
def db_status():
    """
    Show database status and recipe count.
    """
    try:
        from _scripts.mock_data import get_recipe_count
        count = get_recipe_count()
        typer.echo(f"Database contains {count} recipes")
    except ImportError as e:
        typer.echo(f"Error checking database: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Database connection error: {e}", err=True)
        typer.echo("Make sure the database is running and migrations are applied.", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
