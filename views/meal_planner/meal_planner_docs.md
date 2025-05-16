
# 🛠️ MealPlanner Refactor Implementation Guide

This document outlines the proposed refactor plan for the MealPlanner package in the MealGenie application. It is designed to support the newly restructured database and remove legacy dependencies such as QSettings.

---

## 🧩 Goal

Refactor `meal_planner`, `planner_layout`, and `meal_helpers` to:
- Eliminate reliance on `QSettings`
- Use `MealSelection` table for persistence
- Delegate business logic to a new `meal_planner_service`
- Keep `planner_layout` purely focused on UI

---

## 📁 Refactor Overview

### 🎯 Key Files & Roles

| File                  | Role |
|-----------------------|------|
| `meal_planner.py`     | UI controller, manages tab state and user interaction |
| `planner_layout.py`   | Pure UI layout, renders RecipeWidgets for meals |
| `meal_helpers.py`     | To be deprecated / absorbed into new service |
| `meal_planner_service.py` | Handles all database logic for loading/saving/updating meals |

---

## 🔨 Implementation Steps

### Step 1: Create `meal_planner_service.py`

Move business logic from `meal_helpers.py` into service functions:

```python
def load_saved_meal_ids() -> list[int]
def get_meal_by_id(meal_id: int) -> dict[str, Optional[int]]
def save_meal(data: dict[str, Optional[int]]) -> int
def update_meal(meal_id: int, data: dict[str, Optional[int]])
def delete_meal(meal_id: int)
```

Use `MealSelection` model for all reads/writes.

---

### Step 2: Refactor `meal_planner.py`

- Replace `load_meal_plan()` and `save_all_meals()` with calls to `meal_planner_service`
- Pass raw data between `PlannerLayout` and service layer
- Maintain `tab_map` structure: `{index: {"layout": PlannerLayout, "meal_id": int}}`

Example:
```python
data = layout.get_meal_data()
meal_id = meal_planner_service.save_meal(data)
```

---

### Step 3: Simplify `planner_layout.py`

- Remove all DB interaction
- Only expose:
  - `get_meal_data()` → returns `{main, side1, side2, side3}`
  - `set_meal_data(dict)` → populates widget placeholders
- Leave actual recipe fetching to caller (optional enhancement)

---

### Step 4: Phase Out `meal_helpers.py`

- Fully deprecate QSettings
- If anything useful remains (e.g. formatters), move to `ui_helpers` or `meal_planner_service`

---

## 🔁 Long-Term Enhancements

- Add `delete_meal()` button on tabs
- Auto-generate meal names (e.g., "Ollie's Taco Night 🌮")
- Add `MealLog` creation when a meal is "completed"

---

## 📦 Outcome

The MealPlanner package will be cleaner, modular, and fully database-integrated. This sets you up for future features like:
- Scheduled meal rotation
- Cross-day meal planning
- Analytics and cook frequency tracking

---

Ready to begin scaffolding `meal_planner_service.py`?
