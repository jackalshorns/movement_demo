# Movement Demo - Backlog

## Planned Features

- [ ] **Tool for accessibility tweaks** - In-game tool allowing an accessibility expert to click on colors and adjust them on the fly. All colorblind mode settings would be editable in real-time without restarting the game.

- [ ] **Normalized physics comparison mode** - A mode where all 5 characters have their physics normalized relative to each other so they can be directly compared. If all 5 jumped at once, their relative jump heights/speeds would be equivalent. This would require:
  - A "normalized" level designed for fair comparison
  - Scaling factors for each character's speed, jump force, gravity
  - Possibly a side-by-side or simultaneous view of all characters

## Completed

- [x] PS5 button icons with supersampled rendering
- [x] SETTINGS panel with Sound, Theme, and Color Blind options
- [x] High Contrast mode with character/platform outlines
- [x] Colorblind modes (Deuteranopia, Protanopia, Tritanopia)
- [x] All accessibility settings centralized in `accessibility.py`
