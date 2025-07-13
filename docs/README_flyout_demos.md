# FlyoutWidget Demo Applications

This directory contains demo applications showcasing the enhanced `FlyoutWidget` component located at `app/ui/components/layout/flyout_widget.py`.

## Demo Applications

### 1. `advanced_flyout_demo.py` - Comprehensive New Features Demo

A comprehensive demonstration application showcasing all the new flexible anchoring capabilities:

**Features Demonstrated:**
- **Widget Anchoring**: Traditional widget-based anchoring (improved)
- **Point Anchoring**: Anchor to specific screen coordinates
- **Edge Anchoring**: Slide in from screen/window edges (sidebar style)
- **Custom Anchoring**: Precise control with custom start/end positions
- **Interactive Builder**: Live adjustment of all flyout parameters
- **Advanced Features**:
  - Chained flyouts
  - Auto-positioning based on available space
  - Dynamic content updates
  - Multiple simultaneous flyouts

**To Run:**
```bash
python scripts/advanced_flyout_demo.py
```

### 2. `simple_flyout_test.py` - Basic Multi-Mode Test

An updated simple test demonstrating the three main anchoring modes:
- Widget anchoring
- Point anchoring
- Edge anchoring

**To Run:**
```bash
python scripts/simple_flyout_test.py
```

### 3. `flyout_demo.py` - Original Demo (Still Works)

The original comprehensive demo still works with the updated widget, demonstrating backward compatibility.

## FlyoutWidget Overview - Enhanced Version

The `FlyoutWidget` now supports multiple anchoring modes for maximum flexibility and precise control.

### 🎯 New Anchoring Modes

#### 1. Widget Anchoring (Traditional)
```python
# Traditional approach (still works)
flyout = FlyoutWidget(anchor=button, direction=FlyoutWidget.RIGHT, content=content)

# New factory method (cleaner)
flyout = FlyoutWidget.from_widget(button, FlyoutWidget.RIGHT, content)
```

#### 2. Point Anchoring (Coordinates)
```python
# Anchor to specific screen coordinates
flyout = FlyoutWidget.from_point(x=300, y=200, direction=FlyoutWidget.BOTTOM, content=content)
```

#### 3. Edge Anchoring (Off-Screen Sliding) - IMPROVED! ✨
```python
# Slide in from screen edges - perfect for sidebars!
flyout = FlyoutWidget.from_edge("left", content=content, parent=main_window)
flyout = FlyoutWidget.from_edge("right", content=content)
flyout = FlyoutWidget.from_edge("top", content=content)
flyout = FlyoutWidget.from_edge("bottom", content=content)

# With automatic repositioning when window moves/resizes (enabled by default)
flyout = FlyoutWidget.from_edge("left", content=content, auto_reposition=True)
```

**🔧 Edge Anchoring Improvements:**
- Now properly anchors to the **application window** instead of arbitrary parent widgets
- **Consistent behavior** when resizing and repositioning the window
- **Auto-repositioning** keeps flyouts properly anchored during window events
- **Reliable coordinate system** using global window coordinates

### 🔧 Edge Anchoring Fixes

**Problem Solved:** Edge anchoring now properly references the application window instead of arbitrary parent widgets, providing consistent behavior when resizing and moving the window.

**Key Improvements:**
- ✅ **Consistent Reference Point**: Always uses the main application window as the anchor reference
- ✅ **Proper Coordinate System**: Uses global window coordinates for reliable positioning
- ✅ **Auto-Repositioning**: Flyouts automatically reposition when the window moves or resizes
- ✅ **Smart Window Detection**: Automatically finds the correct application window
- ✅ **Event Filtering**: Uses efficient event filtering to monitor window changes

**Test the Fix:**
```bash
python scripts/test_edge_anchoring.py
# Try resizing and moving the window while flyouts are visible!
```

#### 4. Custom Anchoring (Precise Control)
```python
# Define exact start and end positions
start_point = QPoint(100, 100)  # Off-screen position
end_point = QPoint(200, 150)    # Final position
flyout = FlyoutWidget.from_custom(start_point, end_point, content=content)

# Or use anchor point with custom offsets
custom_config = {
    "anchor_point": {"x": 400, "y": 300},
    "offset_x": 20,
    "offset_y": -10,
    "slide_distance": 150
}
flyout = FlyoutWidget(anchor=custom_config, anchor_mode=FlyoutWidget.ANCHOR_CUSTOM, content=content)
```

### 🚀 Convenience Factory Methods

#### Sidebar-Style Flyout
```python
# Create sidebar that slides from window edge
sidebar_flyout = FlyoutWidget.sidebar_style(
    parent=main_window,
    content=sidebar_content,
    from_left=True  # or False for right side
)
```

### 🎛️ Enhanced Features

