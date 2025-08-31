# 📋 Full Recipe Refactoring Plan - Phased Approach

**Target File**: `app\ui\views\full_recipe.py`  
**Current State**: ~505 lines with manual patterns, repeated code, and missed optimization opportunities  
**Goal**: Consolidate using existing utility functions, improve maintainability, reduce code duplication

---

## 🟢 Phase 1: High Impact, Low Complexity

**Status**: Ready to implement  
**Focus**: Replace manual patterns with existing utilities

### 1.1 Main Layout Refactoring (Lines 219-242)

**Current**: Manual scroll area setup (24 lines)
```python
# Root layout holds a single scroll area
root = QVBoxLayout(self)
root.setContentsMargins(0, 0, 0, 0)
root.setSpacing(0)

scroll = QScrollArea(self)
scroll.setObjectName("FullRecipeScroll")
scroll.setFrameShape(QFrame.NoFrame)
scroll.setWidgetResizable(True)
scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
root.addWidget(scroll)

# Scroll content
content = QWidget()
content.setContentsMargins(100, 0, 100, 0)
content.setObjectName("FullRecipeContent")
scroll.setWidget(content)

page = QVBoxLayout(content)
page.setContentsMargins(30, 30, 30, 30)
page.setSpacing(25)
```

**After**: Use `setup_main_scroll_layout()` utility
```python
# Replace 24 lines with utility call
from app.ui.utils.layout_utils import setup_main_scroll_layout

self.root, self.scroll, self.content, self.page = setup_main_scroll_layout(
    self, "FullRecipeContent", margins=(130, 30, 130, 30), spacing=25
)
```
**Impact**: ~20 lines → 4 lines (80% reduction)

### 1.2 Text Sanitization (Lines 137, 311-314, 364, 373)

**Current**: Manual `.strip()` and fallback patterns scattered throughout
```python
steps = [s.strip() for s in directions.splitlines() if s.strip()] if directions else []

total_time = str(getattr(self.recipe, "total_time", "")) or "2 hours 30 mins"
servings = str(getattr(self.recipe, "servings", "")) or "6"
category = getattr(self.recipe, "recipe_category", "") or "Main Course"

recipe_directions = getattr(self.recipe, "directions", "") or ""
notes = getattr(self.recipe, "notes", None)
```

**After**: Use text and format utilities
```python
from app.core.utils.text_utils import sanitize_multiline_input, is_empty_or_whitespace
from app.core.utils.format_utils import safe_getattr_with_fallback

steps = sanitize_multiline_input(directions).splitlines() if directions else []

# Centralized attribute extraction with fallbacks
recipe_data = extract_recipe_display_data(self.recipe)
```
**Impact**: More consistent text handling, reduced duplication

### 1.3 Signal Connection Consolidation (Lines 291-297)

**Current**: Manual signal connections
```python
self.recipe_banner.generate_image_requested.connect(self._on_generate_banner_requested)
self.recipe_banner.image_clicked.connect(self._on_image_clicked)
```

**After**: Use batch signal connection
```python
from app.ui.utils.event_utils import batch_connect_signals

signal_connections = [
    (self.recipe_banner.generate_image_requested, self._on_generate_banner_requested),
    (self.recipe_banner.image_clicked, self._on_image_clicked)
]
batch_connect_signals(signal_connections)
```
**Impact**: Better organization of event handling

---

## 🟡 Phase 2: Medium Impact, Medium Complexity  

**Status**: Structural improvements with moderate effort

### 2.1 Recipe Data Extraction Pattern (Lines 263-265, 311-314)

**Current**: Repeated `getattr()` calls with fallbacks scattered throughout
```python
meal_type = getattr(self.recipe, "meal_type", None) or "Dinner"
category = getattr(self.recipe, "recipe_category", None) or "Main Course"
diet_pref = getattr(self.recipe, "diet_pref", None) or "High-Protein"

total_time = str(getattr(self.recipe, "total_time", "")) or "2 hours 30 mins"
servings = str(getattr(self.recipe, "servings", "")) or "6"
category = getattr(self.recipe, "recipe_category", "") or "Main Course"
diet_pref = getattr(self.recipe, "diet_pref", "") or "High-Protein"
```

