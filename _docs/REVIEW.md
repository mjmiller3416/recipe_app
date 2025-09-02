# MealGenie Code Review Guide

This document describes how to request and scope **single-file code reviews** for the MealGenie project.
It is referenced by [CLAUDE.md](../CLAUDE.md) and acts as the canonical review and refactor policy.

---

# Code Review Guide
This guide defines how to scope **single-file reviews** within the existing workspace and maintain strict separation of concerns.

---

## **1. Review Goals (Priority Order)**

1. **Bugs & Conflicts**
   - Locate actual or likely defects.
   - Provide small, targeted fixes only.

2. **Error Handling**
   - Fail fast for internal logic; raise errors instead of silent recovery.
   - Use try/except only at boundary calls (UI events, I/O, DB, APIs, user input).

3. **Redundancy**
   - Identify repeated logic and centralize where possible.
   - Prefer existing helpers from `app/ui/utils/*`, `app/core/utils/*`, or services.

4. **Optimizations**
   - Optimize **only** when readability and clarity are maintained.
   - Avoid clever one-liners or speculative abstractions.

---

## **2. Project Structure Awareness**

Reviews must respect the **layered architecture** of MealGenie:

### **Core Layer (`app/core`)**
- Contains business logic, persistence, and services.
- **Never** import UI code here.
- Includes:
  - `database/` → Engine, migrations, sessions.
  - `dtos/` → Data transfer objects.
  - `models/` → SQLAlchemy ORM models.
  - `repositories/` → Encapsulated data access.
  - `services/` → Business workflows.
  - `utils/` → Core-only helpers.

### **UI Layer (`app/ui`)**
- Presentation, widgets, dialogs, navigation, and view-level services.
- Split into:
  - `components/` → Reusable widgets, inputs, dialogs, layouts.
  - `models/` → Lightweight UI-only models.
  - `services/` → Shared presentation flows (dialogs, navigation, themes).
  - `utils/` → Qt helpers, validators, models, and pure formatting.
  - `views/` → Pages/screens rendered by `MainWindow`.
  - `view_models/` → View-specific orchestration, validation, Core interactions.

### **Style Layer (`app/style`)**
- Animations, effects, icons, and Material3-based QSS themes.

---

## **3. Separation of Concerns**

### **Views (`app/ui/views`)**
- Responsible for **widgets, layouts, signals** only.
- No Core imports; delegate logic to ViewModels.

### **UI Models (`app/ui/models`)**
- Orchestrate between Views and Core services.
- Perform validation, transformation, and async data handling.
- May import `app/core/services` and `app/core/dtos` only.

### **UI Services (`app/ui/services`)**
- Shared presentation behaviors like dialogs, navigation, notifications and themes.
- **Never** import Core services or repositories.

### **Utils (`app/ui/utils` and `app/core/utils`)**
- `ui/utils`: Qt helpers, QValidators, proxy models, and formatting.
- `core/utils`: Persistence, serialization, and business-side helpers.

---

## **4. Reviewer Checklist**

- [ ] Are bugs or conflicts clearly addressed?
- [ ] Is error handling boundary-only and consistent?
- [ ] Does the code respect import boundaries between `ui` and `core`?
- [ ] Does this reuse existing helpers instead of duplicating logic?
- [ ] Are ViewModels used instead of placing Core logic in Views?
- [ ] Are UI services free from Core dependencies?
- [ ] Is the code predictable and easy to revisit later?
- [ ] Is QSS styling consistent with `app/style`?
- [ ] Are optimizations balanced against clarity?

---

## **5. Contextual Awareness**

- Solo developer; optimize for **single-person maintainability**.
- Use `app/ui/utils/*` and `app/core/utils/*` to avoid duplication.
- Refactors should reduce overall complexity, not increase it.

---

## **6. Change Scope Guidelines**

### **Safe Changes (Allowed During Review)**
- Bug fixes and minor optimizations.
- Refactors that reduce code duplication.
- Moving Core logic out of Views into ViewModels.
- Consolidating repeated dialogs into `ui/services/DialogService`.
- Replacing inline styles with variables defined in `app/style`.

### **Out-of-Scope Changes (Require New PR)**
- Schema-level database changes.
- Major service or repository rewrites.
- Full UI layout restructuring.

---

## **7. Review Strategy**

- Keep single-file reviews focused and self-contained.
- Suggest helper extraction into `ui/utils` or `core/utils` when appropriate.
- Always align with [CLAUDE.md](../CLAUDE.md) and [ui_refactor_guide.md](./ui_refactor_guide.md).

---

## **8. Summary**

- **Views are dumb** → render widgets only.
- **ViewModels are smart** → orchestrate data + services.
- **Core is isolated** → business logic only.
- **UI services are sharers** → dialogs, navigation, themes.
- **Utils are helpers** → small, reusable, layered appropriately.

This ensures all refactors maintain **clarity**, **predictability**, and **consistency** across the codebase.