#### Dynamic Anchor Updates
```python
# Change anchor on the fly
flyout.set_anchor(new_button)  # Switch to widget anchoring
flyout.set_anchor(QPoint(500, 300), FlyoutWidget.ANCHOR_POINT)  # Switch to point anchoring
```

#### Auto-Detection
```python
# The widget auto-detects anchor mode based on type
flyout = FlyoutWidget(anchor=QPoint(100, 100))  # Auto-detects ANCHOR_POINT
flyout = FlyoutWidget(anchor="left")            # Auto-detects ANCHOR_EDGE
flyout = FlyoutWidget(anchor=button)            # Auto-detects ANCHOR_WIDGET
```

### 📐 Anchor Modes Constants

```python
FlyoutWidget.ANCHOR_WIDGET  # Widget-based anchoring
FlyoutWidget.ANCHOR_POINT   # Coordinate-based anchoring
FlyoutWidget.ANCHOR_EDGE    # Edge-based anchoring (off-screen)
FlyoutWidget.ANCHOR_CUSTOM  # Custom positioning with full control

# Edge constants
FlyoutWidget.EDGE_LEFT
FlyoutWidget.EDGE_RIGHT
FlyoutWidget.EDGE_TOP
FlyoutWidget.EDGE_BOTTOM
```

### 🎨 Use Cases

#### Perfect for Sidebars
```python
# Just like your sidebar implementation!
sidebar = FlyoutWidget.from_edge("left", sidebar_content, parent=main_window)
sidebar.toggle_flyout()  # Slides in from off-screen
```

#### Tooltips with Precise Positioning
```python
tooltip = FlyoutWidget.from_point(mouse_x, mouse_y, FlyoutWidget.BOTTOM, tooltip_content)
```

#### Context Menus
```python
context_menu = FlyoutWidget.from_widget(clicked_widget, FlyoutWidget.RIGHT, menu_content)
```

#### Notifications
```python
notification = FlyoutWidget.from_edge("top", notification_content)
```

### ⚙️ Migration Guide

**Old Code:**
```python
flyout = FlyoutWidget(anchor=button, direction=FlyoutWidget.RIGHT, content=content)
```

**New Code (Backward Compatible):**
```python
# Still works exactly the same!
flyout = FlyoutWidget(anchor=button, direction=FlyoutWidget.RIGHT, content=content)

# Or use the cleaner factory method:
flyout = FlyoutWidget.from_widget(button, FlyoutWidget.RIGHT, content)
```

All existing code continues to work unchanged - the enhancements are fully backward compatible!

### 🛠️ Advanced Configuration

#### Custom Positioning Example
```python
# Slide in from a custom off-screen position
custom_config = {
    "start": {"x": -200, "y": 100},  # Start off-screen left
    "end": {"x": 50, "y": 100}       # End 50px from left edge
}
flyout = FlyoutWidget(
    anchor=custom_config,
    anchor_mode=FlyoutWidget.ANCHOR_CUSTOM,
    content=content,
    duration=500
)
```

#### Edge Anchoring with Parent Context
```python
# Edge anchoring respects parent widget bounds
flyout = FlyoutWidget.from_edge("left", content, parent=specific_widget)
# Will slide from the left edge of specific_widget, not the screen
```

## Development Notes

The enhanced FlyoutWidget maintains all original functionality while adding:

- **Flexible anchoring system** with auto-detection
- **Factory methods** for cleaner code
- **Edge anchoring** for off-screen sliding effects
- **Point anchoring** for precise coordinate control
- **Custom anchoring** for complex positioning needs
- **Full backward compatibility** with existing code

The widget automatically handles:
- Parent widget detection and relationships
- Global position calculations for all anchor modes
- Popup behavior and focus management
- Animation cleanup and memory management

### 🔧 Widget Anchoring Fix

**Problem Fixed:** Widget anchoring coordinates were incorrectly calculated, causing flyouts to appear offset from their intended anchor positions.

**Root Cause:** The original code used `widget.geometry().topLeft()` which gives coordinates relative to the parent, then tried to map that to global coordinates. This created a double-offset error.

**Solution:** Now uses `widget.mapToGlobal(QPoint(0, 0))` directly to get the widget's actual global position.

**Before (Incorrect):**
```python
anchor_geo = self.anchor.geometry()
top_left = self.anchor.mapToGlobal(anchor_geo.topLeft())  # Double offset!
```

**After (Fixed):**
```python
anchor_global_pos = self.anchor.mapToGlobal(QPoint(0, 0))  # Correct global position
anchor_size = self.anchor.size()
```

**Result:**
- ✅ RIGHT flyouts now appear exactly to the right of anchor buttons with top edges aligned
- ✅ BOTTOM flyouts now appear exactly below anchor buttons with left edges aligned
- ✅ All widget anchoring now uses precise coordinate calculations
