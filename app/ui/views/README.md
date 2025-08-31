● 📋 Add Recipes Refactoring Plan - Remaining Phases

  ✅ Completed - Phase 1

  High Impact, Low Complexity - DONE
  - ✅ Replaced custom _parse_servings() with parse_servings_range()
  - ✅ Replaced manual int() with safe_int_conversion()
  - ✅ Replaced manual float() with safe_float_conversion()
  - ✅ Replaced manual form clearing with clear_form_fields()
  - ✅ Net reduction: 20 lines (committed in 4918ed9f)

  ---
  🟡 Phase 2: High Impact, Medium Complexity

  Status: ✅ Completed

  2.1 Main Layout Refactoring (Lines 477-497)

  # Replace 20+ lines of manual scroll setup with:
  from app.ui.utils.layout_utils import setup_main_scroll_layout

  def _build_ui(self):
      self.lyt_main, self.scroll_area, self.scroll_content, self.scroll_layout = \
          setup_main_scroll_layout(self, "AddRecipeContent")
  Impact: ~18 lines → 2 lines

  2.2 Form Data Collection (Lines 741-750)

  # Replace manual field collection with:
  from app.ui.utils.form_utils import collect_form_data

  form_mapping = {
      "recipe_name": self.le_recipe_name,
      "recipe_category": self.cb_recipe_category,
      "meal_type": self.cb_meal_type,
      "dietary_preference": self.cb_dietary_preference,
      "total_time": self.le_time,
      "servings": self.le_servings,
      "directions": self.te_directions
  }
  data = collect_form_data(form_mapping)
  # Apply transformations for servings/time parsing
  Impact: Cleaner, more maintainable data collection

  2.3 Add Form Validation (Before line 666)

  # Add comprehensive validation:
  from app.core.utils.validation_utils import validate_required_fields

  required_fields = ["recipe_name", "meal_type", "servings"]
  validation_errors = validate_required_fields(form_data, required_fields)
  if validation_errors:
      # Display validation errors and return early
      return
  Impact: Better UX with proper validation

  ---
  🟠 Phase 3: High Impact, High Complexity

  Status: ✅ Completed

  3.1 RecipeForm Grid Layout Refactor (Lines 43-109)

  Most Complex Change - Complete grid restructure
  # Replace entire RecipeForm layout with declarative config:
  from app.ui.utils.layout_utils import create_labeled_form_grid

  field_configs = {
      "recipe_name": {
          "widget_type": "line_edit",
          "label": "Recipe Name",
          "placeholder": "e.g. Spaghetti Carbonara",
          "object_name": "RecipeNameLineEdit",
          "row": 0, "col": 0, "col_span": 2
      },
      "time": {
          "widget_type": "line_edit",
          "label": "Total Time",
          "placeholder": "e.g. 30 mins",
          "object_name": "TimeLineEdit",
          "row": 2, "col": 0
      },
      "servings": {
          "widget_type": "line_edit",
          "label": "Servings",
          "placeholder": "e.g. 4",
          "object_name": "ServingsLineEdit",
          "row": 2, "col": 1
      },
      "meal_type": {
          "widget_type": "combo_box",
          "label": "Meal Type",
          "placeholder": "Select meal type",
          "list_items": MEAL_TYPE,
          "object_name": "MealTypeComboBox",
          "context": "recipe_form",
          "row": 4, "col": 0
      },
      "recipe_category": {
          "widget_type": "combo_box",
          "label": "Recipe Category",
          "placeholder": "Select category",
          "list_items": RECIPE_CATEGORIES,
          "object_name": "RecipeCategoryComboBox",
          "context": "recipe_form",
          "row": 4, "col": 1
      },
      "dietary_preference": {
          "widget_type": "combo_box",
          "label": "Dietary Preference",
          "placeholder": "Select dietary preference",
          "list_items": DIETARY_PREFERENCES,
          "object_name": "DietaryPreferenceComboBox",
          "context": "recipe_form",
          "row": 6, "col": 0, "col_span": 2
      }
  }

  layout, widgets, labels = create_labeled_form_grid(self, field_configs)
  # Assign widgets to self.le_*, self.cb_* attributes
  Impact: ~66 lines → ~30 lines, much more maintainable

  3.2 Event Management Refactor (Lines 575-586)

  # Replace manual signal connections with:
  from app.ui.utils.event_utils import connect_form_signals, batch_connect_signals

  form_change_handlers = {
      "recipe_name": self._on_recipe_name_changed,
      "meal_type": self._on_meal_type_changed
  }
  connect_form_signals(form_widgets, form_change_handlers)

  # Batch connect remaining signals
  signal_connections = [
      (self.ingredient_container.ingredient_added, self._on_ingredient_added),
      (self.ingredient_container.ingredient_deleted, self._on_ingredient_deleted),
      (self.recipe_image.image_selected, self._update_image_path)
  ]
  batch_connect_signals(signal_connections)
  Impact: Better organization, more maintainable

  ---
  🔵 Phase 4: Final Refinements

  Status: ✅ Completed

  4.1 Tab Order Setup (Lines 639-660)

  # Replace manual tab order with:
  from app.ui.utils.form_utils import setup_tab_order_chain

  widgets = [
      self.le_recipe_name, self.le_time, self.le_servings,
      self.cb_meal_type, self.cb_recipe_category, self.cb_dietary_preference,
      # ... ingredient widgets dynamically added
      self.te_directions
  ]
  setup_tab_order_chain(widgets)
  Impact: ~22 lines → 6 lines

  4.2 Text Sanitization (Multiple locations)

  # Replace manual .strip() calls with:
  from app.core.utils.text_utils import sanitize_form_input, sanitize_multiline_input

  # In to_payload():
  "recipe_name": sanitize_form_input(self.le_recipe_name.text()),
  "directions": sanitize_multiline_input(self.te_directions.toPlainText()),
  Impact: More consistent text processing

  4.3 Widget Creation Consolidation

  Apply throughout RecipeForm and IngredientForm
  # Replace manual widget creation with utilities:
  from app.ui.utils.widget_utils import create_combo_box, create_line_edit

  # Instead of:
  self.cb_meal_type = ComboBox(list_items=MEAL_TYPE, placeholder="Select meal type")
  self.cb_meal_type.setObjectName("ComboBox")
  self.cb_meal_type.setProperty("context", "recipe_form")

  # Use:
  self.cb_meal_type = create_combo_box(
      MEAL_TYPE, "Select meal type", "MealTypeComboBox", "recipe_form"
  )
  Impact: More consistent widget creation

  ---
  📊 Total Estimated Impact

  Code Reduction:

  - Current: ~790 lines
  - After refactoring: ~550-600 lines
  - Net reduction: ~200-250 lines (30-35%)

  Maintainability Improvements:

  - ✅ Centralized validation logic
  - ✅ Consistent form handling patterns
  - ✅ Standardized layout creation
  - ✅ Better error handling
  - ✅ Tested utility functions

  Implementation Order:

  1. Tomorrow morning: Complete Phase 2 (layout, data collection, validation)
  2. Phase 3: RecipeForm grid refactor (most complex)
  3. Phase 4: Final polish and cleanup

  Branch Status:

  - Current branch: refactor/add-recipes-view-consolidation
  - Last commit: 4918ed9f (Phase 1 complete)
  - Ready for: Phase 2 implementation
