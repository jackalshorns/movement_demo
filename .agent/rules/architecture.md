---
description: Project architecture and modular code generation rules
---

# Code Generation Guide

## File Organization

* The main method in `main.py` is the entry point to showcase functionality
* Do not add new logic directly to `main.py`. Instead:
  1. Create distinct functionality in a new file (e.g., `feature_x.py`)
  2. Import and use it from `main.py`

## Module Boundaries

* **player.py**: Player physics, input handling, collision detection
* **character_profiles.py**: CharacterProfile dataclass definitions only
* **playgrounds.py**: Level definitions and PlaygroundManager
* **controller.py**: Gamepad/controller input abstraction
* **particles.py**: Particle system and effects
* **ui.py**: UI panels, sliders, overlays
* **sound_manager.py**: Audio loading and playback

## Adding New Features

* New character abilities → Add to `CharacterProfile` dataclass, implement in `player.py`
* New particle effects → Add spawn method to `ParticleSystem` class
* New UI elements → Add to `ControlPanel` class
* New levels → Add `create_*` method to `PlaygroundManager`

## Constants

* Screen dimensions and FPS live in `settings.py`
* Character physics values live in `character_profiles.py`
* Do not hardcode magic numbers - add them to appropriate config location
