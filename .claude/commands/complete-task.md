---
description: Execute refactoring tasks outlined in a task markdown file
argument-hint: @<task-file-path>
allowed-tools: Read, Write, Edit, Bash
---

# Complete Task: $ARGUMENTS

## Agent Delegation Strategy
Based on the tasks in the plan, delegate to appropriate specialists:
- **python-backend-architect**: For core/, models/, repositories/, services/ changes
- **pyside6-frontend-architect**: For ui/, view_models/, components/ changes
- **test-recipe-specialist**: For test creation and validation
- **code-refactor-simplifier**: For complex refactoring patterns
- **architecture-reviewer**: Final validation of changes

Please read the task file $ARGUMENTS and execute all the refactoring tasks outlined in the plan.

## Execution Process

### 1. Task File Analysis
- Read and parse the complete task file
- Identify all tasks marked as incomplete
- Understand the implementation sequence and dependencies
- Note any special requirements or constraints

### 2. Pre-Execution Validation
- Verify all referenced files exist
- Check that the current codebase matches the assumptions in the task file
- Identify any changes that may have occurred since the plan was created
- Confirm the development environment is ready

### 3. Task Execution
- Execute tasks in the planned sequence
- Follow the implementation steps exactly as outlined
- Create new files when specified in the plan
- Make code changes following the project's architectural patterns
- Ensure proper import statements and file organization

### 4. Quality Assurance
- Run import sorting: `isort .`
- Run tests: `pytest`
- Use **architecture-reviewer** agent to validate layer boundaries
- Verify that changes follow the MealGenie architectural guidelines
- Check that all critical bugs identified in the original review are resolved
- Ensure code formatting and style consistency

### 5. Progress Tracking
- Mark completed tasks in the task file as you complete them
- Add completion timestamps
- Note any deviations from the original plan
- Document any issues encountered during implementation

## Task Completion Format

As you complete each task, update the task file by changing:

```markdown
- [ ] Task description
```

To:

```markdown
- [x] Task description **COMPLETED** - [Timestamp] - [Brief note about implementation]
```

## Final Documentation

At the end of the task file, add a completion summary:

```markdown
## Execution Summary

**Completion Date**: [Date and time]
**Total Tasks Completed**: [Number]
**Tasks Skipped**: [Number with reasons]
**Issues Encountered**: [Any problems and how they were resolved]
**Additional Changes Made**: [Any changes beyond the original plan]
**Testing Results**: [Summary of test outcomes]

### Files Modified
- [List of all files that were changed]

### Files Created
- [List of any new files created]

### Next Steps
- [Any follow-up work needed]
- [Suggestions for further improvements]

### Validation Results
- [ ] Import sorting passed (`isort .`)
- [ ] Tests passed (`pytest`)
- [ ] Architecture review passed
- [ ] All original review issues resolved

**Status**: COMPLETED

### Cross-Reference Files
- **Original Review**: [Link to review file]
- **Refactor Plan**: $ARGUMENTS
- **Next Step**: Run `validate-refactor.md @[this-file]` for final validation
```

## Implementation Guidelines

- Follow the MealGenie MVVM architecture strictly
- Respect import boundaries (UI layer never imports from app.core directly)
- Use the established naming conventions
- Add appropriate error handling
- Include type hints and docstrings for new code
- Test changes thoroughly before marking tasks complete
- Use specialized agents for domain-specific tasks

## Automated Validation Steps
After completing all tasks, run these validation steps:

1. **Code Quality**: `isort .` to verify import organization
2. **Testing**: `pytest` to ensure all tests pass
3. **Architecture Review**: Use architecture-reviewer agent to validate changes
4. **Final Validation**: Run `validate-refactor.md @[this-completed-file]`

Work through the tasks systematically, ensuring each step is properly implemented before moving to the next. If you encounter any issues that require deviating from the plan, document the changes and rationale clearly in the task file.
