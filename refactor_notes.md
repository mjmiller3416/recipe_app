# Recipe App Refactor (Revised)

## 1. Existing Structure

### 🔹 Icon System
**Folder:** `appearance/icon/`

| File | Purpose |
|------|---------|
| `icon.py` | Defines Icon widget (QLabel-based), currently bloated |
| `mixin.py` | Contains IconMixin, shared by buttons (deprecated-in-progress) |
| `config.py` | Enums for Path, Size, Name, Type, State, etc. |
| `loader.py` | IconLoader singleton for theme-refresh propagation |
| `svg_loader.py` | SVGLoader for rendering + recoloring SVGs dynamically |

### 🔹 Button System
**Folder:** `ui/components/widgets/`

| File | Purpose |
|------|---------|
| `button.py` | Current home of Button, ToolButton, and deprecated NavButton |
| `tool_button.py` | Duplicate legacy ToolButton, marked for deprecation |
| `nav_button.py` | Composite sidebar button with embedded ToolButton hack |

## 2. Existing Pain Points

### 🔸 Icon System
- **IconMixin bloated** and being misused across both buttons and widgets
- **State logic is injected** into contexts that don't need it (e.g. standalone Icon)
- **Inheritance is confusing** (QAbstractButton mixed with QLabel via mixin)
- **Fragmentation of logic** across icon.py, mixin.py, loader.py is overkill

### 🔸 Button System
- **Inconsistent layout behavior** between Button, ToolButton, and NavButton
- **NavButton uses embedded button hacks** (disabled ToolButton + manual state sync)
- **Qt's native icon + label layout limitations** led to rigid/awkward spacing hacks
- **Buttons rely on setIcon()** via QAbstractButton's internal logic — inflexible for layout-based design
- **Style and event handling often duplicated** (hover state sync, toggling, etc.)
- **Size hint calculations** with hardcoded values and edge case failures

## 3. Proposed Solutions

### 🧩 Unify Icon System
Move toward a class hierarchy:

```
BaseIcon → ThemedIcon → Icon (QLabel)
                    └→ StateIcon (QWidget)
```

**New behavior:**
- **Stateless icons** = use `Icon(QLabel)`
- **Stateful (hover/checked)** = use `StateIcon(QWidget)`
- **All theme syncing, color/size overrides** handled in `ThemedIcon`
- **SVG rendering abstracted** in `BaseIcon`
- **Existing IconLoader protocol** easily adapts to new ThemedIcon structure

➡️ **All of this goes into a single `icon.py` file.**

### 🧱 Rebuild Button System with Layout Composition
Refactor to layout-based buttons using **QAbstractButton inheritance**:

```
BaseButton (QAbstractButton)
    ├─ Button (with StateIcon + QLabel)
    └─ ToolButton (StateIcon only)
```

**Key traits:**
- ✅ **QAbstractButton inheritance** for proper button behavior (focus, accessibility, keyboard navigation)
- ✅ **StateIcon handles all icon logic** with automatic state synchronization
- ✅ **QHBoxLayout** for flexible icon + label positioning
- ✅ **Override paintEvent()** to let layout handle all visual rendering
- ✅ **Shared state sync logic** in BaseButton eliminates duplication
- ✅ **Proper size hints** delegated to layout system
- ✅ **Cleaner API** with consistent naming (setIconSize vs setCustomIconSize)

➡️ **All button classes move into one file:** `button.py`
➡️ **Remove:** `nav_button.py`, `tool_button.py`

## 4. Files to Merge / Remove

### ✅ To merge into `icon.py`
- **`mixin.py`** → fully integrated into new ThemedIcon / StateIcon system
- **Leave as-is:** `config.py`, `loader.py`, `svg_loader.py` (utility files, still valid)

### 🗑️ To remove
- ✅ `icon/mixin.py`
- ✅ `ui/components/widgets/nav_button.py`
- ✅ `ui/components/widgets/tool_button.py`

