-- migrations/004_add_saved_meal_state.sql
CREATE TABLE IF NOT EXISTS saved_meal_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id INTEGER NOT NULL
);
