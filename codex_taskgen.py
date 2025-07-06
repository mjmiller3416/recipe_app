"""
codex_taskgen.py

Generate Codex-ready prompt templates for MealGenie tasks.
Run from terminal and paste output directly into Codex/ChatGPT.
"""

import argparse
from datetime import datetime

import pyperclip

# ─── Project Info (Edit This If Needed) ────────────────────────────────────────

PROJECT_STRUCTURE = """
📁 MealGenie Project

app/
├── core/
│   ├── models/ (recipe, ingredient, meal_selection, etc.)
│   ├── dtos/ (recipe_dtos, planner_dtos, shopping_dto)
│   ├── repos/ (recipe_repo, planner_repo, shopping_repo)
│   ├── services/ (recipe_service, planner_service, shopping_service)
│   ├── database/ (db.py, base.py, uses Alembic)
│   └── utils/ (validators, platform_utils, singleton_mixin)
├── style_manager/
│   ├── loaders/, stylesheets/, themes/, theme_controller.py
├── ui/
│   ├── views/ (add_recipes, view_recipes, meal_planner, etc.)
│   ├── components/
│   │   ├── recipe_card/
│   │   ├── dialogs/
│   │   ├── forms/
│   │   ├── inputs/
│   │   └── widgets/ (ct_button, ct_icon, etc.)
│   ├── layout/, navigation/, helpers/, services/
├── main_window.py

tests/
├── core/ (models, repos, services)
├── ui/ (components, pages)
├── test_integration.py, test_full_integration.py

misc/
├── scripts/
├── data_files/
├── main.py
"""

CONTEXT_SUMMARY = """\
- SQLAlchemy 2.0 async ORM for all models
- Pydantic DTOs used for validation
- Repository and Service layer architecture
- UI is built with PySide6 and custom QSS styling
- Tests use Pytest and Pytest-Qt
"""

RULES_DEFAULT = """\
- Follow PEP8 formatting
- Use proper type hints
- Use Google-style docstrings
- Keep prompt under 150 lines unless instructed otherwise
"""

# ─── Prompt Generator ──────────────────────────────────────────────────────────

def generate_prompt(task: str) -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    prompt = f"""## 🍽️ MealGenie Codex Prompt

### 🕒 Created: {timestamp}

### 🎯 Task
{task.strip()}

### 📁 Project Structure
{PROJECT_STRUCTURE.strip()}

### 🧠 Context Summary
{CONTEXT_SUMMARY.strip()}

### ✅ Rules
{RULES_DEFAULT.strip()}
"""
    return prompt

# ─── CLI Logic ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate a Codex prompt for MealGenie.")
    parser.add_argument("task", type=str, nargs="+", help="Describe the task for Codex")
    args = parser.parse_args()
    task_text = " ".join(args.task)

    prompt = generate_prompt(task_text)
    pyperclip.copy(prompt)

    print("\n✅ Codex prompt generated and copied to clipboard!\n")
    print(prompt)

if __name__ == "__main__":
    main()