### ✅ To consolidate into `button.py`
- **BaseButton, Button, ToolButton** in one place
- **Shared helper functions** for common state/display logic
- **Final file is self-contained and flexible**

---

# New Structure for Icon Classes (Refactored)

## BaseIcon
**Lowest level icon logic:** size, color, and rendering via SVGLoader.
⚠️ **No theme awareness.** Meant to be subclassed by all icon types.

```python
class BaseIcon:
    def __init__(self, icon_enum: Name):
        """
        Base class to handle raw icon rendering logic.

        Args:
            icon_enum (Name): The predefined icon enum to use.
        """
        ...

    def setSize(self, width: int, height: int):
        """
        Set a custom rendering size for the icon.

        Args:
            width (int): Width in pixels.
            height (int): Height in pixels.
        """
        ...

    def setColor(self, color: str):
        """
        Set a custom color for rendering.

        Args:
            color (str): Hex value or theme role (e.g., "#FF0000" or "on_surface").
        """
        ...

    def clearColor(self):
        """
        Clear the custom color and fall back to the default (or theme role if applicable).
        """
        ...

    def _get_color(self) -> str:
        """
        Determine the effective color for rendering.

        Returns:
            str: Final hex color to be applied.
        """
        ...

    def _get_size(self) -> QSize:
        """
        Determine the effective rendering size.

        Returns:
            QSize: Final QSize to render the icon with.
        """
        ...

    def _render_icon(self):
        """
        Trigger a re-render of the icon using the current size and color settings.
        """
        ...
```

## ThemedIcon (BaseIcon)
**Adds theme-awareness:** auto-refresh on palette changes, and state support.
✅ **Used by all theme-reactive icon widgets.**
✅ **Integrates with existing IconLoader protocol** (just update method signatures).

```python
class ThemedIcon(BaseIcon):
    def __init__(self, icon_enum: Name):
        """
        Themed extension of BaseIcon. Registers for palette updates and
        can be overridden by color role or static hex color.
        """
        ...

    def refresh_theme(self, palette: dict[str, str]):
        """
        Called when the theme palette updates. Refreshes icon appearance.
        Compatible with existing IconLoader protocol.

        Args:
            palette (dict[str, str]): The current color map from ThemeManager.
        """
        ...

    def setSize(self, width: int, height: int):
        """
        Override to ensure theme refreshes are respected when size changes.
        """
        super().setSize(width, height)
        self.refresh_theme(palette=...)  # (get current from IconLoader)

    def setColor(self, color: str):
        """
        Override to update icon immediately with new theme role or static color.
        """
        super().setColor(color)
        self._render_icon()

    def clearColor(self):
        """
        Clear any override and fallback to default state color role.
        """
        super().clearColor()
        self._render_icon()

    def as_qicon(self, state: State = State.DEFAULT) -> QIcon:
        """
        Render the icon as a QIcon for legacy widget compatibility.

        Args:
            state (State): Icon state to use when generating the QIcon.

        Returns:
            QIcon: The themed icon for the requested state.
        """
        ...
```

## Icon (QLabel, ThemedIcon)
**Standalone visual widget** for themed SVG icons.
🎯 **Used in:** views, dashboards, cards, headers, etc.

```python
class Icon(QLabel, ThemedIcon):
    def __init__(self, icon_enum: Name, parent=None):
        """
        A QLabel-based icon widget that reflects theme changes and
        displays static or dynamic SVG content.

        Args:
            icon_enum (Name): The icon to render.
            parent (QWidget): Optional parent widget.
        """
        ...
```

## StateIcon (QWidget, ThemedIcon)
**Button-bound icon** with hover, checked, disabled states.
🔄 **Automatically updates appearance** based on current state.
🔄 **Syncs with parent button** via autoDetectState() calls.

