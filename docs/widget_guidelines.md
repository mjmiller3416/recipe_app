# Widget Guidelines

## 1. Description
Common rules for creating reusable widgets in the UI layer.

## 2. Usage
- Prefer composition of smaller widgets over large monolithic ones.
- Recipe cards, meal planner tabs and shopping lists follow the pattern of emitting validated data via signals.
- Layout helpers in `app/ui/helpers` can be used to keep code concise.

## 3. Dependencies
- PySide6 widgets
- Internal helper utilities

## 4. Warnings
Signals should carry DTOs or simple types to avoid tight coupling between widgets and services.

## 5. Examples
```python
from app.ui.components.recipe_card import RecipeCard
card = RecipeCard()
card.recipe_selected.connect(handle)
```
