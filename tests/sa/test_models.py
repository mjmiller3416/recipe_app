from sqlalchemy.orm import Session

from app.core.sa import Ingredient, Recipe, RecipeIngredient


def test_create_ingredient(db_session: Session) -> None:
    ingredient = Ingredient(name="Flour")
    db_session.add(ingredient)
    db_session.commit()

    assert ingredient.id is not None
    retrieved = db_session.get(Ingredient, ingredient.id)
    assert retrieved.name == "Flour"


def test_recipe_with_ingredient(db_session: Session) -> None:
    recipe = Recipe(name="Bread")
    ingredient = Ingredient(name="Flour")
    link = RecipeIngredient(ingredient=ingredient, recipe=recipe, quantity="1 cup")
    recipe.ingredients.append(link)

    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    assert recipe.id is not None
    assert recipe.ingredients[0].ingredient.name == "Flour"
