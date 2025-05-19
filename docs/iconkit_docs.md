# IconKit Package Documentation

The `iconkit` package is responsible for loading, managing, and displaying themed SVG icons within the application. It provides utilities for recoloring icons based on application themes and user interactions (e.g., hover, checked states).

## Modules

### `__init__.py`

This file serves as the entry point for the `iconkit` package, exporting key classes for easy access.

- **Exports**:
    - `IconKit`: Utility for generating multiple themed QIcons.
    - `ToolButtonIcon`, `ButtonIcon`, `Icon`: Specific icon widget implementations (details should be in `icon_widgets` documentation if that file exists and is relevant).
    - `ThemedIcon`: Core class for creating individual themed icons.

### `loader.py`

Contains the `SVGLoader` class, which handles the low-level loading and processing of SVG files.

- **`SVGLoader` Class**:
    - **`load(file_path, color, size, source, as_icon)`**:
        - Loads an SVG file from `file_path`.
        - Replaces the `source` color (default: `#000`) with the specified `color`.
        - Renders the SVG to the given `size` (logical pixels).
        - Scales the icon based on the device pixel ratio (DPR) for high-DPI support.
        - Returns a `QPixmap` or `QIcon` (if `as_icon` is `True`).
        - Includes error handling for file operations, regex processing, and SVG rendering.
        - Uses `QSvgRenderer` for rendering and `QPainter` for drawing onto a `QPixmap`.

### `kit.py`

Provides the `IconKit` class, a utility for generating a set of themed icons for different states.

- **`IconKit` Class**:
    - **`make_icons(file_name, size, default_color, hover_color, checked_color, source)`**:
        - Takes an SVG `file_name` (relative to the `AppPaths.ICONS_DIR`).
        - Generates three `QIcon` instances for default, hover, and checked states using the provided colors.
        - Utilizes `SVGLoader.load` for each icon state.
        - Primarily used by hover effect handlers.

### `effects.py`

Contains the `ApplyHoverEffects` class, which dynamically changes button icons in response to hover and toggle events.

- **`ApplyHoverEffects` Class**:
    - **`recolor(button, file_name, size, variant)`**:
        - Applies dynamic icon recoloring to a `QAbstractButton` instance.
        - Loads icons for default, hover, checked, and disabled states using `ThemedIcon`.
        - Sets the button's initial icon and icon size.
        - Stores the different icon states as private attributes on the button (e.g., `button._icon_default`).
        - Overrides the button's `enterEvent` and `leaveEvent` to switch icons on hover.
        - Connects to the button's `toggled` signal to update the icon when its checked state changes.

### `themed_icon.py`

Defines the `ThemedIcon` class, a core utility for creating individual themed icons (either `QIcon` or `QPixmap`) from SVG files. It supports flexible color theming.

- **`ThemedIcon` Class**:
    - **`__init__(self, file_path, size, variant)`**:
        - `file_path`: Path to the SVG file.
        - `size`: Desired logical size of the icon.
        - `variant`: Defines the color styling. Can be:
            - A dictionary with state keys (e.g., `{"DEFAULT": "#AAA", "HOVER": "#BBB"}`).
            - A direct hex color string (e.g., `"#6AD7CA"`).
            - A string key that maps to a predefined style in `ICON_STYLES` (managed by `IconController`).
    - **`icon_for_state(self, state)`**: Returns a themed `QIcon` for a specific state (e.g., "HOVER", "CHECKED").
    - **`icon(self)`**: Returns the default themed `QIcon`.
    - **`pixmap(self)`**: Returns the default themed `QPixmap`.
    - **`resolve_color(self, state)`**: Determines the appropriate hex color string for a given state based on the `variant` and the application's theme palette (accessed via `IconController`).
    - Uses `SVGLoader.load` internally for icon creation.

### `icon_mixin.py`

Provides the `IconMixin` class, designed to be mixed into `QAbstractButton` subclasses (like `QPushButton`, `QToolButton`) to easily add themed icon functionality.

- **`IconMixin` Class**:
    - **`_init_themed_icon(self, file_name, size, variant)`**:
        - Initializes and applies a themed icon to the button instance.
        - Creates a `ThemedIcon` instance and sets the button's icon and icon size.
        - Stores icon-related information (file name, size, variant) as private attributes.
    - **`refresh_theme_icon(self, palette)`**:
        - Intended to be called when the application theme changes.
        - Refreshes the button's icon using the new `palette`. (Note: The provided code shows `self._themed_icon.refresh(palette)`, implying `ThemedIcon` might have a `refresh` method not detailed in `themed_icon.py`'s content, or this part might be a placeholder for more complex refresh logic).
    - **`refresh_theme(self, palette)`**: A wrapper for `refresh_theme_icon`, likely to ensure a consistent interface for theme updates, possibly used by `IconController`.

## Workflow

1.  **Loading SVGs (`loader.py`)**: `SVGLoader` reads SVG files, replaces specified color placeholders with new theme colors, and renders them into `QPixmap` or `QIcon` objects, handling DPI scaling.
2.  **Creating Themed Icons (`themed_icon.py`)**: `ThemedIcon` uses `SVGLoader` to generate icons. It resolves colors based on a `variant` argument, which can be a direct color, a dictionary of state-specific colors, or a named theme style. It interacts with `IconController` to access the current theme's color palette.
3.  **Generating Icon Sets (`kit.py`)**: `IconKit` simplifies creating sets of icons (default, hover, checked) for UI elements by calling `SVGLoader` multiple times with different colors.
4.  **Applying Dynamic Effects (`effects.py`)**: `ApplyHoverEffects` uses `ThemedIcon` to get all necessary icon states (default, hover, checked, disabled) and then patches a button's event handlers (`enterEvent`, `leaveEvent`) and `toggled` signal to dynamically change its displayed icon based on user interaction.
5.  **Integrating with Widgets (`icon_mixin.py`)**: `IconMixin` provides a convenient way for button widgets to incorporate `ThemedIcon` functionality, allowing them to display themed icons and refresh them when the application theme changes.

## Dependencies

-   **PySide6**: For Qt GUI elements (`QIcon`, `QPixmap`, `QSvgRenderer`, `QPainter`, `QAbstractButton`, etc.).
-   **`config.AppPaths`**: To resolve icon file paths.
-   **`core.helpers.DebugLogger`**: For logging errors and warnings.
-   **`core.controllers.icon_controller.IconController`**: To access the application's theme palette and icon styles.

## Usage Example (Conceptual)

```python
# Assuming 'my_button' is a QPushButton instance
# and 'settings.svg' is an icon file

# Using IconMixin (if the button class uses it)
# class MyCustomButton(QPushButton, IconMixin):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._init_themed_icon("settings.svg", QSize(24, 24), "primary_action")

# Direct use of ThemedIcon
from ui.iconkit import ThemedIcon
from PySide6.QtCore import QSize
from pathlib import Path

icon_path = Path("settings.svg") # Relative to icon directory
icon_size = QSize(32, 32)
settings_icon = ThemedIcon(icon_path, icon_size, variant="navigation_icon").icon()
# my_button.setIcon(settings_icon)
# my_button.setIconSize(icon_size)

# Applying hover effects
from ui.iconkit import ApplyHoverEffects
# ApplyHoverEffects.recolor(my_button, "settings.svg", icon_size, "navigation_icon")
```

This documentation provides a high-level overview of the `iconkit` package. For more detailed information on specific widget implementations like `ButtonIcon` or `ToolButtonIcon`, refer to their respective source files or documentation if available in the `icon_widgets/` subdirectory.
