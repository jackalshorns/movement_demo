# Movement Demo - Final Documentation

> **Project Status:** Paused as of January 2026

A platformer physics playground for exploring and comparing movement systems from iconic games.

---

## Purpose

This project was created to **study and compare how different games implement 2D character movement**. By implementing 5 distinct movement profiles side-by-side in the same environment, we can:

1. **Feel the differences** between momentum-based (Mario) vs. precise (Link) vs. floaty (N++) movement
2. **Tune physics in real-time** with sliders for gravity, acceleration, jump force, etc.
3. **Test across varied level designs** optimized for different playstyles
4. **Experiment with LLM-powered physics** by describing movement in natural language

---

## What Was Built

### 5 Playable Characters

| Character | Movement Style | Signature Abilities |
|-----------|---------------|---------------------|
| **Mario** | Momentum-based; running increases jump height | Classic acceleration curves |
| **Super Meat Boy** | Ultra-responsive; wall clings and wall jumps | Extreme air control |
| **Link** | Precise, predictable movement | Dash ability |
| **Madeline (Celeste)** | Double jump + wall jump + dash | Mid-air dash recovery |
| **Ninja (N++)** | Floaty, high-momentum parkour | Maximum air time |

### 6 Test Levels

1. **Flat** — Basic ground for testing base movement
2. **Platforms** — Vertical climbing, wall jump practice
3. **SMB Style** — Tight gaps, hazards, precision jumps
4. **Celeste Style** — Parkour climbing, dash-required gaps
5. **N++ Style** — Momentum-based flow, long arcs
6. **Shaft** — Dedicated vertical wall jump gauntlet

### Key Features

- **Real-time physics tuning** — Adjust gravity, jump force, acceleration via UI sliders
- **Controller support** — PS5 and Xbox controllers with visual button prompts
- **LLM physics customization** — Describe physics changes in natural language (e.g., "floaty moon gravity")
- **Accessibility modes** — High contrast, colorblind filters, character/platform outlines
- **Procedural audio** — Sound effects generated on startup (no audio files needed)

---

## Technical Architecture

```
main.py                 # Game loop, event handling, state machine
├── player.py           # Physics, input, collision detection (~530 lines)
├── player_renderer.py  # Per-character sprite rendering
├── character_profiles.py  # CharacterProfile dataclass with all physics params
├── playgrounds.py      # Level definitions
├── controller.py       # Gamepad abstraction
├── ui.py               # HUD, sliders, overlays
├── accessibility.py    # Colorblind/contrast settings
├── particles.py        # Object-pooled particle system
└── llm_physics.py      # Gemini integration for natural language physics
```

---

## Incomplete Work (Archived Branch)

The `archive/canonical-character-scaling` branch contains unfinished work on:

- **Normalized physics comparison mode** — Scaling all characters to equivalent base metrics so their jumps/speeds can be directly compared
- **Canonical hitbox dimensions** — Standardized collision boxes across characters

---

## What I Learned

1. **Small physics differences feel huge** — A 10% change in air acceleration dramatically changes how "tight" a character feels
2. **Wall jump timing is everything** — The "wall stick time" parameter (frames stuck to wall before sliding) is the secret to good wall jumps
3. **Variable jump height is non-negotiable** — Holding jump longer for higher jumps is expected in modern platformers
4. **Momentum vs. precision is a spectrum** — Mario and N++ on one end, Meat Boy and Link on the other, Celeste in the middle

---

## Quick Start (When Resuming)

```bash
cd movement_demo
pip install -r requirements.txt
python main.py
```

Controllers work automatically. See `CLAUDE.md` for development documentation.

---

## Files to Know

| File | Purpose |
|------|---------|
| `character_profiles.py` | Add/edit characters here |
| `playgrounds.py` | Add/edit levels here |
| `accessibility.py` | All colorblind/contrast settings |
| `CLAUDE.md` | Full developer documentation |
| `BACKLOG.md` | Planned features |
