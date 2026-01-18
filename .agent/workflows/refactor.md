---
description: Refactor large files into smaller, focused modules
---

# Refactor for Modularity

Use this workflow when a file exceeds 300 lines and needs to be split.

## Process

1. **Identify extraction targets**: Look for distinct responsibilities that can be separated

2. **Create new module**: Extract related functions/classes to a new file

3. **Add imports**: Update the original file to import from the new module

4. **Update tests**: Ensure any tests are updated to import from new locations

5. **Verify**: Run the game to ensure nothing broke

## Completed Refactors

### player.py → player_renderer.py ✅

- Extracted 236 lines of rendering code
- Reduced player.py from 760 to 527 lines

## Remaining Candidates

### playgrounds.py (369 lines)

Could be split into:

- `level_data.py` - Level definitions as data structures
- `platform.py` - Platform and Hazard sprite classes

### ui.py (408 lines)

Could be split into:

- `ui_controls.py` - Control panel and sliders
- `ui_faces.py` - Character face rendering

## Rules for Extraction

- Keep the class interface stable - don't change public method signatures

- Move private helper methods with the code that uses them
- Preserve existing import patterns in other files
