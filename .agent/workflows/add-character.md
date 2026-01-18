---
description: Add a new playable character to the game
---

# Add New Character

// turbo-all

Follow these steps to add a new character:

## 1. Define the CharacterProfile

Edit `character_profiles.py` and add a new profile:

```python
NEW_CHARACTER = CharacterProfile(
    name="Character Name",
    # Movement
    walk_speed=5.0,
    run_speed=8.0,
    acceleration=0.5,
    deceleration=0.5,
    has_momentum=True,  # True=Mario-like slide, False=instant stop
    # Jump
    jump_force=14.0,
    variable_jump=True,
    has_double_jump=False,
    # Wall mechanics
    has_wall_jump=False,
    has_wall_slide=False,
    wall_jump_style="celeste",  # "celeste", "smb", or "npp"
    # Special
    has_dash=False,
    dash_speed=12.0,
    # Physics
    gravity=0.6,
    falling_gravity=1.0,
    # Visual
    color=(R, G, B),
    description="Short description"
)
```

## 2. Register the Character

Add to the `CHARACTERS` dict at the bottom of `character_profiles.py`.

## 3. Add to Selection List

In `main.py`, add to `char_list`:

```python
char_list = [MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA, NEW_CHARACTER]
```

## 4. Add Visual Representation

In `player_renderer.py`, add a new draw function:

```python
def draw_new_character(surface, center_x, color, velocity_x, on_ground, anim_offset):
    """Draw New Character sprite."""
    # Add your drawing code here
    # See existing draw_mario(), draw_link() etc. for examples
    return anim_offset
```

Then add to the `render_character()` dispatcher:

```python
elif name == "New Character":
    return draw_new_character(player.image, center_x, color,
                              player.velocity.x, player.on_ground, player.anim_offset)
```

## 5. Add to UI

In `ui.py`, update the `draw_character_face()` method with a pixel art face for the new character.

## 6. (Optional) Add Signature Move

In `player.py` `perform_signature_move()`, add a case for the new character.
