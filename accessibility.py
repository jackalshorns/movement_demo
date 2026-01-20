"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ACCESSIBILITY SETTINGS                                ║
║                                                                              ║
║  This file contains ALL accessibility-related settings and tunable values.   ║
║  Artists and designers can modify the constants below to fine-tune the       ║
║  visual appearance of accessibility features.                                ║
║                                                                              ║
║  HOW TO USE:                                                                 ║
║  1. Run the game: python3 main.py                                            ║
║  2. Hold L1 → Navigate to "Color Blind" → Left/Right to toggle              ║
║  3. Observe the High Contrast mode effects                                   ║
║  4. Modify the TUNABLE CONSTANTS below and restart to see changes            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ════════════════════════════════════════════════════════════════════════════
#                          TUNABLE CONSTANTS
#                    (Artists: Modify these values!)
# ════════════════════════════════════════════════════════════════════════════

# ── CHARACTER OUTLINES ──────────────────────────────────────────────────────
# These settings control the outline drawn around player characters when
# High Contrast mode is enabled.

CHARACTER_OUTLINE_THICKNESS = 3        # Pixels of outline around character (1-5 recommended)
CHARACTER_OUTLINE_COLOR = (0, 0, 0)    # RGB color of character outline (black)
CHARACTER_OUTLINE_DIAMOND = True       # True = diamond shape, False = square shape

# ── PLATFORM OUTLINES ───────────────────────────────────────────────────────
# These settings control the outlines drawn around platforms when
# High Contrast mode is enabled.

PLATFORM_OUTLINE_THICKNESS = 4         # Pixels of outer black outline (2-6 recommended)
PLATFORM_OUTLINE_COLOR = (0, 0, 0)     # RGB color of platform outer outline
PLATFORM_INNER_LINE_THICKNESS = 2      # Pixels of inner white highlight line
PLATFORM_INNER_LINE_COLOR = (255, 255, 255)  # RGB color of inner line (white)

# ── COLOR ADJUSTMENTS ───────────────────────────────────────────────────────
# These settings control how colors are modified in High Contrast mode.

HIGH_CONTRAST_DARKEN_AMOUNT = 30       # How much to darken dark colors (0-100)
HIGH_CONTRAST_BRIGHTEN_AMOUNT = 30     # How much to brighten light colors (0-100)
HIGH_CONTRAST_BRIGHTNESS_THRESHOLD = 128  # Colors below this are darkened, above brightened

# ── COLORBLIND-SPECIFIC COLOR SHIFTS ────────────────────────────────────────
# These control how colors are shifted for colorblind users.
# Adjust these values to fine-tune how colors appear for each type of
# color vision deficiency. Artists: experiment with these!

# DEUTERANOPIA (Red-Green) - Most common, affects ~6% of men
# People have difficulty distinguishing red from green
DEUTERANOPIA_RED_SHIFT = 60            # Yellow added to reds (makes reds more orange)
DEUTERANOPIA_GREEN_SHIFT = 80          # Blue added to greens (shifts greens to cyan/blue)
DEUTERANOPIA_THRESHOLD = 30            # Minimum difference to trigger shift

# PROTANOPIA (Red-Green variant) - Affects ~1% of men  
# Similar to deuteranopia but with different red perception
PROTANOPIA_RED_BOOST_R = 20            # Red channel boost for reds
PROTANOPIA_RED_BOOST_G = 80            # Green channel boost for reds (makes orange)
PROTANOPIA_GREEN_SHIFT = 100           # Blue added to greens
PROTANOPIA_THRESHOLD = 30              # Minimum difference to trigger shift

# TRITANOPIA (Blue-Yellow) - Rare, affects ~0.01%
# People have difficulty distinguishing blue from yellow
TRITANOPIA_BLUE_SHIFT = 80             # Red (magenta) added to blues
TRITANOPIA_THRESHOLD = 30              # Minimum difference to trigger shift


# ════════════════════════════════════════════════════════════════════════════
#                          ACCESSIBILITY CLASS
# ════════════════════════════════════════════════════════════════════════════

