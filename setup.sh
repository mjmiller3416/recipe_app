#!/bin/bash

# Only install if not already installed
pip show PySide6 > /dev/null 2>&1 || pip install PySide6==6.6.1
pip show pydantic > /dev/null 2>&1 || pip install pydantic==2.6.4
pip show pytest > /dev/null 2>&1 || pip install pytest==8.2.1