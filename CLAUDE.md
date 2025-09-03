# CLAUDE.md — MealGenie (Agent Rules & Workflow)

> You are Claude Code working inside the **MealGenie** repo. Follow this file **exactly**. These rules **override** defaults. If something conflicts, **this file wins**.

# Workflow
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.

---

## 0) Load Order & Imports

- **At session start**, load this file and the docs referenced with `@` below.
- Subdirectory `CLAUDE.md` files may add local rules. If you read files in that subtree, include the local rules.
- If you modify any imported `@` docs during a session, reload them.

**Always import:**
- `@_docs/REFACTOR.md`  _(UI layer contracts & MVVM rules)_
- `@_docs/REVIEW.md`  _(single‑file review policy & checklist)_

Also note (path references; read on demand):
- `/app/style/`  _(themes, QSS, icons, effects)_
- `/app/ui/*`  _(views, models, components, services, utils)_
- `/app/core/*`  _(models, repositories, services, dtos, database, utils)_

---

## 1) Mission & Architecture (one-screen summary)

**Mission:** A PySide6 desktop app for recipes, planning, and shopping lists with a modern, themeable UI.

**Architecture:** MVVM-ish UI over a layered Core.
- **UI (`app/ui/`)** renders widgets and delegates logic to **UI Models**.
- **Core (`app/core/`)** owns business rules, repositories, and DTOs.
- **Style (`app/style/`)** centralizes theme, icons, animations, effects.

**Import Matrix (must-follow):**
```
ui/views        -> ui/models, ui/services, ui/components, ui/utils, style/*
ui/models       -> app/core/services, app/core/dtos, ui/utils
ui/services     -> ui/components, style/*, ui/utils
ui/utils        -> (pure_* no Qt) or (qt_* with Qt); never import app/core
core/*          -> never import app/ui/*
```
If a change violates this, refactor until it doesn’t. See @_docs/REFACTOR.md.

---

## 2) Golden Workflow (format → lint → test → commit)

For **every** code change:

1. **Implement** change in smallest sensible diff.
2. **Format**: `ruff format .` (or `black .` if configured) and `isort .`
3. **Lint**: `ruff check .` and fix new issues.
4. **Test**: `pytest -q` (or targeted tests).
5. **Commit**: conventional message; branch per Section 6.
6. **Self-check**: run the checklists in Section 7.

> Never skip steps 2–4. If tooling isn’t configured, state that fact and propose the minimal config PR instead of guessing.

---

## 3) Task Types & What To Do

### A) UI Refactor (Views ↔ UI Models)
- **Never** import `app.core.*` in a View. **Move** to UI Model.
- Views: widgets/layouts/signals only. No business logic.
- UI Models: validation, transformation, async/worker orchestration.
- Shared dialogs/navigation/theme → **UI Services**.

### B) Bug Fix
- Minimal diff; add/adjust a **test**; avoid unrelated refactors.
- If fix exposes missing helper, extract into `ui/utils` or `core/utils` (small, named).

### C) Feature
- Define DTOs in Core, service method(s), repo calls; expose through VM; render in View.
- Add tests close to the change; prefer unit + thin integration.

---

## 4) Commands (don’t invent new ones)

**Run app**
```bash
python main.py
```

**Tests**
```bash
pytest
pytest tests/test_x.py::TestCase::test_y
```

**Quality**
```bash
isort .
ruff format . && ruff check .
# (If black is the configured formatter, use it instead of ruff format)
```

**DB / Migrations** (if present)
```bash
alembic upgrade head   # do not add new migrations in UI-only tasks
```

If a command is missing, **ask** or propose a minimal PR to add it.

---

## 5) Style & Conventions

- **Simple > Clever**. Prefer explicit, boring code.
- **Docstrings** on public functions/classes; type hints where reasonable.
- **Logging** via the project’s logger; no stray prints.
- **QSS & Icons** live in `/app/style`; don’t inline hard-coded colors.
- Keep files short: Views ≤ 400 lines, ViewModels ≤ 500 lines; extract helpers.

---

## 6) Git Hygiene

- Branch per task: `refactor/ui/<feature>`, `fix/<bug>`, `feat/<area>`.
- Squash small fixups before PR. Commit messages are imperative:
  `refactor(ui): extract AddRecipeVM and remove core import from view`
- Do **not** push schema changes unless the task explicitly includes them.

---

## 7) Mandatory Checklists

**UI Boundary Check**
- [ ] No `app.core.*` imports in any `app/ui/views/*` file touched.
- [ ] Core calls live in `ui/view_models/*` only.
- [ ] Repeated dialog/notification logic → `ui/services/DialogService`.

**Quality Pass**
- [ ] `isort`, formatter, and linter run, zero new warnings.
- [ ] Tests added/updated. No skipped tests left behind.

**Style & UX**
- [ ] QSS variables used (no hard-coded colors).
- [ ] Signals grouped; long slots broken into helpers.

If any box fails, fix or justify in the PR description.

---

## 8) Canary & Compliance (sanity check)

Once per session, respond with: **“Aye, Captain.”**
If you didn’t, you likely didn’t load this file. Re-load and proceed.

---

## 9) Do‑Not‑Touch (unless explicitly asked)

- Project-wide theme contracts under `/app/style/theme/` (update via Theme/Style PRs).
- Any CI/CD config.
- Database schema/migrations outside explicit DB tasks.

---

## 10) When Unsure

- Prefer adding a tiny helper in `ui/utils` or `core/utils` over sprinkling ad‑hoc logic.
- If crossing a boundary requires contortions, **stop** and propose a mini design note in the PR with options and trade‑offs.
- Keep the conversation short and fresh; start a new session for a new task.

---

## 11) Pinned References

- Architecture & MVVM rules → @_docs/REFACTOR.md
- Review policy & single‑file flow → @_docs/REVIEW.md

---

## 12) Short Rationale

These rules keep UI dumb, UI Models smart, and Core isolated. They make the code predictable, testable, and easier to refactor without spooky action at a distance.
