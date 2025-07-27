1. What Are My Styling Options?
✅ What I've Tried Before (and Why It Didn't Work)
I previously used individual stylesheets per class/widget, e.g.:

combobox.qss, view_recipes.qss, dashboard.qss, search_bar.qss

At runtime, these stylesheets were:

Compiled, combined, and applied globally.

Problems Encountered:
Style Conflicts / Overwrites:

Styles from separate QSS files often overrode each other unintentionally.

This became increasingly difficult to debug as the number of stylesheets grew.

I would frequently resort to in-line styles to force styles to apply, which created a fragmented and inconsistent styling approach.

Per-Instance Styling (Performance Bottlenecks):

I attempted to apply styles per-widget instance, thinking this would offer more precision.

However, this led to the same stylesheet being applied hundreds of times, especially in dynamically generated components like RecipeCard.

For example, in the Recipe Browser, I render over 100 recipe cards, all sharing the same visual styling.

Applying the same stylesheet 100+ times created performance issues and was clearly redundant.

These styles should only be applied once per class, not per instance.

Example:
python
Copy
Edit
frame = QFrame()
frame.setProperty("layout_size", self.size.value)
frame.setAttribute(Qt.WA_StyledBackground, True)
frame.setObjectName("RecipeCard")

frame.setFixedSize(LAYOUT_SIZE[self.size.value])

# ⚠️ Temporary in-line fix for transparency/styling
frame.setStyleSheet("background-color: #1B1D23; border-radius: 10px;")
Even though RecipeCard was correctly named and targeted in a QSS file, properties like background-color and border-radius wouldn’t apply. The fallback was in-line styling—which worked, but broke consistency and scalability.

2. Thoughts on Styling Architecture & Syntax
Preference in Syntax
I prefer Theme.applyWidgetStyle(widget) over self.apply_widget_style() because:

It provides clearer context.

It separates the styling logic from the widget logic.

However, I’m unsure if this undermines the purpose of a mixin subclass.

My original thinking was to register widgets with Theme, then:

At runtime, apply specific styles by referencing this registry.

Each class's style would be applied independently from others.

Terminology Clarification
When I refer to "widget styling", I’m often thinking in terms of the class, not the instance.
In PySide6, almost everything is a QWidget, which has skewed my mental model toward:

Global → Class → Instance

3. General Styling Strategy
Long-Term Goal:
All styling should be handled through external stylesheets.

In-line styles are only being used right now to resolve specific overrides or conflicts.

All stylesheets are (or will be) dynamic, using my theme variable injection system.

4. Current Styling Layers
Layer 1: Global Stylesheet (Applied at Runtime)
This defines the base appearance of all common widgets across the app.

Example:
qss
Copy
Edit
/* Universal Settings */
QWidget {
    font-family: 'Roboto';
    font-size: 10pt;
    background-color: {background};
    color: {on_surface};
}

/* Buttons */
QPushButton {
    background-color: {surface};
    color: {on_surface};
    border: 1px solid {outline};
    padding: 8px 16px;
    border-radius: 4px;
}

/* Input Fields */
QLineEdit, QTextEdit, QComboBox {
    background-color: {surface};
    color: {on_surface};
    border: 1px solid {outline};
    border-radius: 4px;
    padding: 5px;
}

/* Labels inherit parent background */
QLabel {
    background-color: transparent;
}
This layer:

Ensures consistent base styles for common widget types.

Reduces repetition (e.g., font attributes don’t need to be redefined everywhere).

Provides a foundation that custom components build upon.

Layer 2: Widget/Class-Specific Styling
This is where things become complex.

Case Example:
I have a custom ToolButton class, subclassed from QToolButton.

QToolButton is styled globally.

If I don’t style ToolButton, it inherits global styles.

However:

I use ToolButton inside different widgets (e.g. ComboBox, SearchBar), each needing unique styling.

Styling inheritance here can lead to conflicts, especially when deeply nested.

5. The Root of the Problem: QSS Inheritance
QSS inheritance is inconsistent:

Sometimes everything cascades as expected (e.g., styling QWidget affects children).

Other times, especially in deeply nested widgets, specific styles don’t apply—even with object names or properties clearly set.

Troublesome areas:

QScrollArea, QAbstractItemView, and similar widgets often behave unpredictably.

In most cases (about 80%), styling behaves predictably.

But for the remaining 20%, you’re chasing down overrides or trying to track widget ownership and hierarchy.

Final Thoughts
I’m trying to build a scalable styling system that:

> Avoids per-instance stylesheet application, which I’ve confirmed causes performance hits in large dynamic views (e.g., 100+ RecipeCard instances).

**Key Benefits:**
- Delivers clean overrides per class/widget type without relying on in-line hacks.
- Ties into my theme refresh system, meaning:
    - All styling (global, class, instance) can be refreshed together, ensuring consistency.
    - Variable injection and dynamic theme changes are possible across all components, without having to restyle manually.

> 💡 For testing purposes, I’ve recently added `TITLEBAR` to the `Qss` enum to begin experimenting with how this structure scales.

```python
class Qss(Enum):
    BASE = AppPaths.BASE_STYLE

    # Widget-specific stylesheets
    TITLEBAR = AppPaths.QSS_DIR / "titlebar.qss"
```

The ultimate goal is to let each styling layer—global, class-level, and instance—hook into a centralized, declarative styling system that avoids duplication, maximizes reusability, and supports dynamic theming with confidence.

