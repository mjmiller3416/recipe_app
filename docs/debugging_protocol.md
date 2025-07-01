# Debugging Protocol

## 1. Description
Steps for logging and diagnosing issues during development.

## 2. Usage
- Use `DebugLogger` from `app/core/utils` for structured log messages.
- Run the application with `--test` to start the test harness found in `tests/dev`.

## 3. Dependencies
- colorlog (for coloured output)

## 4. Warnings
Logs may contain file paths; avoid committing sensitive data.

## 5. Examples
```python
from dev_tools import DebugLogger
DebugLogger.log("Something happened", "info")
```
