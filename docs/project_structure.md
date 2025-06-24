# Project Structure

## 1. Description
An overview of the folder layout and how the application is organised.

## 2. Usage
Navigate the directories to find specific modules. The table below lists key locations.

```
app/
├── assets/          # fonts and icons
├── config/          # application settings and paths
├── core/            # data models, services and utilities
├── style_manager/   # theme controller and QSS loaders
└── ui/              # widgets, pages and helpers
```

## 3. Dependencies
Internal modules import from these locations using absolute imports.

## 4. Warnings
Changing paths in `app/config/paths` may require updating resource references.

## 5. Examples
- Services live in `app/core/services`
- Pydantic models are under `app/core/data/models`
