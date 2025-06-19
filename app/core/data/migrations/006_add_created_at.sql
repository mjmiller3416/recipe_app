-- migrations/006_add_created_at_to_recipes.sql

ALTER TABLE recipes
  ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;