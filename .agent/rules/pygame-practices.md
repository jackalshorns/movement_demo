---
description: Pygame-specific best practices for this platformer demo
---

# Pygame Best Practices

## Performance

* Use object pooling for frequently created/destroyed objects (see `particles.py`)
* Pre-render static surfaces when possible (e.g., gradient backgrounds)
* Avoid creating new Surfaces every frame - cache them
* Use sprite groups for efficient batch rendering

## Input Handling

* Support both keyboard and controller input for all actions
* Use dead zones for analog stick input (0.2 threshold minimum)
* Implement input buffering for responsive controls (coyote time, jump buffer)

## Physics

* Use `pygame.math.Vector2` for velocity and position calculations
* Separate horizontal and vertical collision checks
* Apply gravity after input processing, before collision detection

## Rendering Order

1. Background (draw_background)
2. Level platforms/hazards
3. Particles (behind player)
4. Player sprite
5. UI overlay (always on top)
