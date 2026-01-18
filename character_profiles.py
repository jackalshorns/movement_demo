"""
Character physics profiles for the movement demo.

Each CharacterProfile is a dataclass defining movement feel, jump behavior,
abilities, and physics constants. Use the CHARACTERS dict for easy access.

Quick Reference - Typical Ranges:
    walk_speed: 3.0-6.0       run_speed: 6.0-12.0
    acceleration: 0.2-2.0     (low=slidey, high=snappy)
    gravity: 0.4-1.0          (low=floaty, high=weighty)
    jump_force: 10.0-18.0

See CLAUDE.md for full documentation on adding new characters.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CharacterProfile:
    """
    Dataclass defining a character's physics and abilities.
    
    Movement Fields:
        walk_speed: Base horizontal speed (3.0-6.0 typical)
        run_speed: Speed when holding run button (6.0-12.0)
        acceleration: How fast to reach max speed (0.2=sluggish, 2.0=instant)
        deceleration: How fast to stop when not pressing direction
        skid_deceleration: Stopping speed when pressing opposite direction
        has_momentum: True=Mario-like sliding, False=instant direction changes
        
    Jump Fields:
        jump_force: Initial upward velocity (10.0-18.0)
        jump_force_run_bonus: Extra height when running fast (Mario-style)
        variable_jump: True=hold longer to jump higher
        has_double_jump: Allow second jump in air (Celeste-style)
        
    Ability Fields:
        has_dash: Enable dash ability
        dash_speed: Horizontal speed during dash
        dash_duration: Frames the dash lasts
        
    Physics Fields:
        gravity: Downward acceleration (0.4=floaty, 1.0=weighty)
        falling_gravity: Gravity when falling (often higher than rising)
        max_fall_speed: Terminal velocity
        air_acceleration_multiplier: Air control (0.0=none, 1.0=full)
        
    Wall Fields:
        has_wall_slide: Slow fall when touching wall
        has_wall_jump: Can jump off walls
        wall_slide_speed: Fall speed when wall sliding
        wall_jump_style: "celeste", "smb", or "npp" - affects jump direction
        wall_stick_time: Frames to stick to wall before sliding
    """
    
    name: str = ""
    
    # Movement
    walk_speed: float = 0.0
    run_speed: float = 0.0
    acceleration: float = 0.0
    deceleration: float = 0.0
    skid_deceleration: float = 0.0
    has_momentum: bool = True
    
    # Jump
    jump_force: float = 0.0
    jump_force_run_bonus: float = 0.0
    variable_jump: bool = False
    has_double_jump: bool = False
    
    # Abilities
    has_dash: bool = False
    dash_speed: float = 0.0
    dash_duration: int = 0
    
    # Physics
    gravity: float = 0.0
    falling_gravity: float = 0.0
    max_fall_speed: float = 0.0
    air_acceleration_multiplier: float = 1.0
    no_horizontal_drag: bool = False
    
    # Advanced
    run_buffer_frames: int = 0
    coyote_time: int = 0
    jump_buffer: int = 0
    
    # Visual
    color: Tuple[int, int, int] = (255, 255, 255)
    description: str = ""
    
    # Wall Slide / Jump
    has_wall_slide: bool = False
    wall_slide_speed: float = 2.0
    has_wall_jump: bool = False
    wall_jump_style: str = "celeste"
    wall_stick_time: int = 0
    
    def __post_init__(self) -> None:
        """Store defaults and validate physics values."""
        self._defaults = {
            "gravity": self.gravity,
            "falling_gravity": self.falling_gravity,
            "walk_speed": self.walk_speed,
            "acceleration": self.acceleration,
            "jump_force": self.jump_force
        }
        self._validate()

    def reset_physics(self) -> None:
        """Reset physics values to their original defaults."""
        for key, value in self._defaults.items():
            setattr(self, key, value)
    
    def _validate(self) -> None:
        """Warn about physics values that might cause issues."""
        warnings = []
        
        if self.gravity <= 0:
            warnings.append(f"gravity={self.gravity} (should be > 0)")
        if self.jump_force <= 0:
            warnings.append(f"jump_force={self.jump_force} (should be > 0)")
        if self.walk_speed < 0:
            warnings.append(f"walk_speed={self.walk_speed} (should be >= 0)")
        if self.acceleration <= 0:
            warnings.append(f"acceleration={self.acceleration} (should be > 0)")
        if self.wall_jump_style not in ("celeste", "smb", "npp"):
            warnings.append(f"wall_jump_style='{self.wall_jump_style}' (should be celeste/smb/npp)")
        
        if warnings and self.name:
            print(f"[CharacterProfile] Warning for '{self.name}': {', '.join(warnings)}")


# Mario: Momentum-based, weighty, speed-dependent jumps
MARIO = CharacterProfile(
    name="Mario",
    # Movement
    walk_speed=4.0,
    run_speed=8.0,
    acceleration=0.3,
    deceleration=0.3,
    skid_deceleration=0.6,
    has_momentum=True,
    # Jump
    jump_force=14.0,
    jump_force_run_bonus=2.0,
    variable_jump=True,
    has_double_jump=False,
    # Special
    has_wall_jump=False,
    has_wall_slide=False,
    has_dash=False,
    dash_speed=0.0,
    dash_duration=0,
    # Physics
    gravity=0.6,
    falling_gravity=1.0,
    max_fall_speed=12.0,
    air_acceleration_multiplier=0.7,
    no_horizontal_drag=True,
    wall_slide_speed=0.0,
    # Advanced
    run_buffer_frames=10,
    coyote_time=6,
    jump_buffer=5,
    # Visual
    color=(200, 30, 30),  # Mario Red (iconic)
    description="Momentum-based, weighty feel, speed affects jump height"
)

# Super Meat Boy: Ultra-responsive, instant changes, wall mechanics
SUPER_MEAT_BOY = CharacterProfile(
    name="Super Meat Boy",
    # Movement
    walk_speed=6.0,
    run_speed=10.0,
    acceleration=2.0,  # Very high = instant
    deceleration=2.0,
    skid_deceleration=2.0,
    has_momentum=False,  # Instant direction changes
    # Jump
    jump_force=15.0,
    jump_force_run_bonus=0.0,  # No speed-dependent jump
    variable_jump=True,
    has_double_jump=False,  # Base Meat Boy doesn't have double jump
    # Special
    has_wall_jump=True,
    has_wall_slide=True,
    has_dash=False,
    dash_speed=0.0,
    dash_duration=0,
    # Physics
    gravity=0.7,
    falling_gravity=0.7,  # Same gravity (no falling gravity difference)
    max_fall_speed=15.0,
    air_acceleration_multiplier=1.0,  # Full air control
    no_horizontal_drag=True,
    wall_slide_speed=2.0,  # Slow fall when wall sliding
    # Advanced
    run_buffer_frames=0,  # No run buffer
    coyote_time=4,  # Shorter coyote time
    jump_buffer=3,
    # Visual
    color=(120, 40, 40),  # Dark red/brown (Meat Boy)
    description="Ultra-responsive, wall jumps, buzzsaw survivor",
    wall_jump_style="smb",
    wall_stick_time=15
)

# Zelda/Link: Precise, simple physics, dash mechanics
ZELDA_LINK = CharacterProfile(
    name="Link",
    # Movement
    walk_speed=4.5,
    run_speed=4.5,  # No run speed difference (uses dash instead)
    acceleration=1.5,  # Fast but not instant
    deceleration=1.5,
    skid_deceleration=1.5,
    has_momentum=False,  # Instant-ish direction changes
    # Jump
    jump_force=13.0,
    jump_force_run_bonus=0.0,
    variable_jump=False,  # Fixed jump height
    has_double_jump=False,
    # Special
    has_wall_jump=False,
    has_wall_slide=False,
    has_dash=True,
    dash_speed=12.0,
    dash_duration=20,  # frames
    # Physics
    gravity=0.8,
    falling_gravity=0.8,  # Same gravity
    max_fall_speed=12.0,
    air_acceleration_multiplier=0.5,  # Less air control
    no_horizontal_drag=False,  # Has air drag
    wall_slide_speed=0.0,
    # Advanced
    run_buffer_frames=0,
    coyote_time=3,  # Very short
    jump_buffer=3,
    # Visual
    color=(40, 180, 40),  # Link Green (iconic)
    description="Precise control, dash-jump combos, simple physics"
)

# Madeline (Celeste): Double jump + wall jump combo
MADELINE = CharacterProfile(
    name="Madeline",
    # Movement
    walk_speed=5.5,
    run_speed=5.5,  # No run mechanic
    acceleration=1.2,
    deceleration=1.2,
    skid_deceleration=1.2,
    has_momentum=False,  # Responsive control
    # Jump
    jump_force=14.5,
    jump_force_run_bonus=0.0,
    variable_jump=True,
    has_double_jump=True,  # Key feature!
    # Special
    has_wall_jump=True,  # Key feature!
    has_wall_slide=True,
    has_dash=True,  # Celeste's signature dash
    dash_speed=15.0,  # Fast dash
    dash_duration=12,  # Shorter duration
    # Physics
    gravity=0.65,
    falling_gravity=0.9,
    max_fall_speed=13.0,
    air_acceleration_multiplier=0.85,  # Good air control
    no_horizontal_drag=True,
    wall_slide_speed=1.5,  # Moderate wall slide
    # Advanced
    run_buffer_frames=0,
    coyote_time=5,
    jump_buffer=4,
    # Visual
    color=(230, 80, 120),  # Strawberry pink/red (Madeline's hair)
    description="Double jump + wall jump, air dash, excellent air control",
    wall_jump_style="celeste",
    wall_stick_time=10
)

# N++ Ninja: High momentum, floaty, fluid
N_NINJA = CharacterProfile(
    name="Ninja (N++)",
    # Movement
    walk_speed=5.0,
    run_speed=11.0,  # Fast run
    acceleration=0.4,  # Slow acceleration (momentum heavy)
    deceleration=0.2,  # Very slippery
    skid_deceleration=0.3,
    has_momentum=True,
    # Jump
    jump_force=13.0,
    jump_force_run_bonus=0.0,
    variable_jump=True,
    has_double_jump=False,
    # Special
    has_wall_jump=True,
    has_wall_slide=True,
    has_dash=False,
    dash_speed=0.0,
    dash_duration=0,
    # Physics
    gravity=0.55,  # Floaty
    falling_gravity=0.55,
    max_fall_speed=18.0,  # Good terminal velocity
    air_acceleration_multiplier=0.9,  # Good air control but momentum based
    no_horizontal_drag=True,
    wall_slide_speed=2.5,  # Faster wall slide than others
    # Advanced
    run_buffer_frames=15,  # High buffer
    coyote_time=5,
    jump_buffer=5,
    # Visual
    color=(180, 180, 180),  # Grey/Black (Ninja)
    description="Floaty, high momentum, fluid parkour flow",
    wall_jump_style="npp",
    wall_stick_time=0
)

# Dictionary for easy access
CHARACTERS = {
    "mario": MARIO,
    "meatboy": SUPER_MEAT_BOY,
    "link": ZELDA_LINK,
    "madeline": MADELINE,
    "ninja": N_NINJA
}
