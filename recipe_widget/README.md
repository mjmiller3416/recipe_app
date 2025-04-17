```
└── 📁recipe_widget
    └── 📁layouts
        └── __init__.py
        └── _large_layout.py *** not yet implemented ***
        └── _medium_layout.py -- layout builder function 
        └── _small_layout.py -- layout builder function
    └── __init__.py
    └── _config.py -- configurration file that constants package based constants 
    └── _full_recipe.py -- dialog style view, that displays the complete recipe (WIP)
    └── _recipe_selection_dialog.py -- dialog style view that displays all recipes. currently calls 
    |                                   ViewRecipes, but only relies on it for a particular layout method 
    |                                   it's using. layout method will eventually be refactored into a 
    |                                   helper function, breaking the dependancy.
    └── _stylesheet.qss -- .qss stylesheet containing visual styling for the RecipeWidget
    └── README.md -- package documentation 
    └── recipe_widget.py -- parent class, contains core functionality, manages supporting logic
```
Order of operations: 


RecipeWidget a subclass of a QFrame -- aside from the required attributes is called and embedded into PySide6 layouts, just as a traditional QFrame is.  

RecipeWidget is a standalone class (WIP) -- It’s only functioning dependency should be a compatible DB to hook into. Outside of DB values, all logic is self contained. 

RecipeWidget accepts the following attributes: 

recipe
    ```Defaults to ‘None’```
    ```Recipe ID that is currently loaded within the RecipeWidget.```

layout_mode
    ```Defaults to “medium”```
    ```“small”, “medium”, & “large” (WIP) layouts```
    ```Visually reformats the layout and style of the widget depending on mode passed. Layouts contain more/less recipe data```
    ```depending on the selected layout e.g. Recipe Name, Servings, Ingredients, etc```

meal_selection
    ```Defaults to ‘False’```
    ```State check to determine correct ‘mousePressEvent’ action```
    ```‘False’, when clicked, open FullRecipe```
    ```‘True’, when clicked, insert recipe details into RecipeWidget.```
    ```Inserted details will be dictated by the layout_mode that was selected.```
    ```Possibly redundant logic and may be able to refactor  to omit for better usability/readability.```

parent
    ```Defaults to ‘None```
    ```Parent class of where the RecipeWidget was called from.```
    ```Possibly remove? Unsure.```
meal_type
    ```Defaults to “main”```
    ```Legacy attribute, now redundant, needs removed.```
    ```A way to track what recipes were “main” dishes and which meals were “side” dishes from within the MealPlanner.```

Order of Operations starting at beginning on Runtime
Order of operations assumes no recipe data has been previously loaded.  


1. Check layout_mode
2. Store layout_mode for later use. 
3. Check recipe 
    ```If NOT ‘None’, load recipe details based on “layout_mode” and relevant ‘Recipe.id’```
    ```If NOT ‘None’, set “meal_selection” to ‘False’```

    ```If ‘None’, set “meal_selection” to ‘True’```
    ```If ‘None’, load as an “empty” RecipeWidget```

	### Note, empty widgets contain only a singular button, whos only functionality is to load the RecipeSelectionDialog class, in order to select a recipe. ###

4. Select the add recipe button
    ```Signal emits```
    ```Triggers RecipeSelectionDialog class``` 
5. Select a recipe
    ```Update recipe attribute with selected ‘Recipe.id’```
    ```“meal_selection” is set to ‘False’```
    ```Store recipe data in a dict, permanently, until RecipeWidget state changes.```
6. Parse recipe data, to determine the appropriate data to load, based on the chosen “layout_mode”
    ```RecipeWidget’s “empty” layout is replaced by the previously stored “layout_mode”```
7. Load appropriate data, based on the existing “layout_mode” is loaded. 
8. RecipeWidget, is now fully loaded with appropriate recipe details based on the “lay_out” mode. 
9. On mousePressEvent
    ```If “meal_selection” = ‘False’ & recipe NOT ‘None’```
        ```Open FullRecipeClass```
    ```Else```  ***this check assume that one cannot be true, unless both are true***
        ```Signal emits```
    ```Triggers RecipeSelectionDialog```

Notes: 

Possible redundancies/legacy attributes in present build. 

“meal_type” is no longer necessary and should be independently managed, within the MealPlanner class (I think) MealPlanner, should be able to determine, within it’s layout, which RecipeWidgets are being dedicated to Main Dishes and which are Side Dishes. That logic doesn’t seem directly connected to the functionality of the RecipeWidget itself. 

“meal_selection” may be redundant. Based on current design, “meal_selection” can be checked, based on the recipe attribute. 
 
	E.g. If recipe is NOT ‘None’, there should never be an instance where “meal_selection” is ‘True’. Same as, if recipe is ‘None’, “meal_selection” should always be ‘True’. 

Additionally, “meal_selection” naming is misleading. RecipeWidget as an independent package has nothing to do with the MealPlanner 

Consider dropping “meal_selection” as an attribute and instead perform a simply check to determine “recipe_selection” 

	E.g. If recipe is NOT ‘None’, recipe_selection is ‘False’ 
		Else recipe_selection is ‘True’ 

When a recipe is loaded to  the RecipeWidget, ALL recipe details, for that recipe should be stored and bound specifically to that particular RecipeWidget. 

### Need some way to track RecipeWidgets, separate multiple widgets logically ###

Once details are stored, only the appropriate details should be loaded based on  the layout chosen. 

After recipe is loaded and RecipeWidget is clicked, a signal will emit and call FullRecipe. It’s at this time, the full recipe details that were earlier stored can be used to fill the the FullRecipe dialog layout. Storing and loading the values in this way, essentially completes two separate tasks, but only requires querying  the db once, unless that card is edited. 

Additional states Edit, and Remove, will be handled by outside classes that use the widget, however may need to implement logic within RecipeWidget to send or recipe signals based on states. 

