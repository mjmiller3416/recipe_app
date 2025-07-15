#!/usr/bin/env python3
"""Simple test for template substitution"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from material_colors import generate_theme_dict
from theme_manager import ThemeTemplate

# Test template substitution
test_qss = """
QWidget {
    background-color: {background};
    color: {on_surface};
}
QPushButton {
    background-color: {primary};
    color: {on_primary};
}
"""

print("=== Template Substitution Test ===")
print("Original QSS:")
print(test_qss)

# Generate colors
color_dict = generate_theme_dict("#2196F3", "light")
print("\nColor dictionary:")
for k, v in color_dict.items():
    if k in ["background", "on_surface", "primary", "on_primary"]:
        print(f"  {k}: {v}")

# Apply template using ThemeTemplate
template = ThemeTemplate(test_qss)
result = template.apply_theme("#2196F3", "light")

print("\nProcessed QSS:")
print(result)

# Check if substitution worked
if "{" in result:
    print("\n❌ Some variables were not substituted!")
    remaining = [line for line in result.split('\n') if '{' in line]
    print("Remaining variables:")
    for line in remaining:
        print(f"  {line.strip()}")
else:
    print("\n✅ All variables substituted successfully!")
