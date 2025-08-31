# Code Review Guide

This document describes how to request and scope single-file code reviews for the **MealGenie** project.
It is referenced by [CLAUDE.md](../CLAUDE.md) and acts as the canonical review policy.

---

# Code Review Guide
This guide defines how to scope **single-file reviews** within the existing workspace.

---

## Review Goals (priority order)

1. **Bugs & Conflicts**
   - Locate actual or likely defects.
   - Provide small, targeted fixes only.

2. **Error Handling**
   - Fail fast for internal logic; raise errors instead of silent recovery.
   - Use try/except only at boundary calls (I/O, DB, APIs, user input).

3. **Redundancy**
   - Identify repeated logic and centralize where possible.
   - Prefer existing helpers from `app/core/utils/*` or services.

4. **Optimizations**
   - Optimize **only** when readability and clarity are maintained.
   - Avoid clever one-liners or speculative abstractions.

---

## House Style

- **Simple > Clever**: explicit, predictable code over “smart” solutions.
- **Error handling**: fail early for programmer errors; handle user/runtime errors gracefully.
- **Naming**: names should make sense to future-you at 11 PM.
- **Logging**: prefer centralized, clear logging over scattered try/except.
- **Predictability**: revisitability matters — boring solutions age better.

---

## Reviewer Checklist

- [ ] Are bugs or conflicts clearly addressed?
- [ ] Is error handling boundary-only and consistent?
- [ ] Does this reuse existing helpers instead of duplicating logic?
- [ ] Is the code predictable and easy to revisit later?
- [ ] Are optimizations balanced against clarity?

---

## Context

- Solo developer; optimize for single-person maintainability.
- Utilities live in `app/core/utils/`.
- Keep changes scoped to the requested file unless refactors reduce overall complexity.


---

## Reviewer Checklist

Before approving a PR, confirm the following:

- [ ] Bugs and conflicts are addressed
- [ ] Error handling aligns with fail-fast vs boundary-only guidelines
- [ ] Reuses existing helpers, services, or utilities when possible
- [ ] Code is optimized **without** hurting clarity
- [ ] Adheres to naming, style, and QSS placeholder rules
- [ ] Changes comply with [CLAUDE.md](../CLAUDE.md) safety rails
