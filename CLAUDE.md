# CLAUDE.md
_Project configuration & rules for AI contributions_

This file is the contract Claude must follow when working in the **MealGenie** repo. If a request conflicts with this file, Claude must surface the conflict and ask for approval before proceeding.

---

## 1) Tech Stack (authoritative)
- **Language:** Python 3.12
- **Desktop UI:** PySide6 (Qt)
- **ORM & Migrations:** SQLAlchemy 2.x + Alembic
- **DB:** SQLite (dev)
- **Styling:** QSS using Material 3 role placeholders (see §4)
- **Tests:** pytest (when present)
- **Editor:** VS Code (with custom QSS syntax support)
- **CLI:** `manage.py` (see §3) — do not invent commands/flags

---

## 2) Project Structure (authoritative)

```
recipe_app/
├─ _data_files/
│  ├─ recipe_images/
│  ├─ temp_crops/
│  ├─ user_profile/
│  ├─ user_settings.json
│  └─ user_settings.py
├─ _dev_tools/
├─ _scripts/
├─ _test/
├─ app/
│  ├─ assets/
│  ├─ config/
│  ├─ core/
│  │  ├─ database/
│  │  ├─ dtos/
│  │  ├─ models/
│  │  ├─ repositories/
│  │  ├─ services/
│  │  └─ utils/
│  ├─ style/
│  │  ├─ animation/
│  │  ├─ effects/
│  │  ├─ icon/
│  │  └─ theme/
│  ├─ ui/
│  │  ├─ components/
│  │  │  ├─ composite/
│  │  │  ├─ dialogs/
│  │  │  ├─ images/
│  │  │  ├─ inputs/
│  │  │  ├─ layout/
│  │  │  ├─ navigation/
│  │  │  └─ widgets/
│  │  ├─ models/
│  │  ├─ services/
│  │  ├─ utils/
│  │  └─ views/
│  └─ main_window.py
└─ main.py
```

### Canonical pointers
- **DB session/engine:** `app/core/database/db.py`
- **Models:** `app/core/models/`
- **DTOs:** `app/core/dtos/`
- **Repositories:** `app/core/repositories/`
- **Services:** `app/core/services/`
- **Core utils:** `app/core/utils/`
- **Theme controller:** `app/style/theme_controller.py`
- **QSS loader:** `app/style/theme/style_sheet.py`
- **Icon system:** `app/style/icon/icon.py`
- **UI utils:** `app/ui/utils/`
- **App views:** `app/ui/views/`
- **Logging:** `_dev_tools/debug_logger.py`

> Reuse existing utilities before creating new ones. Search `app/core/utils/` and `app/ui/utils/` first.

---

## 3) Commands (do not guess)

```bash
python manage.py --help                 # Show help and available commands
python manage.py db                     # Database management commands

# Database subcommands
python manage.py db migrate             # Apply database migrations using Alembic
python manage.py db seed                # Populate with mock recipe data
python manage.py db reset               # Reset database (drops all recipe data)
python manage.py db status              # Show database status and recipe count

# Options
python manage.py db seed --recipes 50   # Create 50 recipes (default: 25)
python manage.py db seed --no-realistic # Use simple data (no Faker)
python manage.py db seed --clear        # Clear existing recipes first

python manage.py db reset --confirm     # Skip confirmation prompt
python manage.py db reset --seed        # Add sample data after reset
```

If a command is not listed here, pause and request it to be added.

---

## 4) Code Style & Conventions (strict)
- **Line length:** 110
- **Public API naming:** **camelCase** (Qt convention)
- **Internal/private Python:**
    - Use snake_case for internal implementation details unless matching surrounding code.
    - Prefix private methods and attributes with an underscore (_method_name).
    - “Protected” methods intended for subclass overrides should also use a single underscore.
    - Double underscores (__name) are not recommended unless name-mangling is required.
    - Always default to public camelCase naming for Qt-facing APIs, signals, and slots.
- **Imports:** stdlib → third-party → local; prefer absolute imports
- **Docstrings:** Google-style for public classes/functions
- **Small, explicit functions > clever abstractions**
- **Error handling:** fail fast for programmer errors; handle boundary I/O gracefully
- **Before adding helpers:** check `app/core/utils/` and `app/ui/utils/` first

### QSS placeholders (Material 3 roles)
Use placeholders exactly as defined (no hardcoded colors).

---
## 5) Repository Etiquette & Branch Strategy (authoritative)

### 5.1 Branch types & names

