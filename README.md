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
