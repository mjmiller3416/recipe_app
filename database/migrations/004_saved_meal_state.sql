-- This migration adds a new table to store saved meal states.
CREATE TABLE IF NOT EXISTS saved_meal_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id INTEGER NOT NULL
);
