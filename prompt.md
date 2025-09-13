# Image/Card Widget Initialization Issues

You need to address three related initialization issues in the image/card widgets.

## Issue 1: CircularImage Border Attributes

The `CircularImage` class is missing initialization for `_border_width` and `_border_color`. These must be set in `__init__` before the properties are accessed.

### ✅ Fix:

```python
class CircularImage(BaseCard):
    def __init__(self, diameter: int = 100, parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.image_path = None
        self.pixmap = None

        # Initialize border properties early
        self._border_width = 0
        self._border_color = QColor(Qt.transparent)

        # Set widget size
        self.setFixedSize(diameter, diameter)

        # Any additional setup
        self._setup_ui()
```

## Issue 2: RoundedImage super() Call

`RoundedImage` incorrectly calls `super().__init__(size, parent)`. It should only pass `parent` to `super()`.

### ✅ Fix:

```python
class RoundedImage(BaseImage):
    """Image widget with configurable rounded corners."""

    def __init__(self, image_path: Union[str, Path, None] = None,
                 size: Union[int, QSize] = 100,
                 radii: Union[int, tuple[int, int, int, int]] = 0,
                 parent=None):
        super().__init__(parent)  # FIXED: only pass parent

        # Store size
        if isinstance(size, int):
            self.size = QSize(size, size)
        else:
            self.size = size

        self.setFixedSize(self.size)

        # Store radii
        self._radii = (radii, radii, radii, radii) if isinstance(radii, int) else radii

        # Optionally set image
        if image_path:
            self.setImagePath(image_path)
```

## Issue 3: LargeRecipeCard Initialization

Error logs still show an initialization problem in `LargeRecipeCard`. This class likely also passes extra arguments to `super().__init__()`.

### ✅ Fix Pattern:

- Only ever call `super().__init__(parent)`
- Store other arguments (size, diameter, etc.) as instance variables
- Initialize all properties that will be accessed by Qt property getters before use
