---
description: Add a new level/playground to the game
---

# Add New Level

// turbo-all

Follow these steps to add a new level:

## 1. Create Level Method

In `playgrounds.py`, add a new method to `PlaygroundManager`:

```python
def create_my_level(self, randomize=False):
    """Description of what this level tests"""
    ground_y = SCREEN_HEIGHT - 60
    
    # Start platform
    self.platforms.add(Platform(0, ground_y, 300, 60, (80, 80, 80)))
    self.start_pos = (100, ground_y - 10)
    
    # Add your platforms
    self.platforms.add(Platform(400, ground_y - 100, 150, 20))
    
    # Finish platform (set is_finish=True)
    finish = Platform(900, ground_y - 200, 100, 20, (200, 200, 50), is_finish=True)
    self.platforms.add(finish)
    self.finish_platform = finish
```

## 2. Register in load_playground()

Add a new case to the `load_playground()` method:

```python
elif index == 6:  # Next available number
    self.create_my_level(randomize)
```

## 3. Update Level Count

Update `next_playground()` and `previous_playground()` to use modulo with the new count.

## 4. Add Level Name

Update `get_name()` with your level's display name.

## 5. Update UI

In `main.py`, update `level_names` list in the selection overlay.

In `ui.py` `draw_level_selector()`, add the new level entry.
