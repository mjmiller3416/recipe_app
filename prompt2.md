# Recipe Card Context Menu Implementation

Create a context menu for recipe cards in the Browse Recipes view. The menu should include the following options:

## Menu Options

### 1. View Full Recipe

Opens the `ViewRecipe` class for the selected recipe.

### 2. Favorite / Unfavorite Recipe

- Toggles the recipe's favorite status using existing favorite/unfavorite functions
- When a recipe is favorited, this option should change to **Unfavorite Recipe**

### 3. Delete Recipe

- Permanently deletes the recipe from the database
- Use existing model functions for deletion; if missing, implement according to the structure and conventions in `app/core/`

### 4. Edit Recipe

**Placeholder only.** When clicked, print to the terminal:

```
Editing Recipe with {ID}
```

> **Note:** Do not implement editing functionality yet.

### 5. Add to Meal Plan → [Submenus]

This option includes nested submenus:

#### First Level Submenu
- Lists all existing meals

#### Second Level Submenu (per meal)
- Lists recipe slots (e.g., "Side Dish 2", "Side Dish 3")
- Show all slots, but only available slots should be selectable
- If a slot is empty, indicate it is empty/available
- Show existing recipes already assigned to that meal for clarity

## Implementation Requirements

- Context menu should appear on right-click of recipe cards
- Menu items should be dynamically updated based on recipe state (favorited/unfavorited)
- Proper error handling for all operations
- Follow existing application patterns and conventions
