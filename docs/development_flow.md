# MealGenie Documentation

## 1. Description

MealGenie is a PySide6 application for planning meals, managing recipes, and creating shopping lists. This directory contains reference material for contributors and maintainers. *Refer to the `docs/` folder for more details.*

## 2. Usage

Run `python main.py` to launch the application. Development utilities can be found under the `scripts/` directory.

## 3. Dependencies

* Python 3.11+
* PySide6 == 6.6.1
* pydantic == 2.6.4
* pytest == 8.2.1
* colorlog == latest

🔸 **Linux users only**: The following system packages may be required to support PySide6 in headless or offscreen environments (e.g., CI/CD):

* `libegl1`
* `libgl1`

To install all required Python dependencies, run:

```bash
./setup.sh
```

## 4. Warnings

The UI requires a working Qt environment.

💡 On **Debian-based Linux systems**, you may need to install required system libraries using:

```bash
sudo apt-get install libegl1 libgl1
```

The test suite uses `QT_QPA_PLATFORM=offscreen` to support headless testing environments (e.g., GitHub Actions, Docker containers).

## 5. Examples

```bash
# install dependencies
bash setup.sh

# run app
python main.py

# run tests in headless mode
QT_QPA_PLATFORM=offscreen pytest
```

---

# Development Flow

## 1. Description

This document outlines the recommended workflow for contributing to MealGenie.

## 2. Workflow

1. Clone the repository and run `setup.sh` to install all required dependencies.
2. Create a feature branch from `main` and commit your changes with clear, descriptive messages.
3. Set `QT_QPA_PLATFORM=offscreen` before running tests to ensure headless compatibility.
4. Use `pytest` to verify your changes.
5. Open a pull request targeting the `main` branch for code review.

## 3. Dependencies

* Git
* Bash shell
* Python 3.11+ with all packages installed via `setup.sh`
* Linux: `libegl1`, `libgl1` may be required for UI tests

## 4. Warnings

🚫 Do **not** push directly to `main`. Always create a branch and open a pull request.
✅ Ensure tests pass locally before submitting a PR.

## 5. Examples

```bash
# install requirements
bash setup.sh

# run tests in headless mode
QT_QPA_PLATFORM=offscreen pytest

# create and push new branch
git checkout -b feature/my-awesome-feature
git push origin feature/my-awesome-feature
```
