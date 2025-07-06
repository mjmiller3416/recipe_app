# MealGenie 🍽️

A modern, cross-platform desktop application for meal planning, recipe management, and shopping list generation built with PySide6.

**Version:** 1.0.0 | **Python:** 3.11+ | **License:** MIT | **Platform:** Windows | macOS | Linux

## 📖 Overview

MealGenie simplifies household meal management by combining structured meal planning with an intuitive, modern interface. Plan your weekly meals, manage your recipe collection, and automatically generate shopping lists - all in one beautifully designed application.

### ✨ Key Features

- **📅 Meal Planning**: Create weekly meal plans with main dishes and up to 3 side dishes per meal
- **🍳 Recipe Management**: Add, edit, and organize recipes with ingredients, directions, and metadata
- **🛒 Smart Shopping Lists**: Automatically generate shopping lists from planned meals with ingredient aggregation
- **❤️ Favorites System**: Mark favorite recipes for quick access
- **🎨 Custom Theming**: Modern, customizable interface with dark/light theme support
- **🔍 Advanced Search**: Filter recipes by category, meal type, and favorites
- **📱 Modern UI**: Frameless window design with custom title bar and collapsible sidebar

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recipe_app
   ```

2. **Install dependencies**
   ```bash
   # Windows (PowerShell)
   .\setup.sh

   # Linux/macOS
   bash setup.sh
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Linux Users Note
You may need to install additional system libraries:
```bash
sudo apt-get install libegl1 libgl1
```

## 🏗️ Architecture

MealGenie follows a clean, modular architecture:

```
recipe_app/
├── app/
│   ├── core/                  # Business logic & data layer
│   │   ├── data/             # Database interface & CRUD utilities
│   │   ├── services/         # Business logic services
│   │   ├── models/           # Pydantic data models
│   │   ├── dtos/             # Data transfer objects
│   │   └── repos/            # Repository pattern implementations
│   ├── ui/                   # User interface components
│   │   ├── components/       # Reusable UI widgets
│   │   ├── views/            # Application pages/screens
│   │   ├── services/         # UI-specific services
│   │   └── helpers/          # UI utility functions
│   ├── style_manager/        # Theme system & styling
│   ├── config/               # Application configuration
│   └── assets/               # Icons, fonts, and other assets
├── data_files/               # User data & temporary files
├── scripts/                  # Automation & utility scripts
├── tests/                    # Test suite (pytest)
├── docs/                     # Documentation
└── dev_tools/                # Development utilities
```

## 📋 Core Features

### 🍳 Recipe Management
- **Add New Recipes**: Rich form with validation for recipe details, ingredients, and cooking directions
- **Recipe Categories**: Organize by meal type (Breakfast, Lunch, Dinner, etc.) and recipe category (Chicken, Beef, Vegetarian, etc.)
- **Image Support**: Upload and crop recipe images
- **Detailed Metadata**: Track cooking time, servings, and favorite status
- **Ingredient Management**: Structured ingredient list with quantities and units

### 📅 Meal Planning
- **Weekly Planning**: Tabbed interface for organizing multiple meals
- **Recipe Assignment**: Select main dishes and up to 3 side dishes per meal
- **Persistent Storage**: Meal plans automatically save and restore between sessions
- **Flexible Planning**: Create custom meal combinations from your recipe collection

### � Shopping List Generation
- **Automatic Aggregation**: Combine ingredients from multiple planned meals
- **Smart Merging**: Aggregate quantities of identical ingredients
- **Manual Items**: Add custom items to your shopping list
- **Category Organization**: Group ingredients by shopping categories (produce, meat, dairy, etc.)
- **Interactive Checklist**: Mark items as purchased during shopping

### 🎨 User Interface
- **Modern Design**: Clean, intuitive interface with custom styling
- **Responsive Layout**: Adaptive design that works on various screen sizes
- **Theme System**: Customizable color schemes and styling
- **Search & Filter**: Advanced filtering by category, meal type, and favorites
- **Frameless Window**: Native-feeling window with custom title bar

## 🛠️ Development

### Development Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd recipe_app
   bash setup.sh
   ```

2. **Run in test mode**
   ```bash
   python main.py --test
   ```

3. **Run tests**
   ```bash
   # Regular testing
   pytest

   # Headless testing (CI/CD)
   QT_QPA_PLATFORM=offscreen pytest
   ```

### Available Scripts

- **Run Application**: `python main.py`
- **Test Mode**: `python main.py --test`
- **Reset Database**: `python main.py --reset`
- **Import Recipes**: `python main.py --import-recipes`
- **Clear Cache**: `python scripts/clear_pycache.py`
- **UI Converter**: `python scripts/ui_converter.py`

### VS Code Tasks

The project includes predefined VS Code tasks for common operations:
- **Run main.py**: Execute the main application
- **Run Test Environment**: Launch in test mode
- **Convert UI Files**: Process Qt Designer files
- **Run QtDesigner**: Launch Qt Designer tool

### Tech Stack

- **Framework**: PySide6 (Qt for Python)
- **Database**: SQLite with Pydantic models
- **Validation**: Pydantic for data validation
- **Testing**: pytest with Qt support
- **Styling**: QSS (Qt Style Sheets)
- **Architecture**: Service-oriented with repository pattern

## 📊 Database Schema

MealGenie uses SQLite with the following core models:

- **Recipe**: Recipe details, metadata, and cooking information
- **Ingredient**: Individual ingredient information and categories
- **RecipeIngredient**: Junction table linking recipes to ingredients with quantities
- **MealSelection**: Meal plans with main and side dish assignments
- **WeeklyMenu**: Weekly meal planning state
- **ShoppingItem**: Shopping list items and status

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test modules
pytest tests/core/
pytest tests/ui/
```

### Test Structure
- **Unit Tests**: Core business logic and models
- **Integration Tests**: Service layer interactions
- **UI Tests**: Widget behavior and user interactions

## 🚢 Deployment

### Packaging (Planned)

Future packaging options will include:
- **Windows**: `.exe` or `.msi` via PyInstaller
- **macOS**: `.app` bundle
- **Linux**: AppImage or Flatpak

## 🔒 Security

- **Input Validation**: Pydantic validation for all user inputs
- **Local Storage**: SQLite database stored locally
- **No Remote Access**: No external API dependencies for core functionality

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and ensure tests pass
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines

- Follow the existing code style and architecture patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PRs

## 📚 Additional Documentation

For detailed information about the project architecture and development:

- [`app/core/README.md`](app/core/README.md) - Database & Data Layer Architecture
- [`docs/`](docs/) - Comprehensive documentation
- [`scripts/`](scripts/) - Development and automation tools
- [`tests/`](tests/) - Test suites
- [`AGENTS.md`](AGENTS.md) - Project overview and development guidelines

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions, issues, or feature requests:

1. **Check existing issues** in the repository
2. **Create a new issue** with detailed information
3. **Provide steps to reproduce** any bugs
4. **Include system information** (OS, Python version, etc.)

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- Icons and assets from various open-source contributors
- Testing framework powered by [pytest](https://pytest.org/)
- Validation handled by [Pydantic](https://pydantic.dev/)

---

**MealGenie** - Making meal planning delicious and simple! 🍽️✨
