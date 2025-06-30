#!/bin/bash

echo "🔧 Setting up Python packages..."

# Python packages
pip show PySide6 > /dev/null 2>&1 || pip install PySide6==6.6.1
pip show pydantic > /dev/null 2>&1 || pip install pydantic==2.6.4
pip show pytest > /dev/null 2>&1 || pip install pytest==8.2.1
pip show colorlog > /dev/null 2>&1 || pip install colorlog
pip show PySide6-Fluent-Widgets > /dev/null 2>&1 || pip install PySide6-Fluent-Widgets

echo "✅ Python packages installed."

echo "🧱 Installing system libraries (if needed)..."

# Detect package manager and install Linux deps
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y libegl1 libgl1
    else
        echo "⚠️ Detected Linux, but not a Debian-based system. Please install the following manually:"
        echo "  - libegl1"
        echo "  - libgl1"
    fi
else
    echo "ℹ️ Skipping system packages — not required for macOS or Windows."
fi

echo "✅ Setup complete."