**After**: Create centralized data extraction utility function  
```python
def _extract_recipe_display_data(self, recipe: Recipe) -> dict:
    """Extract and format recipe data with consistent fallbacks."""
    from app.core.utils.text_utils import sanitize_form_input
    
    return {
        "title": sanitize_form_input(getattr(recipe, "recipe_name", "")) or "Untitled Recipe",
        "meal_type": getattr(recipe, "meal_type", None) or "Dinner", 
        "category": getattr(recipe, "recipe_category", None) or "Main Course",
        "diet_pref": getattr(recipe, "diet_pref", None) or "High-Protein",
        "total_time": str(getattr(recipe, "total_time", "")) or "2 hours 30 mins",
        "servings": str(getattr(recipe, "servings", "")) or "6",
        "directions": getattr(recipe, "directions", "") or "",
        "notes": getattr(recipe, "notes", None)
    }

# Usage
recipe_data = self._extract_recipe_display_data(self.recipe)
```
**Impact**: Centralized fallback logic, easier to maintain, consistent formatting

### 2.2 Widget Creation Standardization (Lines 71-115, 158-183)

**Current**: Manual widget and layout creation in IngredientList and DirectionsList
```python
# IngredientList._addIngredientItem()
item_widget = QWidget()
item_widget.setObjectName("IngredientItem")

item_layout = QGridLayout(item_widget)
item_layout.setContentsMargins(0, 0, 0, 0)
item_layout.setHorizontalSpacing(10)
item_layout.setVerticalSpacing(0)

qty_label = QLabel(formatted_qty)
qty_label.setObjectName("IngredientQuantity")
qty_label.setMinimumWidth(60)
qty_label.setMaximumWidth(60)
qty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
```

**After**: Use widget creation utilities
```python
from app.ui.utils.widget_utils import create_label_with_alignment, apply_object_name_pattern
from app.ui.utils.layout_utils import create_form_grid_layout

item_widget = QWidget()
apply_object_name_pattern(item_widget, "Ingredient", "Item")

item_layout = create_form_grid_layout(item_widget, margins=(0,0,0,0), spacing=10)

qty_label = create_label_with_alignment(formatted_qty, Qt.AlignRight | Qt.AlignVCenter)
apply_object_name_pattern(qty_label, "Ingredient", "Quantity")
qty_label.setFixedWidth(60)
```
**Impact**: More consistent widget creation, reduced boilerplate

### 2.3 Error Handling Consolidation (Lines 434-496)

**Current**: Repeated try/catch patterns in AI generation methods
```python
# Multiple similar patterns for error handling and path validation
if Path(banner_path).exists():
    self.recipe_banner.set_banner_image_path(banner_path)
    # ... success handling
else:
    self.recipe_banner.show_placeholder_state()
    self.recipe_banner.reset_banner_button()
    # ... error handling
```

**After**: Use error handling utilities
```python
from app.core.utils.error_utils import handle_path_operation, log_operation_result

result = handle_path_operation(
    banner_path,
    success_callback=lambda p: self.recipe_banner.set_banner_image_path(p),
    failure_callback=lambda: self._reset_banner_to_placeholder(),
    operation_name="Banner image loading"
)
log_operation_result(result, f"Banner loading for '{recipe_name}'")
```
**Impact**: Consistent error handling, reduced duplication

---

## 🟠 Phase 3: High Impact, High Complexity

**Status**: Major structural changes requiring careful refactoring

### 3.1 Card Creation Pattern Consolidation (Lines 328-390)

**Most Complex Change** - Multiple similar card creation patterns
**Current**: Repeated card setup with near-identical patterns
```python
# Ingredients Card
ingredients_card = Card(content, card_type="Primary")
ingredients_card.setHeader("Ingredients", Icon.INGREDIENTS)
ingredients_card.headerIcon.setSize(30, 30)
ingredients_card.headerIcon.setColor("primary")
ingredients_card.setContentMargins(25, 25, 25, 25)
ingredients_card.setSpacing(15)
ingredients_card.expandWidth(True)

# Directions Card
directions_card = Card(content, card_type="Primary")
directions_card.setHeader("Directions", Icon.DIRECTIONS)
directions_card.headerIcon.setSize(30, 30)
directions_card.headerIcon.setColor("primary")
directions_card.setContentMargins(25, 25, 25, 25)
directions_card.setSpacing(15)
directions_card.expandWidth(True)

# Notes Card (similar pattern)
```

**After**: Create card factory utility function
```python
def _create_recipe_section_card(self, title: str, icon: Icon, content_widget: QWidget) -> Card:
    """Create standardized recipe section card."""
    card = Card(self.content, card_type="Primary")
    card.setHeader(title, icon)
    card.headerIcon.setSize(30, 30)
    card.headerIcon.setColor("primary") 
    card.setContentMargins(25, 25, 25, 25)
    card.setSpacing(15)
    card.expandWidth(True)
    card.addWidget(content_widget)
    return card

# Usage
ingredients_card = self._create_recipe_section_card("Ingredients", Icon.INGREDIENTS, ingredients_list)
directions_card = self._create_recipe_section_card("Directions", Icon.DIRECTIONS, directions_list)
if notes_text:
    notes_card = self._create_recipe_section_card("Notes", Icon.NOTES, notes_text)
```
**Impact**: ~45 lines → ~15 lines, much more maintainable

