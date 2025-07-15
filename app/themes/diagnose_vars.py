#!/usr/bin/env python3
"""Simple diagnostic script to check missing variables"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from material_colors import generate_theme_dict
from theme_manager import ThemeTemplateLoader, ThemeTemplate

# Load the actual base_style.qss template
loader = ThemeTemplateLoader()
template = loader.load_base_style()

print("=== Base Style Template Analysis ===")
print("Template length:", len(template.template_content))

# Get required variables
required_vars = template.get_required_variables()
print(f"Required variables ({len(required_vars)}):")
for var in sorted(required_vars):
    print(f"  {var}")

# Get available variables from color generation
color_dict = generate_theme_dict("#9C27B0", "dark")  # Purple dark
print(f"\nAvailable variables ({len(color_dict)}):")
for var in sorted(color_dict.keys()):
    print(f"  {var}")

# Find missing variables
missing = required_vars - set(color_dict.keys())
print(f"\nMissing variables ({len(missing)}):")
for var in sorted(missing):
    print(f"  ❌ {var}")

# Find extra variables
extra = set(color_dict.keys()) - required_vars
print(f"\nExtra variables ({len(extra)}):")
for var in sorted(extra):
    print(f"  ➕ {var}")

# Test substitution
print("\n=== Testing Substitution ===")
result = template.apply_theme("#9C27B0", "dark")

# Find lines with actual template variables (not CSS blocks)
import re
template_var_pattern = r'\{([^}\n]+)\}'
remaining_template_vars = re.findall(template_var_pattern, result)

print(f"Remaining template variables: {len(remaining_template_vars)}")

if remaining_template_vars:
    print("Unsubstituted template variables:")
    for var in sorted(set(remaining_template_vars)):
        print(f"  ❌ {var}")

    # Show lines containing these variables
    print("\nLines with unsubstituted template variables:")
    for line in result.split('\n'):
        if any(f'{{{var}}}' in line for var in remaining_template_vars):
            print(f"  {line.strip()}")
            if len([l for l in result.split('\n') if any(f'{{{var}}}' in l for var in remaining_template_vars)]) > 3:
                print("  ... (showing first few)")
                break
else:
    print("✅ All template variables substituted successfully!")

# Also check for CSS blocks (which are normal and expected)
css_blocks = [line for line in result.split('\n') if line.strip().endswith('{') and not re.search(template_var_pattern, line)]
print(f"\nCSS blocks (normal): {len(css_blocks)}")
print("Examples:", css_blocks[:3] if css_blocks else "None")
