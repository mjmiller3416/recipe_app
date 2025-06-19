-- migrations/007_add_is_favorite_to_recipes.sql

ALTER TABLE recipes
  ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0;