### 3.2 Layout Builder Pattern (Lines 322-396)

**Current**: Manual two-column layout construction
```python
content_layout = QHBoxLayout()
content_layout.setContentsMargins(0, 0, 0, 0)
content_layout.setSpacing(30)

# Left Column: Ingredients (1/3 width)
# ... ingredients card setup

# Right Column: Directions + Notes (2/3 width)  
right_column_widget = QWidget()
right_column_layout = QVBoxLayout(right_column_widget)
right_column_layout.setContentsMargins(0, 0, 0, 0)
right_column_layout.setSpacing(25)

# ... add cards to columns
content_layout.addWidget(ingredients_card, 1, Qt.AlignTop)
content_layout.addWidget(right_column_widget, 2, Qt.AlignTop)
```

**After**: Use layout builder utility
```python
from app.ui.utils.layout_utils import create_two_column_layout

content_layout = create_two_column_layout(
    left_widgets=[ingredients_card],
    right_widgets=[directions_card, notes_card] if notes_card else [directions_card],
    left_weight=1,
    right_weight=2, 
    spacing=30,
    alignment=Qt.AlignTop
)
```
**Impact**: ~25 lines → 8 lines, more declarative

---

## 🔵 Phase 4: Final Polish & Optimization

**Status**: Code quality improvements and performance optimizations

### 4.1 Method Decomposition (Lines 219-399)

**Current**: Large `_build_ui()` method (180 lines)
**After**: Break into focused methods
```python
def _build_ui(self) -> None:
    """Build the main UI matching the mock design.""" 
    self._setup_scroll_layout()
    self._create_header_section()
    self._create_recipe_info_section()
    self._create_content_sections()

def _setup_scroll_layout(self):
    """Setup main scroll layout."""
    # Use Phase 1.1 improvements

def _create_header_section(self):
    """Create back button, title, and tags."""
    # Extract header creation logic
    
def _create_recipe_info_section(self):
    """Create banner and info cards."""
    # Extract banner and info card setup
    
def _create_content_sections(self):  
    """Create ingredients, directions, and notes sections."""
    # Use Phase 3.1 and 3.2 improvements
```
**Impact**: Better code organization, easier testing, improved maintainability

### 4.2 Constants Consolidation

**Current**: Magic numbers scattered throughout
```python
content.setContentsMargins(100, 0, 100, 0)  # Line 235
page.setContentsMargins(30, 30, 30, 30)     # Line 240
tags_layout.addSpacing(20)                  # Line 268
card.setContentMargins(25, 25, 25, 25)     # Lines 332, 357, 379
```

**After**: Define layout constants
```python
# At top of file
class LayoutConstants:
    CONTENT_MARGINS = (130, 30, 130, 30)
    PAGE_MARGINS = (30, 30, 30, 30) 
    CARD_MARGINS = (25, 25, 25, 25)
    TAG_SPACING = 20
    CONTENT_SPACING = 30
    COLUMN_SPACING = 25
```
**Impact**: Easier maintenance, consistent spacing

### 4.3 Performance Optimizations

**Current**: Multiple `getattr()` calls on same object
**After**: Cache recipe attribute lookups
```python
@property
def _recipe_cache(self):
    """Cache frequently accessed recipe attributes."""
    if not hasattr(self, '_cached_recipe_data'):
        self._cached_recipe_data = self._extract_recipe_display_data(self.recipe)
    return self._cached_recipe_data
```
**Impact**: Reduced attribute lookup overhead

---

## 📊 Total Estimated Impact

### Code Reduction:
- **Current**: ~505 lines
- **After refactoring**: ~350-400 lines  
- **Net reduction**: ~105-155 lines (21-31% reduction)

### Maintainability Improvements:
- ✅ Centralized layout creation patterns
- ✅ Consistent text processing and fallback handling
- ✅ Standardized widget creation using utilities  
- ✅ Better error handling consolidation
- ✅ Improved method organization and decomposition
- ✅ Reduced code duplication across similar patterns

### Implementation Priority:
1. **Phase 1**: Quick wins with existing utilities (1-2 hours)
2. **Phase 2**: Medium complexity structural improvements (2-3 hours)
3. **Phase 3**: Complex card and layout refactoring (3-4 hours) 
4. **Phase 4**: Final polish and optimization (1-2 hours)

**Total Effort**: 7-11 hours for complete refactoring
**Branch Strategy**: Continue on current branch or create `refactor/full-recipe-view-consolidation`