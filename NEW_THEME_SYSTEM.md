# PySide6 Demo Dashboard with Theme Integration

## Objective
Create a PySide6 demo application that acts as a showcase Dashboard UI. It should demonstrate the full range of PySide6's capabilities: modern card-based layout, animations, dark/light theme switching, and dynamic color theming.

## ✅ Core Requirements

### 🖥 Application Scope
- Single-view dashboard application (no page switching)
- Contains elevated "card-style" widgets with visual depth (drop shadows, borders, rounded corners, etc.)
- Leverages animations (e.g., fade-ins, slide-ins, hover effects)
- Includes iconography using assets stored in: `app/assets/icons/`

### 🎨 Theme Integration
Must integrate with the custom ThemeManager system located in:

```
theme_manager/
├── __init__.py
├── base_style.qss
├── IMPLEMENTATION_COMPLETE.md
├── material_colors.py
├── theme_helpers.py
└── theme_manager.py
```

- Reference and follow the documentation inside `IMPLEMENTATION_COMPLETE.md` for proper integration with this theming system
- Dynamically apply QSS using the theme variables

### ⚙️ Settings Controls
- Include a settings button (with icon) in the corner of the dashboard that opens a QDialog for theme options
- Must include a light/dark mode toggle
- Include a source color dropdown selector that applies instantly

### 📄 Stylesheets
- Include standalone `.qss` file(s) to showcase how QSS works with the ThemeManager
- Demonstrate variables being used from `material_colors.py`

## ✨ Bonus UI Enhancements (Highly Encouraged)
- Animated hover effects on buttons/cards
- Progress bars, charts, or status indicators (e.g., usage tiles)
- Responsive layout using QGridLayout or QHBoxLayout / QVBoxLayout combos
- Simulated dashboard data (hardcoded is fine)
- Theme-aware icons (light/dark mode compatible)

## 📦 Output Expectations
- Full PySide6 app in a single file OR modular folder-based structure
- Accompanying `.qss` files in a dedicated folder (e.g., `theme_manager/styles/`)
- All assets referenced properly relative to the file system

