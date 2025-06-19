
# Unit Conversions Manager Blueprint

## 1. Project Structure

```
project_root/
├── conversions.json            # your unit mappings (edit via UI)
├── database/
│   └── …                       # your Pydantic models & services
├── ui/
│   ├── main_window.py          # your app’s startup & menu
│   └── conversion_editor.py    # the new ConversionEditor widget
└── services/
    └── shopping_service.py     # loads conversions.json at runtime
```

## 2. Prepare the JSON File

- **Create** `conversions.json` in your project root, initialize with your default map:
  ```json
  {
    "butter": { "stick": 8, "tbsp": 1 },
    "ground beef": { "lb": 1, "oz": 1/16 }
  }
  ```
- **Add** it to version control so you have a baseline but can commit UI-made changes too.

## 3. Build the `ConversionEditor` Widget

**File:** `ui/conversion_editor.py`

- **Subclass** `QWidget`
- **Layout**: a `QTableWidget` (cols: Ingredient, Unit, Factor) + Add/Remove/Save buttons
- **Methods**:
  - `load_data()`: JSON → table rows
  - `add_row()`: append empty row
  - `remove_selected()`: delete highlighted rows
  - `save_data()`: validate cells → reconstruct dict → write `conversions.json` → user feedback

*(Use the sketch I shared earlier as your starting code.)*

## 4. Hook it into Your Main App

**File:** `ui/main_window.py` (or wherever your menu lives)

1. **Import**:
   ```python
   from app.ui.conversion_editor import ConversionEditor
   from pathlib import Path
   ```
2. **Add** a “Unit Conversions…” action under your Settings menu:
   ```python
   act_conv = QAction("Unit Conversions…", self)
   act_conv.triggered.connect(self.open_conversion_editor)
   settings_menu.addAction(act_conv)
   ```
3. **Implement** the slot:
   ```python
   def open_conversion_editor(self):
       editor = ConversionEditor(
           json_path=Path(__file__).parent.parent / "conversions.json",
           parent=self
       )
       editor.exec_()  # or .show() depending on modal needs
   ```

## 5. Wire Up Your Shopping Service

**File:** `services/shopping_service.py`

- **At import or startup**, load your conversions:
  ```python
  import json
  from pathlib import Path
  CONV_PATH = Path(__file__).parent.parent / "conversions.json"
  with open(CONV_PATH) as f:
      _CONVERSIONS = json.load(f)
  ```
- **Use** that `_CONVERSIONS` dict in your `_convert_qty()` function—so any time she’s updated via the UI, a restart (or dynamic reload) picks up the new rules.

## 6. Test & Iterate

1. **Manual test**:
   - Launch the app, open “Unit Conversions,” add a new ingredient/unit/factor, save → check your `conversions.json`.
   - Run your meal-planner → generate the shopping list → confirm conversions behave as expected.
2. **Unit tests** (optional):
   - Write a pytest for `_convert_qty()` that loads a test JSON and verifies known cases (e.g. 16 tbsp → 2 sticks).
3. **Error handling**:
   - Ensure invalid input (non-numeric factor) triggers a user warning and doesn’t obliterate your JSON.

## Future Enhancements

- **Dynamic reload**: watch `conversions.json` for changes (via `watchdog`) and refresh `_CONVERSIONS` without restarting.
- **Advanced UI**: allow editing multiple units per ingredient in one row (e.g. inline JSON editor or nested tables).
- **Backup/versioning**: before each save, snapshot the old JSON so you can roll back if needed.
