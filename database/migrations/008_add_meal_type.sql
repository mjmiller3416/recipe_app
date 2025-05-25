-- migrations/008_add_meal_type.sql

ALTER TABLE recipes
  ADD COLUMN meal_type TEXT;

-- Set default values for existing recipes
UPDATE recipes 
SET meal_type = 'Dinner' 
WHERE meal_type IS NULL;

-- Make the column NOT NULL after setting defaults
-- Note: SQLite doesn't support ALTER COLUMN, so we'll handle this in the model validation