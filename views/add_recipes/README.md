# Add Recipe Image Widget

## Overview

The `AddRecipeImage` widget provides a complete image upload functionality for the Add Recipes view. It allows users to:

- Click to browse and select image files
- Automatically copy selected images to the recipe images directory
- Display feedback about the selected image
- Clear the selected image
- Emit signals when an image is selected

## Features

### Supported Image Formats
- PNG (*.png)
- JPEG (*.jpg, *.jpeg)
- BMP (*.bmp)
- GIF (*.gif)
- TIFF (*.tiff)
- WebP (*.webp)

### Automatic File Management
- Creates the recipe images directory if it doesn't exist
- Generates unique filenames to prevent conflicts
- Copies images to `data/recipe_images/` directory
- Stores the full path for database storage

### User Interface
- Large clickable icon button (300x300px)
- Status label showing current selection
- Tooltip feedback
- Visual feedback when image is selected

## Usage

### In AddRecipes View

The widget is automatically integrated into the AddRecipes form:

```python
# Widget is created and added to the form grid
self.btn_add_image = AddRecipeImage()
form_grid.addWidget(self.btn_add_image, 0, 3, 2, 1)

# Signal connection updates the selected image path
self.btn_add_image.image_selected.connect(self._update_image_path)
```

### Signals

- `image_selected(str)`: Emitted when an image is selected, passes the full file path
- `clicked()`: Standard QToolButton clicked signal

### Methods

- `select_image()`: Opens file dialog for image selection
- `set_image(file_path)`: Sets an image programmatically
- `get_image_path()`: Returns the current selected image path
- `clear_image()`: Clears the current selection

## Integration with Recipe Saving

When a recipe is saved, the `selected_image_path` is automatically included in the recipe data:

```python
recipe_data = {
    # ... other fields
    "image_path": self.selected_image_path or ""
}
```

After successful save, the form is cleared including the image selection.

## Error Handling

The widget includes comprehensive error handling for:
- Invalid file paths
- File system errors during copying
- Missing directories
- Unsupported file formats

All errors are logged and displayed to the user via message dialogs.

## Configuration

Widget appearance is controlled by the `ADD_RECIPES` configuration in `config/config.py`:

```python
ADD_RECIPES = {
    "ADD_IMAGE": {
        "FILE_PATH": AppPaths.ICONS_DIR / "add_image.svg",
        "ICON_SIZE": QSize(300, 300),
        "DYNAMIC": THEME["ICON_STYLES"]["TOOLBUTTON"],
    },
}
```
