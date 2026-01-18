---
description: Pygame project code style and organization guidelines
---

# Code Style Guide

## Python Style

* Follow PEP 8 style guide
* Use type hints for function parameters and return values
* All public methods must have docstrings with Args/Returns sections

## Project Structure

* `main.py` is the game loop entry point - keep it focused on orchestration
* New gameplay features should be implemented in dedicated modules, not added to `main.py`
* Each class should be in its own file if it exceeds 200 lines

## Naming Conventions

* Classes: `PascalCase`
* Functions/methods: `snake_case`
* Constants: `UPPER_SNAKE_CASE`
* Private methods: prefix with `_`

## Comments

* Explain "why" not "what"
* Magic numbers must have comments explaining their purpose
* Complex physics calculations need inline explanations
