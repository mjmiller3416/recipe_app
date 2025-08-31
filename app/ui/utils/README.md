# UI Utilities

Reusable helpers for **PySide6 UI construction, styling, and ergonomics**.

## Goals

- Simplify widget setup, layout management, and styling.
- Centralize QSS logic and theme-aware helpers.
- Keep **UI concerns in UI** — no domain, database, or policy logic.

## What belongs here

- Widget factories: `make_icon_button`, `spacer`, `make_label`
- Layout helpers: `vstack`, `hstack`, `clear_layout`
- QSS helpers: `apply_qss`, `theme_class`
- DPI/sizing helpers: `px`, `em`, `scale_for_dpi`
- Icon helpers: `icon`, `icon_button` **(check app\style\icon\ before adding new methods)**
- Signal helpers: `connect_safely`, `debounce_signal`

## What doesn’t belong

- Business rules or database calls
- Workflow orchestration (dialogs, navigation, saves)
- Global config reads (pass parameters instead)
- Long-lived app state

## Allowed dependencies

- `PySide6 / Qt`
- `app/ui/components/*`
- `app/style_manager/*`
- Standard library modules

## Folder structure suggestion

```
app/ui/utils/
  __init__.py
  widgets.py
  layouts.py
  qss.py
  images.py
  dpi.py
  signals.py
  shortcuts.py
  README.md
```
