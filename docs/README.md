# MealGenie Documentation

## 1. Description
MealGenie is a PySide6 application for planning meals, managing recipes and creating shopping lists. This directory contains reference material for contributors and maintainers.

## 2. Usage
Run `python main.py` to launch the application. Development utilities can be found under the `scripts/` directory.

## 3. Dependencies
- Python 3.11+
- PySide6
- pydantic

Use `./setup.sh` to install the exact versions used in development.

## 4. Warnings
The UI requires a working Qt environment. Some features rely on the bundled SQLite database under `app/core/data`.

## 5. Examples
```bash
# install dependencies
bash setup.sh

# start the app
python main.py
```
