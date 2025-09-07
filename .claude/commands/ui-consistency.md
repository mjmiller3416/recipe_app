---
description: Check MealGenie UI component patterns, recipe interface consistency, and MVVM compliance
argument-hint: @<file-path>
allowed-tools: Read, Write, Edit, Task
---

# MealGenie UI Consistency Check: $ARGUMENTS

**AGENT COORDINATION**: Use **pyside6-frontend-architect** for UI architecture analysis and **architecture-reviewer** for MVVM boundary validation.

Please analyze $ARGUMENTS for MealGenie UI consistency, recipe interface patterns, and MVVM best practices:

## UI Component Structure Analysis

### 1. Component Organization
- Proper separation of concerns within UI components
- Consistent file and class naming conventions
- Appropriate component size and complexity
- Clear component responsibilities

### 2. Recipe Domain State Management
- Proper use of recipe ViewModels vs direct recipe data manipulation
- Consistent patterns for handling recipe form input and ingredient parsing
- Appropriate separation between UI state and recipe business data
- Error state handling consistency for recipe validation and meal planning failures

### 3. MealGenie Styling Consistency  
- Consistent use of Material3 theme system across recipe cards and meal widgets
- Proper separation of styling concerns in recipe browsing and meal planning interfaces
- Reuse of common styling patterns for ingredient lists, nutrition displays, and dietary tags
- Appropriate use of MealGenie style constants vs hardcoded values in recipe components

### 4. Recipe UI Patterns
- Consistent recipe error message display across forms and validation
- Uniform loading states for recipe browsing, image loading, and meal plan generation
- Standardized user feedback patterns for recipe creation, editing, and meal planning
- Consistent navigation patterns between recipe views, meal planning, and shopping lists

### 5. Component Reusability
- Opportunities for component abstraction
- Proper use of existing composite components
- Identification of repeated UI patterns
- Suggestions for new reusable components

## UI Architecture Patterns

### 6. View Model Usage
- Proper separation between view logic and presentation
- Consistent view model patterns
- Appropriate data binding approaches
- State management best practices

### 7. Dialog and Navigation Management
- Consistent use of dialog managers
- Proper navigation flow patterns
- Appropriate use of navigation managers
- Error handling in navigation flows

## Output Format
Provide:
1. **Consistency issues**: Deviations from established patterns
2. **Improvement suggestions**: Specific recommendations for better consistency
3. **Reusability opportunities**: Code that could be abstracted into reusable components
4. **Best practices**: Recommendations aligned with your UI architecture
5. **Priority fixes**: Most important consistency issues to address first