- `feature/<topic-or-ticket>-short-description` — new functionality
- `bugfix/<issue-or-ticket>-short-description` — fixes that are not production emergencies
- `hotfix/<issue>-short-description` — production-breaking issues only
- `refactor/<area>-short-description` — non-behavioral code reorganization
- `chore/<task>-short-description` — tooling, config, CI, docs
- `experiment/<spike>-short-description` — throwaway spikes (may never merge)

### 5.2 Branch lifecycle rules

- No direct commits to `main`
- Keep feature branches up to date with `main` (fast-forward or rebase; be consistent within the branch)
- Open PRs early; prefer smaller, focused diffs
- Delete branches after merge to keep the repo tidy

### 5.3 Decision logic (Claude MUST follow before any change)

- Read current branch:

```bash
git rev-parse --abbrev-ref HEAD
```

- Derive task scope from the Scope Summary (see §8)
- Decide where to commit:
  - If the task belongs to the same topic as the current branch and stays within the change budget (§9) → use the current branch
  - If the task is logically separate (different feature/bug/chore), or it exceeds the budget, or it touches guarded paths requiring approval (§9) → create a new branch
  - If the task is a prod emergency → create a `hotfix/` branch off the latest `main`
- If a branch change is needed, propose and run exact commands (see 5.4).

### 5.4 Commands Claude should propose when switching/creating branches

Always show details:

```bash
# Ensure clean state
git status

# Update main
git fetch origin
git checkout main
git pull --ff-only origin main

# Create a new branch from main
git checkout -b feature/<topic>-<short-description>

# OR, if continuing on current feature branch is valid
git checkout feature/<topic>-<short-description>
git pull --ff-only origin feature/<topic>-<short-description>

# Link to issue (if applicable)
# (document issue ID in PR description)
```

### 5.5 Examples

- You’re on `feature/meal-planner-tabs` and asked to fix an unrelated seeding bug → create `bugfix/seed-defaults-off-by-one`
- You’re on `feature/iconkit-refresh` and asked to tweak an icon color var (same topic, tiny diff) → keep current branch
- Schema change found mid-task (guarded) → pause, propose `feature/recipe-schema-add-image-attrib` and request approval

---

## 6) Do Not Touch (hard rules)
- Do not modify existing Alembic migration files retroactively
- Do not change or move canonical paths in §2 without approval
- Do not hardcode colors; use Material 3 placeholders (§4)
- Do not alter `.env`, secrets, API keys, or DB URLs
- Do not rewrite working legacy components/config unless the task explicitly requests it
- Do not duplicate helpers; extend existing ones in `app/core/utils/` or `app/ui/utils/`
- Do not change bootstrapping in `main.py` or `app/main_window.py` unless scoped in task

---

## 7) Review Policy (embedded summary)
For single-file changes, prioritize:
1) **Bugs & conflicts** → small, targeted fixes
2) **Error handling** → fail fast internally; try/except only at I/O boundaries
3) **Redundancy** → consolidate; prefer existing helpers/services
4) **Optimizations** → only if clarity is maintained; avoid clever one-liners

See full guide: `docs/review_guide.md`

---

## 8) Interaction Rules (how Claude must work)
- Before making changes: produce a **Scope Summary** + **Todo List**
- Patch must be **diff-only** and respect the change budget (§9)
- Always confirm helpers don’t already exist
- Ask clarifying questions before assuming implementation

---

## 9) Safety Rails (AI-optimized)
- **Call-before-write:** For these paths, propose changes and wait for approval:
  - `app/style/theme_controller.py`
  - `app/style/theme/style_sheet.py`
  - `app/core/database/db.py`
  - `app/core/models/` & `app/core/repositories/` schema changes
  - any existing Alembic migration
- **Reuse-first rule:** If an existing helper covers ≥70% of needs, extend it
- **Ambiguity rule:** If command/path/flag isn’t listed, stop and ask

---

## 10) Testing & Verification
- After DB changes: `python manage.py db status`
- After data updates: run `db seed` variants for sanity checks
- For UI/QSS: confirm theme placeholders; no hardcoded colors
- Add/update tests in `_test/` when feasible

---

## 11) PR Template
**Summary**
What changed and why.

**Scope & Constraints**
Files touched; risks; out-of-scope.

**Checklist**
- [ ] Followed Review Policy (§7)
- [ ] Stayed within change budget (§9)
- [ ] Reused helpers (§2, §8)
- [ ] Ran verification commands (§10)

**Commands & Results**
Paste exact commands and outputs.

---

## 12) When to Refuse
- If request conflicts with §6
- If change exceeds §9 without approval
- If ambiguity remains after one clarifying question
