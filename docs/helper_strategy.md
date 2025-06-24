# Helper Strategy

## 1. Description
Guidelines on when to factor logic into helper functions.

## 2. Usage
Use helpers from `app/ui/helpers` for repetitive layout or widget code. Business logic should remain in services within `app/core`.

## 3. Dependencies
None besides internal modules.

## 4. Warnings
Avoid overusing helpers when the logic is only used once; keep the code close to where it's needed.

## 5. Examples
```python
from app.ui.helpers.ui_helpers import create_fixed_wrapper
wrapper = create_fixed_wrapper(button, 200)
```
