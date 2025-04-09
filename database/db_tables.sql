CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL,
    recipe_category TEXT NOT NULL,
    total_time INTEGER,
    servings INTEGER,
    directions TEXT,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL,
    ingredient_category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_selection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_name TEXT NOT NULL,
    main_recipe_id INTEGER NOT NULL,
    side_recipe_1 INTEGER,
    side_recipe_2 INTEGER,
    side_recipe_3 INTEGER,
    FOREIGN KEY (main_recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (side_recipe_1) REFERENCES recipes(id),
    FOREIGN KEY (side_recipe_2) REFERENCES recipes(id),
    FOREIGN KEY (side_recipe_3) REFERENCES recipes(id)
);

CREATE TABLE IF NOT EXISTS shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    have BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS weekly_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL,    -- if quantity/unit are recipe-specific overrides
    unit TEXT,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);