# Movement Demo - AI Assistant Guide

> Platformer physics playground comparing movement systems from Mario, Super Meat Boy, Celeste, Zelda, and N++.

## Quick Start

```bash
pip install -r requirements.txt
python3 main.py
```

---

## 🎮 Quick Modification Levers

### Add a New Character

Edit [`character_profiles.py`](file:///Users/jackalshorns/Antigravity/movement_demo/character_profiles.py):

```python
NEW_CHARACTER = CharacterProfile(
    name="Character Name",
    # Movement
    walk_speed=5.0,          # Base movement speed
    run_speed=8.0,           # Speed when holding run
    acceleration=0.5,        # How fast you reach max speed (0.2=sluggish, 2.0=instant)
    deceleration=0.5,        # How fast you stop
    has_momentum=True,       # True=Mario-like slide, False=instant stop
    # Jump
    jump_force=14.0,         # Base jump height
    variable_jump=True,      # True=hold longer to jump higher
    has_double_jump=False,
    # Wall mechanics
    has_wall_jump=False,
    has_wall_slide=False,
    wall_jump_style="celeste",  # "celeste", "smb", or "npp"
    # Special
    has_dash=False,
    dash_speed=12.0,
    # Physics
    gravity=0.6,             # Lower=floatier (0.4-1.0 typical)
    falling_gravity=1.0,     # Gravity when falling (often higher)
    # Visual
    color=(R, G, B),
    description="Short description"
)
```

Then add to `CHARACTERS` dict at bottom.

**For visuals:** Add a draw function in [`player_renderer.py`](file:///Users/jackalshorns/Antigravity/movement_demo/player_renderer.py):

```python
def draw_new_char(surface, center_x, color, velocity_x, on_ground, anim_offset):
    # Drawing code here
    return anim_offset
```

---

### Add a New Level/Playground

Edit [`playgrounds.py`](file:///Users/jackalshorns/Antigravity/movement_demo/playgrounds.py):

1. Add a new method to `PlaygroundManager`:

```python
def create_my_level(self, randomize=False):
    ground_y = SCREEN_HEIGHT - 60
    # Always start with ground
    self.platforms.add(Platform(0, ground_y, 400, 60))
    # Add platforms: Platform(x, y, width, height, color, is_finish)
    self.platforms.add(Platform(500, ground_y - 100, 150, 20))
    # Finish platform (green)
    self.platforms.add(Platform(900, ground_y - 200, 100, 20, (100, 255, 100), True))
```

1. Register it in `load_playground()`:

```python
elif index == 6:  # Next number
    self.create_my_level(randomize)
```

1. Update `get_name()` with your level name.

---

### Tune Physics in Real-Time

The **UI sliders** (right panel) modify these fields on the active `CharacterProfile`:

- `gravity`
- `falling_gravity`
- `walk_speed`
- `acceleration`
- `jump_force`

**Controller adjustments:**

- Press **LB (L1)** to reset all sliders to character defaults
- Hold **RB (R1)** + D-Pad Up/Down to select, Left/Right to adjust

---

### Add Controller Buttons

Edit [`controller.py`](file:///Users/jackalshorns/Antigravity/movement_demo/controller.py):

- Button mappings are in `get_movement_input()`, `get_cycling_input()`, etc.
- PS5/Xbox button indices differ - check `self.debug_mode` output

---

### Add Keyboard Keys

Edit [`keybindings.py`](file:///Users/jackalshorns/Antigravity/movement_demo/keybindings.py):

```python
self.bindings = {
    "my_action": [pygame.K_q],
    ...
}
```

---

### Add Particle Effects

Edit [`particles.py`](file:///Users/jackalshorns/Antigravity/movement_demo/particles.py):

```python
def spawn_my_effect(self, x, y, color):
    for _ in range(5):
        p = self._get_next_particle()
        p.spawn(x, y, vx=random.uniform(-2, 2), vy=random.uniform(-3, 0),
                lifetime=20, color=color, size=3)
```

Call from `player.py` via `self.particle_system.spawn_my_effect(...)`.

---

### Add Sounds

1. Add to `sound_files` dict in [`sound_manager.py`](file:///Users/jackalshorns/Antigravity/movement_demo/sound_manager.py)
2. Or add `.wav` files to `sounds/` folder (auto-loaded)
3. Play with `self.sound_manager.play("sound_name")` in player code

---

## ♿ Accessibility (High Contrast Mode)

> **IMPORTANT**: Accessibility is a core priority for this project. All accessibility settings are centralized in [`accessibility.py`](file:///Users/jackalshorns/Antigravity/movement_demo/accessibility.py) for easy artist tuning.

### Quick Toggle

Hold **L1** → Navigate to **Color Blind** → **Left/Right** to toggle between **Off** and **High Contrast**

### Tunable Constants (for Artists)

All settings are at the **top** of `accessibility.py`:

```python
# ── CHARACTER OUTLINES ──────────────────────────────────────────────────────
CHARACTER_OUTLINE_THICKNESS = 3        # Pixels (1-5 recommended)
CHARACTER_OUTLINE_COLOR = (0, 0, 0)    # RGB color (black)
CHARACTER_OUTLINE_DIAMOND = True       # Diamond or square shape

# ── PLATFORM OUTLINES ───────────────────────────────────────────────────────
PLATFORM_OUTLINE_THICKNESS = 4         # Outer outline pixels (2-6 recommended)
PLATFORM_OUTLINE_COLOR = (0, 0, 0)     # RGB color (black)
PLATFORM_INNER_LINE_THICKNESS = 2      # Inner highlight pixels
PLATFORM_INNER_LINE_COLOR = (255, 255, 255)  # RGB color (white)

# ── COLOR ADJUSTMENTS ───────────────────────────────────────────────────────
HIGH_CONTRAST_DARKEN_AMOUNT = 30       # Darken dark colors (0-100)
HIGH_CONTRAST_BRIGHTEN_AMOUNT = 30     # Brighten light colors (0-100)
```

### Where Effects Are Rendered

| Effect | File | Function |
|--------|------|----------|
| Character outlines | `player_renderer.py` | `add_character_outline()` |
| Platform outlines | `sprites.py` | `Platform.draw()` |
| Color adjustments | `accessibility.py` | `adjust_color()` |

### Helper Functions

```python
from accessibility import get_character_outline_settings, get_platform_outline_settings

# Get current character outline config
settings = get_character_outline_settings()
# Returns: {'enabled': True, 'thickness': 3, 'color': (0,0,0), 'diamond': True}

# Get current platform outline config
settings = get_platform_outline_settings()
# Returns: {'enabled': True, 'thickness': 4, 'color': (0,0,0), ...}
```

### Adding New Colorblind Modes

Uncomment modes in `accessibility.py`:

```python
MODES = [
    "Off",
    "High Contrast",
    # "Deuteranopia",  # ← Uncomment to enable
    # "Protanopia",
    # "Tritanopia",
]
```

---

## Architecture Overview

```
main.py              # Game loop, event handling, state machine
├── player.py        # Player class (physics, input, collisions)
├── player_renderer.py    # Character sprite drawing (per-character)
├── controller.py    # Gamepad input wrapper (PS5/Xbox)
├── keybindings.py   # Keyboard input + save/load
├── playgrounds.py   # Level definitions (PlaygroundManager)
├── sprites.py       # Platform, Key, Hazard sprite classes
├── character_profiles.py  # CharacterProfile dataclass + 5 presets
├── character_faces.py     # Pixel art face definitions
├── particles.py     # Object-pooled particle system (with caching)
├── sound_manager.py # Audio loading/playback
├── sound_generator.py     # Procedural sound generation
├── ui.py            # HUD, sliders, overlays, pause screen
└── settings.py      # Screen dimensions, FPS
```

---

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `Player` | player.py | ~530 lines handling physics, input, collisions |
| `CharacterProfile` | character_profiles.py | Dataclass defining physics/abilities |
| `PlaygroundManager` | playgrounds.py | Level loader with 6 built-in levels |
| `ControllerInput` | controller.py | Gamepad abstraction |
| `ParticleSystem` | particles.py | Pool of 100 particles + surface caching |
| `ControlPanel` | ui.py | Left/right HUD panels |
| `render_character` | player_renderer.py | Dispatcher for character sprite drawing |

---

## State Machine (main.py)

```
Normal gameplay
  ├─ Hold LT (L2) → Character selection mode (D-pad navigates)
  ├─ Hold RT (R2) → Level selection mode (D-pad navigates)
  ├─ Release trigger → Apply selection
  ├─ Hold RB (R1) → Physics adjustment mode (D-pad adjusts sliders)
  ├─ Press LB (L1) → Reset physics to defaults
  └─ Press Start/Options → Toggle pause/help screen
```

---

## CharacterProfile Field Reference

### Movement

| Field | Type | Description |
|-------|------|-------------|
| `walk_speed` | float | Base horizontal speed |
| `run_speed` | float | Speed when holding run |
| `acceleration` | float | How fast to reach max speed |
| `deceleration` | float | How fast to stop |
| `has_momentum` | bool | Slide vs instant stop |

### Jump

| Field | Type | Description |
|-------|------|-------------|
| `jump_force` | float | Initial upward velocity |
| `jump_force_run_bonus` | float | Extra height when running (Mario) |
| `variable_jump` | bool | Hold to jump higher |
| `has_double_jump` | bool | Celeste-style air jump |

### Wall Mechanics

| Field | Type | Description |
|-------|------|-------------|
| `has_wall_slide` | bool | Slow fall on walls |
| `has_wall_jump` | bool | Jump off walls |
| `wall_slide_speed` | float | Fall speed on wall |
| `wall_jump_style` | str | "celeste", "smb", "npp" |
| `wall_stick_time` | int | Frames stuck to wall |

### Physics

| Field | Type | Description |
|-------|------|-------------|
| `gravity` | float | Downward acceleration |
| `falling_gravity` | float | Gravity when vy > 0 |
| `max_fall_speed` | float | Terminal velocity |
| `air_acceleration_multiplier` | float | Air control (0.0-1.0) |

---

## Common Patterns

### Finding where X happens

- **Player movement logic**: `player.py` → `get_input()`, `apply_gravity()`
- **Collision detection**: `player.py` → `check_collisions()`, `check_wall_contact()`
- **Jump logic**: `player.py` → `jump()` (handles ground, wall, double)
- **Visual effects**: `player_renderer.py` → `draw_mario()`, `draw_madeline()`, etc.
- **Level layouts**: `playgrounds.py` → individual `create_*` methods
- **UI drawing**: `ui.py` → `draw_left_panel()`, `draw_right_panel()`, `draw_pause_screen()`

### Debugging

- `controller.debug_mode = True` → Print all button presses
- Add `print()` statements in `player.update()` for physics debugging
- Press **R** to reset player position
