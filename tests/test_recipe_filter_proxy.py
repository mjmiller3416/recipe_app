from datetime import datetime, timedelta

from PySide6.QtCore import QSize


class DummyRecipe:
    def __init__(
        self,
        recipe_id: int,
        name: str,
        category: str = "All",
        created_at: datetime | None = None,
        total_time: int = 30,
        servings: int = 4,
        is_favorite: bool = False,
    ):
        self.id = recipe_id
        self.recipe_name = name
        self.recipe_category = category
        self.created_at = created_at or datetime.now()
        self.total_time = total_time
        self.servings = servings
        self.is_favorite = is_favorite
        self.reference_image_path = None

    def formatted_servings(self) -> str:
        return str(self.servings)

    def formatted_time(self) -> str:
        return f"{self.total_time}m"


def _build_proxy(recipes: list[DummyRecipe], recipe_models) -> tuple:
    RecipeListModel = recipe_models.RecipeListModel
    RecipeFilterProxyModel = recipe_models.RecipeFilterProxyModel

    model = RecipeListModel(image_size=QSize(16, 16))
    model.load_recipes(recipes)
    proxy = RecipeFilterProxyModel()
    proxy.setSourceModel(model)
    return model, proxy


def _titles(proxy) -> list[str]:
    return [
        proxy.index(row, 0).data(proxy.sourceModel().TITLE_ROLE)
        for row in range(proxy.rowCount())
    ]


def test_category_and_favorites_filter(recipe_models):
    recipes = [
        DummyRecipe(1, "Beef Chili", category="Ground Beef", is_favorite=False),
        DummyRecipe(2, "Chicken Soup", category="Chicken", is_favorite=True),
        DummyRecipe(3, "Beef Tacos", category="Ground Beef", is_favorite=True),
    ]
    _, proxy = _build_proxy(recipes, recipe_models)

    proxy.set_category_filter("Ground Beef")
    assert proxy.rowCount() == 2

    proxy.set_favorites_only(True)
    assert proxy.rowCount() == 1
    assert _titles(proxy) == ["Beef Tacos"]

    proxy.set_category_filter(None)
    proxy.set_favorites_only(False)
    assert proxy.rowCount() == 3


def test_sort_modes(recipe_models):
    base_date = datetime(2024, 1, 1)
    recipes = [
        DummyRecipe(1, "Curry", servings=6, total_time=50, created_at=base_date + timedelta(days=1)),
        DummyRecipe(2, "Apple Pie", servings=4, total_time=90, created_at=base_date + timedelta(days=2)),
        DummyRecipe(3, "Brownies", servings=12, total_time=30, created_at=base_date),
    ]
    _, proxy = _build_proxy(recipes, recipe_models)

    proxy.set_sort_mode("A-Z")
    proxy.sort(0)
    assert _titles(proxy) == ["Apple Pie", "Brownies", "Curry"]

    proxy.set_sort_mode("Z-A")
    proxy.sort(0)
    assert _titles(proxy) == ["Curry", "Brownies", "Apple Pie"]

    proxy.set_sort_mode("Most Servings")
    proxy.sort(0)
    assert _titles(proxy)[0] == "Brownies"

    proxy.set_sort_mode("Shortest Time")
    proxy.sort(0)
    assert _titles(proxy)[0] == "Brownies"

    proxy.set_sort_mode("Newest")
    proxy.sort(0)
    assert _titles(proxy)[0] == "Apple Pie"
