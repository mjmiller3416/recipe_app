# Style Guide

## 1. Description
Rules for QSS styling and theme naming.

## 2. Usage
- QSS lives in `app/style_manager/stylesheets` and is loaded via `ThemeController`.
- Theme variables are injected using placeholders like `{PRIMARY}`.
- Icons are recoloured through the IconKit utilities.

## 3. Dependencies
- PySide6

## 4. Warnings
Ensure new themes define all required keys to avoid missing colours.

## 5. Examples
```python
from app.style_manager import ThemeController
ThemeController().apply_full_theme()
```
