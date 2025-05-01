-- migrations/002_create_meal_logs.sql
CREATE TABLE IF NOT EXISTS meal_logs (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  meal_selection_id    INTEGER NOT NULL,
  checked_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (meal_selection_id)
    REFERENCES meal_selections(id)
    ON DELETE CASCADE
);
