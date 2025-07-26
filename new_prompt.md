# Project Brief: PySide6 ThemeManager Test Application

Your goal is to build a modern, multi-page PySide6 application to serve as a comprehensive testbed for our ThemeManager.

The application should simulate a real-world program, like a recipe manager or a settings dashboard, featuring a rich user interface with sidebar navigation. This will allow us to thoroughly test theme application across a wide variety of standard and custom widgets, icons, and interactive elements.

## Core Requirements

Your application must include the following features:

### 1. Main Structure & Navigation

- **Sidebar Navigation**: A main navigation panel on the left to switch between different pages. Use our custom icons for navigation items.
- **Multiple Pages/Views**: At least three distinct pages accessible from the sidebar (e.g., a Dashboard, a Data View page, and Settings).
- **Status Bar**: A simple status bar at the bottom to display dynamic information or icons (e.g., WIFI, BATTERY).

### 2. Theme Management & Controls

Create a dedicated Settings page for all theme and application customizations.

- **Mode Switch**: Implement a control (e.g., QComboBox or custom toggle) to switch between Light and Dark modes (`Mode.LIGHT`, `Mode.DARK`).
- **Color Selection**: Provide a control to select a primary theme color from the Color enum.
- **Live Updates**: Theme changes must apply instantly across the entire application without requiring a restart.
- **State Persistence**: The application must save the user's last selected theme (both mode and color) and automatically apply it on the next launch. Use QSettings for this purpose.

### 3. Widget & View Showcase

To ensure comprehensive theme testing, populate your pages with a diverse set of UI elements:

**Standard Widgets**: Include a representative sample of standard Qt widgets:
- `QLabel`, `QLineEdit`, `QTextEdit`
- `QPushButton` (standard), `QCheckBox`, `QRadioButton`
- `QComboBox`, `QSpinBox`, `QSlider`
- `QProgressBar`, `QTabWidget`

**Complex Data View**: Use a `QTreeView` to display nested, hierarchical data. This is crucial for testing how themes apply to more complex item views.

**Custom-Drawn Widget**: Include at least one custom-drawn widget (e.g., a circular progress bar or a simple graph). This widget must manually pull colors from the ThemeManager and correctly repaint itself when the theme changes, demonstrating deep integration.

### 4. User Experience & Interactivity

- **Dialog Testing**: Implement a button that launches a `QMessageBox` or a custom `QDialog`. Use this to test theme inheritance and styling on pop-up windows. Display INFO, WARNING, or ERROR icons within these dialogs.
- **UI Animations**: Incorporate subtle animations using `QPropertyAnimation` for a smoother user experience. For example, animate the transition between pages with a fade or slide effect.

### 5. Custom Component Integration

- Use the provided custom `Button` and `ToolButton` classes extensively throughout the application.
- Demonstrate different button `Type` enums (`PRIMARY`, `SECONDARY`, `DEFAULT`) to test their unique styles and states.
- Integrate `Icon` widgets both as standalone elements and within buttons. Use a variety of icons from the `Name` enum across all pages to test their appearance with different themes.

## Implementation Guide

Use the following components and patterns to build the application.

### Required Imports

Ensure these imports are at the top of your relevant files. Assume they will always be available.

```python
from app.theme_manager.icon import Icon, Name
from app.theme_manager.theme import Color, Mode, Theme
from app.ui.components.widgets import Button, ToolButton, Type
```

### Initializing the Theme

In your main entry point, load the saved theme or set an initial default before showing the main window.

```python
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example: Load saved theme or set a default
    # You will need to implement the settings logic
    settings = QSettings("YourCompany", "YourApp")
    color_name = settings.value("theme_color", Color.GREEN.name)
    mode_name = settings.value("theme_mode", Mode.DARK.name)
    Theme.setTheme(Color[color_name], Mode[mode_name])

    window = YourMainWindow()
    window.show()
    sys.exit(app.exec())
```

### Applying Theme Changes

Connect your UI controls to a function that dynamically updates the theme and saves the choice.

```python
def apply_theme_changes(self):
    """Updates the application theme and saves the selection."""
    selected_color = self.color_combo.currentData()
    selected_mode = self.mode_combo.currentData()

    if selected_color and selected_mode:
        try:
            Theme.setTheme(selected_color, selected_mode)
            # Save the new settings
            settings = QSettings("YourCompany", "YourApp")
            settings.setValue("theme_color", selected_color.name)
            settings.setValue("theme_mode", selected_mode.name)
        except Exception as e:
            print(f"Error applying theme: {e}")
```

### Using Custom Icons & Buttons

**Icons**: Create an icon using `my_icon = Icon(Name.DASHBOARD)`. To use a non-default size, call `my_icon.setIconSize(width, height)`.

**Buttons**: Instantiate buttons with a type and set their icon.

```python
# A primary action button
save_button = Button(Type.PRIMARY, "Save Changes")
save_button.setIcon(Name.SUCCESS)

# A simple tool button for a toolbar
edit_button = ToolButton(Type.TOOL)
edit_button.setIcon(Name.EDIT)
```

## Best Practices

- **Code Quality**: Write clean, readable code with docstrings and comments explaining complex logic, especially around theme integration and custom drawing.
- **Signal Handling**: Use Qt's signals and slots robustly. If ThemeManager provides a themeChanged signal, connect your custom-drawn widgets to it to trigger a repaint.
- **Error Handling**: Gracefully handle potential runtime errors, such as failing to load a resource or a saved setting, and log them clearly.
