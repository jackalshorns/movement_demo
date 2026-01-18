# Migration Guide

Guide for porting this movement demo's physics to other engines (Unity, Godot, etc).

## Core Concepts

### Character Profile System

All physics parameters are defined in `character_profiles.py` as dataclasses. To port:

1. Create equivalent data structures in your engine
2. Copy the numeric values directly - they're frame-rate independent at 60 FPS
3. Scale values if using different time steps

### Key Physics Values

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| `gravity` | 0.4 - 1.0 | Lower = floatier |
| `falling_gravity` | 0.5 - 1.2 | Often higher than rising gravity |
| `jump_force` | 10 - 18 | Initial upward velocity |
| `walk_speed` | 3 - 6 | Pixels per frame at 60 FPS |
| `acceleration` | 0.2 - 2.0 | Lower = more momentum |

---

## Physics Loop Order

The update loop in `player.py` follows this order (critical for feel):

```
1. get_input()           # Read input, set target velocities
2. rect.x += velocity.x  # Apply horizontal movement
3. check_collisions('horizontal')
4. check_wall_contact()  # For wall slide/jump
5. apply_gravity()       # Modify velocity.y
6. rect.y += velocity.y  # Apply vertical movement  
7. check_collisions('vertical')
8. jump()                # Process jump buffer
```

---

## Porting Character Archetypes

### Mario (Momentum-based)

- `has_momentum = True` - velocity changes gradually
- `jump_force_run_bonus` - faster = higher jumps
- High `run_buffer_frames` - maintains speed after releasing run

### Super Meat Boy (Responsive)

- `has_momentum = False` - instant direction changes
- `wall_jump_style = "smb"` - always kicks away from wall
- High `wall_stick_time` - clings to walls briefly

### Celeste/Madeline (Versatile)

- `has_double_jump = True`
- `has_dash = True` with short `dash_duration`
- `wall_jump_style = "celeste"` - directional wall jumps

### N++ Ninja (Floaty)

- Low `gravity` (0.55) and `acceleration` (0.4)
- `wall_jump_style = "npp"` - momentum-preserving bounces
- High `max_fall_speed` for fast falls

---

## Input Buffering

Two critical buffers for responsive controls:

### Coyote Time

```python
if not on_ground:
    air_timer += 1
can_jump = on_ground or (air_timer < coyote_time)
```

Typical value: 4-6 frames

### Jump Buffer

```python
if jump_pressed:
    jump_buffer_timer = jump_buffer  # e.g., 5 frames
else:
    jump_buffer_timer = max(0, jump_buffer_timer - 1)
```

---

## Wall Jump Styles

### SMB Style

```python
velocity.y = -jump_force
velocity.x = -wall_direction * run_speed * 1.2  # Always kicks away
```

### Celeste Style

```python
velocity.y = -jump_force
if pressing_away:
    velocity.x = -wall_direction * run_speed  # Big escape
elif pressing_toward:
    velocity.x = wall_direction * walk_speed * 0.3  # Re-grab
else:
    velocity.x = -wall_direction * walk_speed * 0.6  # Climb
```

### N++ Style

```python
velocity.y = -jump_force * 0.9
kick_speed = max(abs(velocity.x), walk_speed)
velocity.x = -wall_direction * kick_speed * 1.1  # Momentum bounce
```

---

## File Structure Reference

| File | Purpose | Port Priority |
|------|---------|---------------|
| `character_profiles.py` | Physics data | HIGH - port first |
| `player.py` | Physics logic | HIGH - core gameplay |
| `player_renderer.py` | Visuals only | LOW - engine-specific |
| `particles.py` | Effects | LOW - optional |
| `controller.py` | Input | MEDIUM - adapt to engine |
