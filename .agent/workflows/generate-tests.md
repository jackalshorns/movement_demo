---
description: Generate unit tests for the project using pytest
---

# Generate Unit Tests

Generate comprehensive unit tests following these guidelines:

## Test Structure

* Create test files in the project root with `test_` prefix (e.g., `test_character_profiles.py`)
* Use pytest as the testing framework
* Group tests by functionality in test classes

## What to Test

### CharacterProfile (character_profiles.py)

* Test that all required fields are set
* Test `reset_physics()` restores default values
* Test that each character preset has valid values

### Player (player.py)

* Test collision detection methods
* Test jump logic (ground jump, wall jump, double jump)
* Test physics calculations (gravity, momentum)
* Mock the level and particle system dependencies

### Controller (controller.py)

* Test input normalization
* Test dead zone handling
* Test trigger value conversion

## Test Naming

* Use descriptive names: `test_mario_has_momentum()`, `test_wall_jump_requires_wall_contact()`

## Running Tests

```bash
pytest -v
```
