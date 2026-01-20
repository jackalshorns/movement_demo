"""
UI Theme constants for consistent, accessible styling.
Supports Dark/Light theme toggle.
"""

import pygame

# Initialize pygame font system
pygame.font.init()

# =============================================================================
# THEME SYSTEM - Dark/Light mode toggle
# =============================================================================

class Theme:
    """Manages Dark/Light theme settings."""
    DARK = "Dark"
    LIGHT = "Light"
    
    def __init__(self):
        self.current = self.LIGHT  # Light theme default for accessibility
    
    def toggle(self):
        """Toggle between Dark and Light themes."""
        self.current = self.LIGHT if self.current == self.DARK else self.DARK
        return self.current
    
    def is_dark(self):
        return self.current == self.DARK

# Global theme instance
theme = Theme()


# =============================================================================
# FONTS - Large, readable sizes
# =============================================================================

FONT_FAMILY = None  # None = pygame default

# Font sizes (large for accessibility)
FONT_SIZE_LARGE = 32       # Top bar headers
FONT_SIZE_HEADER = 28      # Section headers
FONT_SIZE_TEXT = 24        # Body text
FONT_SIZE_SMALL = 22       # Small labels
FONT_SIZE_TINY = 20        # Hints

# Cached font objects
_font_cache = {}

def get_font(size, bold=False):
    """Get a cached font object."""
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(FONT_FAMILY, size, bold=bold)
    return _font_cache[key]

def font_large():
    return get_font(FONT_SIZE_LARGE, bold=True)

def font_header():
    return get_font(FONT_SIZE_HEADER, bold=True)

def font_text():
    return get_font(FONT_SIZE_TEXT)

def font_small():
    return get_font(FONT_SIZE_SMALL)

def font_tiny():
    return get_font(FONT_SIZE_TINY)


# =============================================================================
# COLORS - Theme-aware colors
# =============================================================================

def get_colors():
    """Get current theme colors."""
    if theme.is_dark():
        return {
            # Background
            'bg_top': (25, 25, 50),
            'bg_bottom': (15, 15, 30),
            'grid': (50, 50, 80),
            'top_bar_bg': (20, 20, 45, 240),
            
            # Text - PURE WHITE for maximum readability
            'text_bright': (255, 255, 255),
            'text_dim': (220, 220, 220),
            'text_hint': (180, 180, 180),
            
            # Headers - bright, saturated
            'header_blue': (100, 200, 255),
            'header_red': (255, 100, 100),  # For Abilities, Controls, Accessibility
            'header_orange': (255, 180, 80),
            'header_green': (100, 255, 150),
            'header_purple': (200, 150, 255),
            'header_yellow': (255, 230, 100),
            
            # UI elements
            'slider_track': (70, 70, 100),
            'slider_handle': (220, 220, 220),
            'highlight': (255, 255, 120),
            'widget_bg': (30, 30, 60, 200),
        }
    else:  # Light theme
        return {
            # Background
            'bg_top': (220, 225, 235),
            'bg_bottom': (200, 205, 215),
            'grid': (180, 185, 195),
            'top_bar_bg': (240, 242, 248, 240),
            
            # Text - Dark for light background
            'text_bright': (30, 30, 40),
            'text_dim': (60, 60, 70),
            'text_hint': (100, 100, 110),
            
            # Headers - darker, saturated (red for section headers per mockup)
            'header_blue': (30, 100, 160),
            'header_red': (180, 60, 60),  # For Abilities, Controls, Accessibility
            'header_orange': (180, 100, 30),
            'header_green': (30, 130, 70),
            'header_purple': (100, 60, 160),
            'header_yellow': (160, 130, 20),
            
            # UI elements
            'slider_track': (160, 165, 180),
            'slider_handle': (100, 100, 120),
            'highlight': (255, 180, 40),
            'widget_bg': (250, 252, 255, 240),
            'widget_border': (180, 185, 200),
        }


# =============================================================================
# SPACING - Generous for readability
# =============================================================================

MARGIN_LEFT = 15
MARGIN_RIGHT = 15
MARGIN_TOP = 15

SPACING_SECTION = 20
SPACING_ITEM = 28
SPACING_SLIDER = 38
SPACING_LINE = 26

SLIDER_WIDTH = 160
SLIDER_HEIGHT = 10


# =============================================================================
# LAYOUT POSITIONS - Based on mockup
# =============================================================================

# Top row (Character | Level | Physics)
TOP_ROW_Y = 25

# Left panel (Abilities, Controls, Accessibility)
LEFT_PANEL_X = 15
LEFT_PANEL_Y = 70
LEFT_PANEL_WIDTH = 180

# Right panel (Physics sliders + description)
RIGHT_PANEL_X = 824 - 220  # SCREEN_WIDTH - 220
RIGHT_PANEL_Y = 70
RIGHT_PANEL_WIDTH = 200

def get_right_panel_x(screen_width):
    return screen_width - RIGHT_PANEL_WIDTH - MARGIN_RIGHT

def get_slider_x(screen_width):
    return screen_width - SLIDER_WIDTH - MARGIN_RIGHT - 20


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def draw_widget_background(surface, x, y, width, height):
    """Draw a semi-transparent widget background."""
    colors = get_colors()
    bg_color = colors['widget_bg']
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    # Draw border
    border_color = (colors['text_dim'][0], colors['text_dim'][1], colors['text_dim'][2], 100)
    pygame.draw.rect(bg_surface, border_color, (0, 0, width, height), 1)
    surface.blit(bg_surface, (x, y))

def draw_header_background(surface, x, y, width, height, alpha=220):
    """Draw a semi-transparent background for headers."""
    colors = get_colors()
    bg_color = colors['top_bar_bg']
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    surface.blit(bg_surface, (x, y))
