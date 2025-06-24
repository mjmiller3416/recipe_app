# 🍽️ MealGenie Dashboard Design Documentation

## 🧾 Summary: Dashboard Vision

The Dashboard is a customizable, grid-based command center designed to present all core application data in a modular, interactive layout. Users can add, reposition, and resize widgets using an intuitive edit mode that reveals a rounded, opaque grid for alignment and snapping.

### 🔑 Key Features

* Invisible Grid: 9x6 structure (editable only)

* Widgets: Predefined sizes (e.g., 1x1, 3x1, 4x3, etc.)

* Snap-To-Grid: Widgets align to nearest available cell

* Drag-and-Drop Repositioning

* Resizing via Tooltips or Context Menus

* Layout Persistence

* Interactive vs Static Mode Toggle


### 📦 Widget Types (Examples)

* Quick Add Recipe

* Weekly Meal Carousel

* Grocery Snapshot

* Favorite Recipes

* Recent Activity

### 🧱 Architecture Overview

#### Core Classes

* DashboardGrid: Main canvas layout using fixed cell structure

* DashboardWidget: Base class for all widgets

* WidgetSize: Enum for widget sizing presets

* GridOverlay: Paints visual grid (edit mode only)

* DashboardController: Manages state, collisions, widget logic

* LayoutPersistenceService: Loads/saves widget state

## Phase 1: Static Grid + Dummy Widgets

### ✅ Goal

Render a fixed 9x6 dashboard grid and display static, hardcoded widgets based on their size and grid coordinates.

### 📄 Files

* widget_sizes.py: Enum for available widget sizes

* dashboard_widget.py: Base widget with simple QLabel layout

* dashboard_grid.py: Widget that places DashboardWidgets in fixed positions

### 📦 Required Classes and Responsibilities

`WidgetSize (Enum)`

* Defines valid widget sizes using (columns, rows) as values

Includes convenience methods:

* cols(): Returns width in columns

* rows(): Returns height in rows

`DashboardWidget`

Base widget that:

* Stores an ID, title, and WidgetSize

* Renders simple layout (e.g., QLabel placeholder)

* Will eventually support interaction/resizing (not in Phase 1)

`DashboardGrid`

Handles:

* Fixed constants for rows, cols, spacing, and cell size

* Manual placement of dashboard widgets using grid math

* Optional dev-mode grid paint overlay (faint)

*Must implement:*

* _place_widget(widget, row, col) → calculates and sets widget size + position

* _place_dummy_widgets() → hardcoded sample widgets for testing layout

### 📌 Static Layout Rules

* Grid Size: 9 columns × 6 rows

* Cell Size: 100px × 100px (plus spacing)

* Spacing: 10px between cells

* Widget Placement:

* Based on top-left corner cell + size from WidgetSize

*Example: A 4x3 widget at (2,4) consumes 4 columns & 3 rows*

### 📌 Example Dummy Widgets

* 1x2 Recipe Card at (1,1)

* 3x1 Header Banner at (0,3)

* 4x3 Carousel at (2,4)

### Phase Outcome

* Basic rendering of a responsive dashboard canvas

* Supports static widget display using grid structure

* Sets the stage for edit mode, snapping, and drag logic#

