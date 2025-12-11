from PySide6.QtCore import QSize
from PySide6.QtTest import QSignalSpy


class DummyRecipe:
    def __init__(
        self,
        recipe_id: int,
        name: str,
        category: str = "All",
        total_time: int = 30,
        servings: int = 4,
        is_favorite: bool = False,
    ):
        self.id = recipe_id
        self.recipe_name = name
        self.recipe_category = category
        self.total_time = total_time
        self.servings = servings
        self.is_favorite = is_favorite
        self.reference_image_path = None

    def formatted_servings(self) -> str:
        return str(self.servings)

    def formatted_time(self) -> str:
        return f"{self.total_time}m"


def test_recipe_list_model_roles(recipe_models):
    RecipeListModel = recipe_models.RecipeListModel
    recipe = DummyRecipe(1, "Spaghetti", category="Dinner", total_time=45, servings=6, is_favorite=True)
    model = RecipeListModel(image_size=QSize(32, 32))
    model.load_recipes([recipe])

    assert model.rowCount() == 1
    index = model.index(0, 0)

    assert model.data(index, RecipeListModel.TITLE_ROLE) == "Spaghetti"
    assert model.data(index, RecipeListModel.SERVINGS_ROLE) == "6"
    assert model.data(index, RecipeListModel.TIME_ROLE) == "45m"
    assert model.data(index, RecipeListModel.FAVORITE_ROLE) is True
    assert model.data(index, RecipeListModel.CATEGORY_ROLE) == "Dinner"
    assert model.data(index, RecipeListModel.ID_ROLE) == 1
    assert model.data(index, RecipeListModel.IMAGE_ROLE) is not None


def test_set_data_toggles_favorite_and_emits(qt_app, recipe_models):
    RecipeListModel = recipe_models.RecipeListModel
    recipe = DummyRecipe(2, "Tacos", is_favorite=False)
    model = RecipeListModel(
        favorite_handler=lambda r, val: r,
        image_size=QSize(24, 24),
    )
    model.load_recipes([recipe])

    index = model.index(0, 0)
    spy = QSignalSpy(model.dataChanged)

    assert model.setData(index, True, RecipeListModel.FAVORITE_ROLE) is True
    assert recipe.is_favorite is True
    assert spy.count() == 1
