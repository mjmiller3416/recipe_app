# QSS Loader Refactor Plan

## Goal
Refactor the existing `StyleLoader` class to support both basic stylesheet loading and runtime variable injection using theme variables. This will improve flexibility, readability, and scalability for theme management across the application.

---

## Overview
We will split the loader functionality into two classes:

### 1. `BaseStyleLoader`
- Responsibility: Load `.qss` files from disk without modifications.
- Use case: Basic style loading when theme injection is not needed.

### 2. `ThemedStyleLoader`
- Inherits from: `BaseStyleLoader`
- Responsibility: Loads QSS files and injects `{VARIABLE}` placeholders using a `theme` dictionary.
- Use case: All runtime styling needs where centralized themes are applied (colors, fonts, etc.).

---

## Folder Structure
Place in:
```
styles/
├── theme_variables.py
├── utils/
│   ├── base_loader.py       # <- BaseStyleLoader
│   └── themed_loader.py     # <- ThemedStyleLoader
```

---

## Implementation Blueprint

### base_loader.py
```python
from pathlib import Path

class BaseStyleLoader:
    def load(self, path: str) -> str:
        with open(Path(path), "r", encoding="utf-8") as f:
            return f.read()
```

### themed_loader.py
```python
from styles.utils.base_loader import BaseStyleLoader
from styles.theme_variables import THEME

class ThemedStyleLoader(BaseStyleLoader):
    def __init__(self, theme: dict = None):
        self.theme = theme or THEME

    def load(self, path: str) -> str:
        qss = super().load(path)
        for key, value in self.theme.items():
            qss = qss.replace(f"{key}", value)
        return qss
```

---

## Future Integration Steps

1. **Update StyleManager**
   - Replace existing `StyleLoader()` with `ThemedStyleLoader()`
   - Load your themed QSS dynamically and apply to `QApplication`

2. **Theme Switching (Optional)**
   - Create multiple theme dicts (e.g., `DARK_THEME`, `LIGHT_THEME`)
   - Allow user preference or runtime switching

3. **Testing and Fallbacks**
   - Add error handling in `ThemedStyleLoader` for missing keys or malformed placeholders
   - Log any unresolved `{VAR}` markers as warnings

4. **Component-based Styling**
   - Break QSS into component files like `buttons.qss`, `inputs.qss`, etc.
   - Load them modularly depending on current UI context

---

## Final Thought
This setup gives you the best of both worlds: clean separation for low-level loading vs high-level injection, and future-proofing for dynamic theme handling.

Let this live in your roadmap until you're ready to wire it in. ✨
