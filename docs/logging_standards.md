# Logging Standards and Guidelines

## Overview

This document establishes comprehensive logging standards for the Recipe App project using our custom DebugLogger. Proper logging is essential for debugging, monitoring, and maintaining the application.

## Log Levels and Usage

### 🔵 DEBUG
**Purpose**: Detailed diagnostic information for development and troubleshooting
**When to use**:
- Function entry/exit in complex operations
- Variable values during complex calculations
- State transitions in theme/icon systems
- Cache operations and hit/miss information
- Database query details

**Examples**:
```python
DebugLogger.log("Processing {recipe_count} recipes for user {user_id}", "debug")
DebugLogger.log("Cache hit for icon {icon_name} with color {color}", "debug")
DebugLogger.log("Entering {method_name} with parameters: {params}", "debug")
```

### 🟢 INFO
**Purpose**: General application flow and significant events
**When to use**:
- Application startup/shutdown
- Feature initialization
- Successful operations (save, load, export)
- User actions (navigation, settings changes)
- Performance metrics and timing

**Examples**:
```python
DebugLogger.log("Theme set to color: {color}, mode: {mode}", "info")
DebugLogger.log("Recipe '{recipe_name}' saved successfully", "info")
DebugLogger.log("Application startup completed in {startup_time}s", "info")
```

### 🟡 WARNING
**Purpose**: Potentially problematic situations that don't prevent operation
**When to use**:
- Fallback operations being used
- Deprecated methods being called
- Missing optional resources
- Configuration issues that have defaults
- Performance concerns

**Examples**:
```python
DebugLogger.log("SVG file {filename} missing fill attribute, injecting default", "warning")
DebugLogger.log("Database migration took {duration}s - consider optimization", "warning")
DebugLogger.log("Recipe image not found, using placeholder", "warning")
```

### 🔴 ERROR
**Purpose**: Error conditions that prevent specific operations but don't crash the app
**When to use**:
- File I/O failures
- Database operation failures
- Network/API errors
- Invalid user input that can't be processed
- Resource loading failures

**Examples**:
```python
DebugLogger.log("Failed to load recipe {recipe_id}: {error}", "error")
DebugLogger.log("Database connection lost, retrying...", "error")
DebugLogger.log("Invalid image format for {filename}: {format}", "error")
```

### 🔥 CRITICAL
**Purpose**: Severe errors that may cause application termination
**When to use**:
- Database corruption
- System resource exhaustion
- Security violations
- Fatal configuration errors
- Unrecoverable exceptions

**Examples**:
```python
DebugLogger.log("Database corrupted, unable to continue", "critical")
DebugLogger.log("Out of memory during image processing", "critical")
DebugLogger.log_and_raise("Configuration file missing critical settings", ValueError)
```

## Logging Patterns by Module

### Theme Management System
```python
# Theme changes (INFO)
DebugLogger.log("Theme changed from {old_theme} to {new_theme}", "info")

# Icon loading (DEBUG)
DebugLogger.log("Loading icon {icon_name} with color {color}", "debug")

# Cache operations (DEBUG)
DebugLogger.log("Cache cleared ({item_count} items)", "debug")

# SVG processing issues (WARNING)
DebugLogger.log("SVG {filename} missing fill attribute, auto-injecting", "warning")

# Icon loading failures (ERROR)
DebugLogger.log("Failed to load icon {icon_path}: {error}", "error")
```

### Database Operations
```python
# Query execution (DEBUG)
DebugLogger.log("Executing query: {query} with params: {params}", "debug")

# Successful operations (INFO)
DebugLogger.log("Saved {record_count} recipes to database", "info")

# Connection issues (WARNING)
DebugLogger.log("Database connection slow ({duration}s), consider pooling", "warning")

# Query failures (ERROR)
DebugLogger.log("Query failed: {query}, error: {error}", "error")

# Database corruption (CRITICAL)
DebugLogger.log("Database integrity check failed: {details}", "critical")
```

