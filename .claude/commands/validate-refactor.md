---
description: Final validation of completed refactoring tasks
argument-hint: @<completed-task-file-path>
allowed-tools: Read, Bash, Task
---

# Validate Refactor: $ARGUMENTS

## Validation Overview
This command performs comprehensive validation of completed refactoring tasks to ensure:
- All original review issues are resolved
- Code quality standards are met
- Architectural integrity is maintained
- Tests pass and coverage is maintained

Please read the completed task file $ARGUMENTS and perform thorough validation of all implemented changes.

## Validation Process

### 1. Task Completion Verification
- Read the completed task file and verify all tasks are marked as completed
- Check that no critical or high-priority tasks were skipped
- Validate that implementation notes are provided for each completed task
- Ensure any deviations from the original plan are properly documented

### 2. Automated Quality Checks
Run the following automated checks and document results:

```bash
# Import organization
isort . --check-only --diff

# Test execution
pytest -v

# Code coverage (if available)
pytest --cov=app --cov-report=term-missing
```

### 3. Architecture Validation
Use the **architecture-reviewer** agent to:
- Validate that layer boundaries are respected
- Check for any new architectural violations
- Ensure imports follow MealGenie patterns
- Verify MVVM architecture compliance

### 4. Original Issue Resolution
- Cross-reference with the original review file
- Verify each critical and major issue has been addressed
- Check that suggested improvements have been implemented
- Ensure no new issues have been introduced

### 5. Manual Spot Checks
Perform targeted manual reviews of:
- Modified files for code quality and consistency
- New files for architectural compliance
- Test files for adequate coverage
- Documentation updates (if applicable)

## Validation Report Format

Create a validation report at `.claude/reviews/validation-$(date +%Y-%m-%d)-[filename].md`:

```markdown
# Refactoring Validation Report

## Summary
- **Original Review**: [Link to original review file]
- **Refactor Plan**: [Link to plan file]
- **Completed Tasks**: [Link to completed task file]
- **Validation Date**: $(date +%Y-%m-%d)
- **Overall Status**: PASSED / FAILED

## Automated Checks
- **Import Sorting** (`isort .`): PASSED / FAILED
- **Tests** (`pytest`): PASSED / FAILED [X/Y tests passed]
- **Code Coverage**: [Coverage percentage if available]

## Architecture Review
- **Layer Boundaries**: COMPLIANT / VIOLATIONS FOUND
- **Import Patterns**: CORRECT / ISSUES FOUND
- **MVVM Architecture**: MAINTAINED / VIOLATIONS FOUND
- **MealGenie Patterns**: FOLLOWED / DEVIATIONS FOUND

## Original Issues Resolution
### Critical Issues RESOLVED / UNRESOLVED
- [List each critical issue and its resolution status]

### Major Issues RESOLVED / UNRESOLVED
- [List each major issue and its resolution status]

### Minor Issues RESOLVED / PARTIALLY RESOLVED / UNRESOLVED
- [List each minor issue and its resolution status]

## New Issues Detected
- [List any new problems introduced during refactoring]

## Files Modified
- [List of all files changed with brief description of changes]

## Files Created
- [List of new files with their purpose]

## Recommendations
### Immediate Actions Required
- [Any critical issues that must be fixed]

### Future Improvements
- [Suggestions for follow-up work]

### Technical Debt
- [Any technical debt that remains or was introduced]

## Quality Metrics
- **Code Quality**: Improved / Maintained / Degraded
- **Test Coverage**: [Before/After if measurable]
- **Performance Impact**: None / Positive / Negative / Unknown
- **Maintainability**: Improved / Maintained / Degraded

## Final Approval
- [ ] All critical issues resolved
- [ ] No architectural violations introduced
- [ ] Tests pass consistently
- [ ] Code follows project standards
- [ ] Documentation is adequate

**Final Status**: APPROVED FOR PRODUCTION / REQUIRES ADDITIONAL WORK

## Sign-off
**Validated by**: Claude Code Architecture Validation
**Date**: $(date +%Y-%m-%d %H:%M:%S)
**Next Action**: [Ready for merge/deployment OR List required fixes]
```

## Validation Guidelines

- **Be thorough but practical** - Focus on issues that impact functionality, maintainability, or architecture
- **Document everything** - Provide clear evidence for all findings
- **Prioritize issues** - Critical problems block approval, minor issues can be noted for future work
- **Cross-reference thoroughly** - Ensure every original issue is accounted for
- **Test comprehensively** - Don't approve without successful test execution

## Agent Usage
- Use **architecture-reviewer** agent for comprehensive architectural validation
- Use **test-recipe-specialist** agent if test-related issues are found
- Use **general-purpose** agent for any additional investigation needed

## Success Criteria
The refactoring is considered validated when:
1. All automated checks pass
2. No critical or major architectural violations exist
3. All original critical and high-priority issues are resolved
4. Tests pass consistently
5. No significant new issues were introduced

Only approve refactoring that meets these criteria. Document any exceptions clearly with justification.