```python
class StateIcon(QWidget, ThemedIcon):
    def __init__(self, icon_enum: Name, type: Type = Type.DEFAULT):
        """
        Themed icon that dynamically reacts to button state.

        Args:
            icon_enum (Name): Icon to display.
            type (Type): Button type to determine default state colors.
        """
        ...

    def setType(self, type: Type):
        """
        Set the visual type used for mapping state→colorRole (e.g. PRIMARY).

        Args:
            type (Type): Predefined visual role type.
        """
        ...

    def setStateDefault(self, color_role: str):
        """Override the color role for default state."""
        ...

    def setStateHover(self, color_role: str):
        """Override the color role for hover state."""
        ...

    def setStateChecked(self, color_role: str):
        """Override the color role for checked state."""
        ...

    def setStateDisabled(self, color_role: str):
        """Override the color role for disabled state."""
        ...

    def clearStateOverride(self, state: State):
        """
        Clear a specific state's override, restoring the default from `Type`.

        Args:
            state (State): Which state to clear.
        """
        ...

    def clearAllStateOverrides(self):
        """Clear all state overrides and fall back to default type mapping."""
        ...

    def updateState(self, state: State):
        """
        Force the icon to switch to a specific state.

        Args:
            state (State): State to switch to (e.g. HOVER).
        """
        ...

    def autoDetectState(self, checked: bool, hovered: bool, enabled: bool):
        """
        Set icon state automatically based on standard button logic.
        Called by parent BaseButton during state changes.

        Args:
            checked (bool): Whether button is checked.
            hovered (bool): Whether mouse is hovering.
            enabled (bool): Whether widget is enabled.
        """
        ...
```

# Structure for Button Classes (Layout-based) (Refactored)

## BaseButton (QAbstractButton)
**A unified base class** for all layout-based buttons (Button, ToolButton)
🔧 **Features:** state synchronization, icon management, shared event handling
✅ **Inherits from QAbstractButton** for proper button behavior (focus, accessibility, keyboard nav)

```python
class BaseButton(QAbstractButton):
    def __init__(self, type: Type = Type.DEFAULT):
        """
        Initialize the base button container.

        Args:
            type (Type): Button style type, which defines icon color mapping for each state.
        """
        ...

    def paintEvent(self, event):
        """Override to let layout handle all visual rendering."""
        pass

    def sizeHint(self) -> QSize:
        """Delegate size calculation to internal layout."""
        if self._button_size:
            return self._button_size
        
        layout_hint = self.layout().sizeHint()
        margins = self.contentsMargins()
        return QSize(
            layout_hint.width() + margins.left() + margins.right(),
            layout_hint.height() + margins.top() + margins.bottom()
        )

    def _sync_icon_state(self):
        """Synchronize StateIcon with current button state."""
        if self.state_icon:
            self.state_icon.autoDetectState(
                checked=self.isChecked(),
                hovered=self.underMouse(),
                enabled=self.isEnabled()
            )

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        super().enterEvent(event)
        self._sync_icon_state()

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        super().leaveEvent(event)
        self._sync_icon_state()

    def changeEvent(self, event):
        """Handle enabled/disabled state changes."""
        super().changeEvent(event)
        if event.type() == event.EnabledChange:
            self._sync_icon_state()

    def setButtonSize(self, width: int, height: int):
        """
        Set a fixed size for the entire button widget.

        Args:
            width (int): Button width in pixels.
            height (int): Button height in pixels.
        """
        ...

    def setIconSize(self, width: int, height: int):
        """
        Set the icon's size within the button.

        Args:
            width (int): Icon width in pixels.
            height (int): Icon height in pixels.
        """
        ...

    def setIconSpacing(self, pixels: int):
        """
        Set the spacing between the icon and label inside the layout.

        Args:
            pixels (int): Pixel spacing between icon and label.
        """
        ...

    def setStateHover(self, role: str):
        """
        Override the color role used for the hover state.

        Args:
            role (str): Theme palette role string (e.g. 'on_surface').
        """
        ...

    def setStateDefault(self, role: str):
        """Override the default icon color role."""
        ...

    def setStateChecked(self, role: str):
        """Override the checked icon color role."""
        ...

    def setStateDisabled(self, role: str):
        """Override the disabled icon color role."""
        ...

    def clearAllStateOverrides(self):
        """
        Clears all icon state color overrides, restoring type-based defaults.
        """
        ...

    def icon(self) -> "StateIcon":
        """
        Returns the StateIcon widget used in the button.

        Returns:
            StateIcon: The button's internal themed icon widget.
        """
        ...
```

