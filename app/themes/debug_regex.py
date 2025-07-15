#!/usr/bin/env python3
"""Debug regex pattern issues"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from theme_manager import ThemeTemplateLoader

# Load the actual base_style.qss template
loader = ThemeTemplateLoader()
template = loader.load_base_style()

print("=== Regex Pattern Debugging ===")
print("First 500 characters of template:")
print(repr(template.template_content[:500]))

# Test different regex patterns
patterns = [
    (r'\{([^}\n]+)\}', "Current pattern (no newlines)"),
    (r'\{([^}]+)\}', "Original pattern (with newlines)"),
    (r'\{(\w+)\}', "Word characters only"),
]

for pattern, description in patterns:
    print(f"\n--- {description} ---")
    matches = re.findall(pattern, template.template_content)
    print(f"Found {len(matches)} matches:")
    for match in sorted(set(matches))[:10]:  # Show first 10 unique matches
        print(f"  '{match}'")

    if len(matches) > 10:
        print(f"  ... and {len(matches) - 10} more")

# Show lines that contain { but aren't being substituted
print("\n=== Lines with { characters ===")
lines_with_braces = [line for line in template.template_content.split('\n') if '{' in line]
print(f"Found {len(lines_with_braces)} lines with braces:")
for line in lines_with_braces[:5]:
    print(f"  '{line.strip()}'")
