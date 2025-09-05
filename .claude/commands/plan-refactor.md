---
description: Create a detailed refactoring plan based on code review feedback
argument-hint: @<review-file-path>
allowed-tools: Read, Write
---

# Plan Refactor: $ARGUMENTS

## Agent Usage Strategy
Please use the **project-orchestrator** agent to create comprehensive refactoring plans that coordinate between specialized agents:
- **python-backend-architect** for core/, models/, repositories/, services/ changes
- **pyside6-frontend-architect** for ui/, view_models/, components/ changes  
- **architecture-reviewer** for validation of layer boundaries
- **test-recipe-specialist** for test-related changes

Please read @_docs/ARCHITECTURE.md to understand the project's architectural principles and structure.
Please read the code review file $ARGUMENTS and create a comprehensive refactoring plan based on the suggestions and feedback provided.

## Planning Process

### 1. Review Analysis
- Extract all critical bugs, architectural violations, and improvement suggestions
- Categorize issues by priority (Critical, High, Medium, Low)
- Identify dependencies between different refactoring tasks
- Note any architectural patterns that need to be followed

### 2. Task Breakdown
- Break down complex refactoring items into discrete, actionable tasks
- Sequence tasks to handle dependencies properly (e.g., fix critical bugs before architectural changes)
- Estimate complexity/effort for each task
- Identify which files will be affected by each change

### 3. Implementation Strategy
- Group related changes that can be done together
- Identify which changes require new files to be created
- Plan testing strategy for each refactoring step
- Consider rollback strategies for risky changes

## Output Requirements

Create a detailed markdown file with the following structure:

```markdown
# Refactoring Plan: [Original File Name]

## Overview
- **File**: [Original file path]
- **Review Date**: [Date]
- **Total Tasks**: [Number]
- **Estimated Effort**: [High/Medium/Low]

## Critical Issues (Must Fix)
### Task 1: [Description]
- **Priority**: Critical
- **Files Affected**: [List]
- **Description**: [Detailed description]
- **Implementation Steps**:
  1. [Step 1]
  2. [Step 2]
- **Testing Requirements**: [What to test]
- **Dependencies**: [Any prerequisites]

## High Priority Issues
[Same format as Critical]

## Medium Priority Issues
[Same format as Critical]

## Implementation Sequence
1. [Task order with rationale]
2. [Dependencies explained]

## Architecture Improvements
- [Specific architectural changes needed]
- [New files to create]
- [Import structure changes]

## Testing Strategy
- [Unit tests to add/modify]
- [Integration tests needed]
- [Manual testing requirements]

## Risk Assessment
- [Potential issues]
- [Rollback plan]
- [Mitigation strategies]

## Success Criteria
- [ ] All critical bugs fixed
- [ ] Architecture violations resolved
- [ ] Code follows project patterns
- [ ] Tests pass (`pytest`)
- [ ] Import sorting verified (`isort .`)
- [ ] Performance maintained/improved
- [ ] Architecture review validation passed

## Agent Delegation Plan
- **Tasks for python-backend-architect**: [List core/backend tasks]
- **Tasks for pyside6-frontend-architect**: [List UI/frontend tasks]
- **Tasks for test-recipe-specialist**: [List testing tasks]
- **Final validation**: architecture-reviewer agent
```

## File Creation Instructions

**CRITICAL**: When creating the refactoring plan file:
1. **ALWAYS use the Write tool directly** - NEVER use bash commands like echo, cat, or heredocs
2. **DO NOT use Bash tool** for file creation - this causes quote parsing errors with markdown content
3. Create the file at `.claude/tasks/$(date +%Y-%m-%d)-plan-[filename].md`
4. If the tasks directory doesn't exist, create it first with a separate Write operation
5. Use the Write tool's content parameter directly with the full markdown content

**Example of CORRECT approach:**
```python
Write(file_path=".claude/tasks/2024-12-05-plan-main_window.md", content="# Refactoring Plan\n\nContent here...")
```

**AVOID these approaches that cause errors:**
- `bash: echo "content" > file.md`
- `bash: cat << EOF > file.md`
- Any bash command for writing markdown files

Make the plan actionable and specific - each task should be clear enough that any developer could execute it based on your description.

---
