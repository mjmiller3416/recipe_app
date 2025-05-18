-- Create the shopping_states table to persist checkbox state for ingredients
CREATE TABLE IF NOT EXISTS shopping_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    checked BOOLEAN NOT NULL DEFAULT 0
);