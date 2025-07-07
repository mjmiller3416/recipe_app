"""
# Project: MealGenie (PySide6)
## Task: Resolve circular imports in custom icon module.

### Context:
I'm building a centralized icon system under `app/style_manager/icons/` to manage all icon loading, theming, and button hover effects in one self-contained package. However, circular imports are occurring between the following files:

- `icon_loader.py` (singleton theme-aware icon registry)
- `icon_factory.py` (wraps SVGLoader + uses IconLoader to recolor dynamically)
- `button_effects.py`, `icon_mixin.py` (utility layers that depend on IconFactory)
- `ThemeController` is injected into `IconLoader` in `main_window.py` at runtime

### Error:
```
ImportError: cannot import name 'IconLoader' from partially initialized module 'app.style_manager' (most likely due to a circular import)
```

### Stack:
- `icon_loader.py` imports `IconFactory`
- `icon_factory.py` imports `IconLoader`
- This chain is triggered during `main.py` boot when ThemeController and IconLoader are initialized and linked

### Constraints:
- I want to keep all icon logic within a single icon package (`style_manager/icons/`)
- I want to **avoid lazy imports** unless absolutely necessary
- I’m open to structural refactoring if it keeps things clean and self-contained

### Goal:
Refactor this icon system to eliminate circular imports while preserving:
- Runtime injection of `ThemeController` into `IconLoader`
- IconLoader being available for `IconFactory` to retrieve the palette
- A unified import tree (no scattered icon logic)

### Deliverables:
- Suggested file/module split if needed
- Clear explanation of where the circular import comes from
- Modified class or import structure to fix it
- Advice on whether `IconFactory` or `IconLoader` needs to be abstracted or decoupled
- Bonus: recommend where to initialize theme + icon system to reduce boot-time conflicts
"""Can
