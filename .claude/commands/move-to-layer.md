---
description: Move code to the appropriate architectural layer
argument-hint: @<file-path> <what-to-move> to <target-layer>
---

# Move to Correct Layer: $ARGUMENTS

Please move the specified code to the appropriate architectural layer:

## Task
Move: $2 $3 $4 $5 $6 $7 $8 $9

From file: $1

## Architecture Context
- **Core layer** (`app/core/`): Business logic, data models, repositories, services, utilities
- **UI layer** (`app/ui/`): Presentation logic, components, view models, views, UI utilities
- **Style layer** (`app/style/`): Styling, theming, animations, visual effects

## Requirements
- Identify the correct target location based on the code's responsibility
- Create or update the appropriate module in the target layer
- Update imports in the original file
- Ensure proper separation of concerns
- Maintain all existing functionality

## Provide
1. The code in its new location with proper module structure
2. Updated original file with corrected imports
3. Explanation of why this placement is architecturally correct
4. Any additional interface or dependency considerations