## Button (BaseButton)
**A layout-based QPushButton replacement** with both icon + label.
📝 **StateIcon + QLabel positioned via QHBoxLayout.** 
🔄 **Replaces NavButton** with cleaner implementation.

```python
class Button(BaseButton):
    def __init__(self, label: str, type: Type = Type.DEFAULT, icon: Name = None):
        """
        Create a full button with icon and label.
        Replaces both old Button and NavButton functionality.

        Args:
            label (str): The button text label.
            type (Type): Visual style type (defines icon color map).
            icon (Name, optional): Optional icon enum to display.
        """
        super().__init__(type)
        
        # Setup layout with StateIcon + QLabel
        self.layout = QHBoxLayout(self)
        
        if icon:
            self.state_icon = StateIcon(icon, type)
            self.layout.addWidget(self.state_icon)
        
        self.label = QLabel(label)
        self.layout.addWidget(self.label)
        
        # Connect signals for state sync
        self.toggled.connect(self._sync_icon_state)

    def setText(self, label: str):
        """
        Set the button's text label.

        Args:
            label (str): New label to display.
        """
        ...

    def text(self) -> str:
        """
        Get the current text label.

        Returns:
            str: Current button text.
        """
        ...

    def setChecked(self, checked: bool):
        """
        Set the button's checked state.

        Args:
            checked (bool): Whether the button is checked.
        """
        ...

    def setCheckable(self, enabled: bool):
        """
        Enable or disable toggle behavior for the button.

        Args:
            enabled (bool): If True, allows button to toggle checked state.
        """
        ...
```

## ToolButton (BaseButton)
**Icon-only variant** of Button.
🔧 **StateIcon only,** but still supports checkable state, spacing, color overrides, and theme integration.

```python
class ToolButton(BaseButton):
    def __init__(self, icon: Name, type: Type = Type.DEFAULT):
        """
        Create a compact icon-only tool button.

        Args:
            icon (Name): The icon to display.
            type (Type): Visual style type (defines icon color map).
        """
        super().__init__(type)
        
        # Setup layout with just StateIcon
        self.layout = QHBoxLayout(self)
        self.state_icon = StateIcon(icon, type)
        self.layout.addWidget(self.state_icon)
        
        # Connect signals for state sync
        self.toggled.connect(self._sync_icon_state)

    def setChecked(self, checked: bool):
        """Set whether the tool button is checked."""
        ...

    def setCheckable(self, enabled: bool):
        """Enable or disable toggle behavior."""
        ...
```

---

## 5. Implementation Strategy

### 📋 Phase 1: Icon System
1. Create new `icon.py` with BaseIcon, ThemedIcon, Icon, StateIcon classes
2. Update IconLoader protocol to work with new ThemedIcon structure
3. Test standalone icon functionality in isolation
4. Verify theme switching and state management

### 📋 Phase 2: Button System  
1. Create new `button.py` with BaseButton, Button, ToolButton classes
2. Implement state synchronization between BaseButton and StateIcon
3. Test button functionality (click, toggle, hover, sizing) in isolation
4. Verify QAbstractButton behavior (focus, keyboard navigation, accessibility)

### 📋 Phase 3: Integration & Migration
1. Gradually replace existing button usage throughout app
2. Update API calls (setCustomIconSize → setIconSize, etc.)
3. Replace NavButton usage with new Button class
4. Remove deprecated files: `mixin.py`, `nav_button.py`, `tool_button.py`
5. Full testing of theme integration, state management, and edge cases

### 📋 Branch Strategy
- **Separate branch** for refactor work
- **Isolated testing** for each phase before app integration  
- **Gradual rollout** with easy rollback capability
- **Rebase with main** only after full implementation and testing