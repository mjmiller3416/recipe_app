# Database Design

## 1. Description
SQLite is used for local storage. Models are defined with Pydantic and basic CRUD utilities live in `app/core/data`.

## 2. Usage
`init_db()` creates tables from migration scripts. Models inherit `ModelBase` for simple CRUD methods.

## 3. Dependencies
- SQLite (via `sqlite3`)
- pydantic

## 4. Warnings
Running `main.py --reset` will drop existing tables and recreate them.

## 5. Examples
```python
from app.core.data.models.recipe import Recipe
recipes = Recipe.all()
```
