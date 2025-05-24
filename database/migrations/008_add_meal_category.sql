-- migrations/008_add_meal_category.sql

ALTER TABLE recipes
  ADD COLUMN meal_category TEXT;

-- Set default values for existing recipes
UPDATE recipes 
SET meal_category = 'Dinner' 
WHERE meal_category IS NULL;

-- Make the column NOT NULL after setting defaults
-- Note: SQLite doesn't support ALTER COLUMN, so we'll handle this in the model validation