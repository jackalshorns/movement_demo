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

## Current Refactoring Candidates

### player.py (760+ lines)

Could be split into:

- `player_physics.py` - Movement, gravity, collision logic
- `player_renderer.py` - `update_visuals()` procedural sprites
- `player_input.py` - Input processing abstraction

### playgrounds.py (378 lines)

Could be split into:

- `level_data.py` - Level definitions as data structures
- `platform.py` - Platform and Hazard sprite classes

## Rules for Extraction

* Keep the class interface stable - don't change public method signatures
- Move private helper methods with the code that uses them
- Preserve existing import patterns in other files
