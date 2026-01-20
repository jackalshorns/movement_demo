# Movement Demo

A platformer physics playground comparing movement systems from iconic games: **Mario**, **Super Meat Boy**, **Celeste**, **Zelda**, and **N++**.

Built with Python + Pygame for rapid iteration and experimentation.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Pygame](https://img.shields.io/badge/Pygame-2.6-green)

## Setup

```bash
git clone https://github.com/jackalshorns/movement_demo.git
cd movement_demo
pip install -r requirements.txt
python main.py
```

## Controls

### Keyboard

| Action | Keys |
|--------|------|
| Move | ← → or A/D |
| Jump | Space, W, or ↑ |
| Run | Shift |
| Dash | X or C |
| Reset | R |

### Controller (PS5/Xbox)

| Action | Button |
|--------|--------|
| Move | Left Stick or D-pad |
| Jump | X / A |
| Run | L2/R2 (analog) |
| Dash | Circle / B |
| Signature Move | Circle / B |

### Selection

- **LT + D-pad**: Select character
- **RT + D-pad**: Select level
- **LB**: Reset physics sliders
- **Share**: Randomize level

### Quick Select (Keyboard)

- **Y U I O P**: Characters (Mario, Meat Boy, Link, Madeline, Ninja)
- **1-6**: Levels
- **7**: Randomize

## Characters

| Character | Style | Signature |
|-----------|-------|-----------|
| **Mario** | Momentum-based, speed affects jump height | Coin |
| **Super Meat Boy** | Ultra-responsive, wall jumps | Squish |
| **Link** | Precise control, dash ability | Sword Arc |
| **Madeline** | Double jump + wall jump + dash | Glitch |
| **Ninja (N++)** | Floaty, high momentum parkour | Shuriken |

## Levels

1. **Flat** - Basic run and jump
2. **Platforms** - Wall jump practice
3. **SMB Style** - Hazards and tight walls
4. **Celeste Style** - Parkour climb
5. **N++ Style** - Momentum flow
6. **Shaft** - Dedicated wall jump practice

## LLM Physics Customization

Describe physics in natural language and let Claude adjust the sliders!

### Setup

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Set the environment variable:

   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. Install the dependency:

   ```bash
   pip install anthropic
   ```

### Usage

1. Hold **R1** and D-pad down to select **Customize**
2. Press **X** to enter text input mode
3. Type a description (e.g., "floaty moon gravity", "slippery ice")
4. Press **Enter** to apply, **Escape** to cancel

### Example Prompts

- "floaty moon gravity" → Low gravity, high jumps
- "slippery ice physics" → Low acceleration
- "heavy and snappy like Meat Boy" → High gravity, high acceleration
- "bouncy trampoline jumps" → High jump force

## For Developers

See [`CLAUDE.md`](CLAUDE.md) for:

- Architecture overview
- How to add characters
- How to add levels
- Physics tweaking guide

## License

MIT