### UI Components
```python
# Widget initialization (DEBUG)
DebugLogger.log("Initializing {widget_name} with {param_count} parameters", "debug")

# User interactions (INFO)
DebugLogger.log("User navigated to {page_name} page", "info")

# Layout issues (WARNING)
DebugLogger.log("Widget {widget_name} size constraints violated", "warning")

# Widget creation failures (ERROR)
DebugLogger.log("Failed to create widget {widget_type}: {error}", "error")
```

### File Operations
```python
# File access (DEBUG)
DebugLogger.log("Reading file {file_path} ({file_size} bytes)", "debug")

# Successful operations (INFO)
DebugLogger.log("Exported {record_count} recipes to {file_path}", "info")

# Missing files (WARNING)
DebugLogger.log("Config file {file_path} not found, using defaults", "warning")

# File operation failures (ERROR)
DebugLogger.log("Cannot write to {file_path}: {error}", "error")
```

## Best Practices

### 1. Use Variable Substitution
✅ **Good**: `DebugLogger.log("Processing {item_count} items", "info")`
❌ **Bad**: `DebugLogger.log(f"Processing {item_count} items", "info")`

*The DebugLogger handles variable substitution and provides better formatting*

### 2. Include Context
✅ **Good**: `DebugLogger.log("Recipe {recipe_id} validation failed: {error}", "error")`
❌ **Bad**: `DebugLogger.log("Validation failed", "error")`

### 3. Log State Changes
```python
def set_theme(self, color: Color, mode: Mode):
    old_color, old_mode = self.current_color, self.current_mode
    DebugLogger.log("Changing theme from {old_color}/{old_mode} to {color}/{mode}", "info")
    # ... implementation
    DebugLogger.log("Theme change completed successfully", "debug")
```

### 4. Log Performance Metrics
```python
start_time = time.time()
# ... operation
duration = time.time() - start_time
DebugLogger.log("Operation completed in {duration:.3f}s", "info")
```

### 5. Use log_and_raise for Critical Errors
```python
if not self.database_connection:
    DebugLogger.log_and_raise("Database connection required but not available", ConnectionError)
```

### 6. Don't Log Sensitive Information
❌ **Never log**: Passwords, API keys, personal data, file contents
✅ **Safe to log**: File paths, object names, counts, durations

## Log Level Configuration

### Development Environment
```python
DebugLogger.set_log_level("DEBUG")  # Show everything
DebugLogger.set_log_file("debug_dev.log")
```

### Testing Environment
```python
DebugLogger.set_log_level("INFO")  # Skip debug noise
DebugLogger.set_log_file("test_run.log")
```

### Production Environment
```python
DebugLogger.set_log_level("WARNING")  # Only issues
DebugLogger.set_log_file("production.log")
```

## Module-Specific Guidelines

### Theme Manager
- **INFO**: Theme changes, system initialization
- **DEBUG**: Icon loading, cache operations, color calculations
- **WARNING**: Missing resources, fallback operations
- **ERROR**: SVG loading failures, theme application failures

### Database Layer
- **INFO**: Connection establishment, bulk operations
- **DEBUG**: Individual queries, connection pooling
- **WARNING**: Slow queries, connection retries
- **ERROR**: Query failures, constraint violations
- **CRITICAL**: Database corruption, connection pool exhaustion

### UI Layer
- **INFO**: Page navigation, major user actions
- **DEBUG**: Widget creation, layout calculations
- **WARNING**: Layout issues, deprecated widget usage
- **ERROR**: Widget creation failures, event handling errors

### Service Layer
- **INFO**: Service initialization, major operations
- **DEBUG**: Method entry/exit, parameter validation
- **WARNING**: Fallback logic, deprecated method usage
- **ERROR**: Service operation failures, external API errors

## Implementation Checklist

- [ ] Replace all hardcoded log level strings with appropriate levels
- [ ] Add missing logging for error conditions
- [ ] Add performance logging for critical operations
- [ ] Remove excessive debug logging from production paths
- [ ] Ensure all exceptions are logged before re-raising
- [ ] Add logging configuration for different environments
- [ ] Document logging conventions in each module's README