# MealGenie Documentation

## 1. Description

MealGenie is a PySide6 application for planning meals, managing recipes, and creating shopping lists. This directory contains reference material for contributors and maintainers.

*Refer to the `docs/` folder for more details.*

## 2. Usage

Run `python main.py` to launch the application. Development utilities can be found under the `scripts/` directory.

## 3. Dependencies

### Python Requirements

- **Python 3.11+**
- **PySide6** == 6.6.1
- **pydantic** == 2.6.4
- **pytest** == 8.2.1
- **colorlog** == latest

### System Requirements

🔸 **Linux users only**: The following system packages may be required to support PySide6 in headless or offscreen environments (e.g., CI/CD):

- `libegl1`
- `libgl1`

### Installation

To install all required Python dependencies, run:

```bash
./setup.sh
```

## 4. Warnings

⚠️ The UI requires a working Qt environment.

💡 On **Debian-based Linux systems**, you may need to install required system libraries using:

```bash
sudo apt-get install libegl1 libgl1
```

📝 The test suite uses `QT_QPA_PLATFORM=offscreen` to support headless testing environments (e.g., GitHub Actions, Docker containers).

## 5. Examples

### Development Workflow

```bash
# Install dependencies
bash setup.sh

# Run the application
python main.py

# Run tests in headless mode
QT_QPA_PLATFORM=offscreen pytest
```

### Available Scripts

- **Main Application**: `python main.py`
- **Package Automation**: `python scripts/package_automation.py`
- **Test App Creation**: `python scripts/create_test_app.py`
- **UI Converter**: `python scripts/ui_converter.py`

## 6. Project Structure

For detailed information about the project architecture and data flow, see:

- [`app/core/README.md`](app/core/README.md) - Database & Data Layer Architecture
- [`docs/`](docs/) - Comprehensive documentation
- [`scripts/`](scripts/) - Development and automation tools
- [`tests/`](tests/) - Test suites

## 7. Contributing

Please refer to the documentation in the `docs/` folder for:

- Development workflow
- Style guidelines
- Database design
- Widget guidelines
- Debugging protocols