class AccessibilitySettings:
    """
    Manages accessibility settings like colorblind modes.
    
    Usage:
        from accessibility import accessibility
        
        # Check if any mode is active
        if accessibility.is_active:
            # Apply accessible styling
            
        # Get outline settings
        if accessibility.outline_characters:
            draw_outline_around_character()
            
        # Adjust a color for current mode
        adjusted = accessibility.adjust_color((255, 0, 0))
    """
    
    # ═══════════════════════════════════════════════════════════════════════
    # AVAILABLE MODES - All 5 are now enabled!
    # Artists: You can reorder these or comment out modes you don't want
    # ═══════════════════════════════════════════════════════════════════════
    MODES = [
        "Off",           # No modifications
        "High Contrast", # Bold outlines, high contrast colors
        "Deuteranopia",  # Red-green colorblindness (most common ~6% of men)
        "Protanopia",    # Red-green variant (~1% of men)
        "Tritanopia",    # Blue-yellow colorblindness (rare ~0.01%)
    ]
    
    def __init__(self):
        self.colorblind_mode_index = 0  # Default: Off
        self.outline_characters = False  # Add outlines to characters
        self.pattern_platforms = False   # Add patterns to platforms
    
    @property
    def colorblind_mode(self):
        """Get current mode name."""
        return self.MODES[self.colorblind_mode_index]
    
    @property
    def is_active(self):
        """Returns True if any colorblind/accessibility mode is enabled."""
        return self.colorblind_mode_index > 0
    
    def cycle_mode(self, direction=1):
        """
        Cycle through colorblind modes.
        
        Args:
            direction: 1 = next mode, -1 = previous mode
            
        Returns:
            Name of the new mode
        """
        self.colorblind_mode_index = (self.colorblind_mode_index + direction) % len(self.MODES)
        self._apply_mode()
        return self.colorblind_mode
    
    def _apply_mode(self):
        """Apply visual settings based on current mode."""
        mode = self.colorblind_mode
        
        if mode == "Off":
            self.outline_characters = False
            self.pattern_platforms = False
        elif mode == "High Contrast":
            self.outline_characters = True
            self.pattern_platforms = True
        elif mode in ["Deuteranopia", "Protanopia", "Tritanopia"]:
            self.outline_characters = True
            self.pattern_platforms = False
    
    def adjust_color(self, color):
        """
        Adjust a color based on current colorblind mode.
        
        Args:
            color: (R, G, B) tuple (0-255 each)
        
        Returns:
            Adjusted (R, G, B) tuple
        """
        if not self.is_active:
            return color
        
        r, g, b = color
        mode = self.colorblind_mode
        
        if mode == "High Contrast":
            # Boost contrast - darken darks, brighten brights
            avg = (r + g + b) // 3
            if avg < HIGH_CONTRAST_BRIGHTNESS_THRESHOLD:
                return (
                    max(0, r - HIGH_CONTRAST_DARKEN_AMOUNT),
                    max(0, g - HIGH_CONTRAST_DARKEN_AMOUNT),
                    max(0, b - HIGH_CONTRAST_DARKEN_AMOUNT)
                )
            else:
                return (
                    min(255, r + HIGH_CONTRAST_BRIGHTEN_AMOUNT),
                    min(255, g + HIGH_CONTRAST_BRIGHTEN_AMOUNT),
                    min(255, b + HIGH_CONTRAST_BRIGHTEN_AMOUNT)
                )
        
        elif mode == "Deuteranopia":
            # Red-green colorblindness: shift to blue/orange spectrum
            if r > g + DEUTERANOPIA_THRESHOLD:  # Reddish → add yellow
                return (r, min(255, g + DEUTERANOPIA_RED_SHIFT), b)
            elif g > r + DEUTERANOPIA_THRESHOLD:  # Greenish → shift to blue
                return (r, g // 2, min(255, b + DEUTERANOPIA_GREEN_SHIFT))
            return color
        
        elif mode == "Protanopia":
            # Red-green variant
            if r > g + PROTANOPIA_THRESHOLD:  # Reddish → more orange
                return (min(255, r + PROTANOPIA_RED_BOOST_R), min(255, g + PROTANOPIA_RED_BOOST_G), b)
            elif g > r + PROTANOPIA_THRESHOLD:  # Greenish → stronger blue
                return (r, g // 2, min(255, b + PROTANOPIA_GREEN_SHIFT))
            return color
        
        elif mode == "Tritanopia":
            # Blue-yellow confusion: shift blue to pink/magenta
            if b > r + TRITANOPIA_THRESHOLD and b > g + TRITANOPIA_THRESHOLD:  # Bluish → add red
                return (min(255, r + TRITANOPIA_BLUE_SHIFT), g, b)
            return color
        
        return color
    
    def get_outline_color(self, base_color):
        """
        Get contrasting outline color for a base color.
        
        Args:
            base_color: (R, G, B) tuple
            
        Returns:
            Black for light colors, white for dark colors
        """
        r, g, b = base_color
        brightness = (r + g + b) / 3
        if brightness > 128:
            return (0, 0, 0)  # Black outline for light colors
        else:
            return (255, 255, 255)  # White outline for dark colors


# ════════════════════════════════════════════════════════════════════════════
#                          GLOBAL INSTANCE
# ════════════════════════════════════════════════════════════════════════════

# This is the global accessibility settings object used throughout the game.
# Import it with: from accessibility import accessibility
accessibility = AccessibilitySettings()


# ════════════════════════════════════════════════════════════════════════════
#                          HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def get_character_outline_settings():
    """
    Get the current character outline settings for rendering.
    
    Returns:
        dict with 'enabled', 'thickness', 'color', 'diamond' keys
    """
    return {
        'enabled': accessibility.outline_characters,
        'thickness': CHARACTER_OUTLINE_THICKNESS,
        'color': CHARACTER_OUTLINE_COLOR,
        'diamond': CHARACTER_OUTLINE_DIAMOND,
    }


def get_platform_outline_settings():
    """
    Get the current platform outline settings for rendering.
    
    Returns:
        dict with 'enabled', 'thickness', 'color', 'inner_thickness', 'inner_color' keys
    """
    return {
        'enabled': accessibility.is_active,
        'thickness': PLATFORM_OUTLINE_THICKNESS,
        'color': PLATFORM_OUTLINE_COLOR,
        'inner_thickness': PLATFORM_INNER_LINE_THICKNESS,
        'inner_color': PLATFORM_INNER_LINE_COLOR,
    }
