"""
Pixel art face definitions for each character.
Each face is an 8x8 grid of characters that map to colors.
"""

# Default simple face
DEFAULT_FACE = [
    "........",
    ".XXXXXX.",
    ".X....X.",
    ".X.O.O.X.",
    ".X....X.",
    ".X.XX.X.",
    ".XXXXXX.",
    "........"
]

MARIO_FACE = [
    "..RRR...",
    ".RRRRR..",
    "..SSSS..",
    "..SOSS..",
    "...SS...",
    "..RRRR..",
    ".R.RR.R.",
    ".B.B..B."
]

MEAT_BOY_FACE = [
    "........",
    ".RRRRRR.",
    ".R....R.",
    ".R.O.O.R.",
    ".R....R.",
    ".R.RR.R.",
    ".RRRRRR.",
    "........"
]

LINK_FACE = [
    "..GGG...",
    ".GGGGG..",
    "..SSSS..",
    "..SOSS..",
    "...SS...",
    "..GGGG..",
    ".G.GG.G.",
    "........"
]

MADELINE_FACE = [
    "..RRR...",
    ".RRRRR..",
    ".RSSSS..",
    ".RSOSS..",
    ".RSSSS..",
    "..BBBB..",
    "........",
    "........"
]

NINJA_FACE = [
    "........",
    ".KKKKK..",
    ".KSSSSK.",
    ".KSOSSK.",
    ".KKKKK..",
    "..KKK...",
    ".K.K.K..",
    "........"
]


# Color mappings for each character
def get_face_data(profile_name, profile_color):
    """
    Get pixel art face and color map for a character.
    
    Returns:
        (pixels, color_map) tuple
    """
    # Base colors
    skin = (255, 200, 150)
    eye = (0, 0, 0)
    
    base_color_map = {
        '.': None, 
        'X': profile_color, 
        'O': eye, 
        'S': skin,
        'R': (200, 50, 50),
        'G': (50, 200, 50)
    }
    
    if profile_name == "Mario":
        return MARIO_FACE, {**base_color_map, 'B': (50, 50, 200)}
    
    elif profile_name == "Super Meat Boy":
        return MEAT_BOY_FACE, {**base_color_map, 'R': (180, 50, 50)}
    
    elif profile_name == "Link":
        return LINK_FACE, base_color_map
    
    elif profile_name == "Madeline":
        return MADELINE_FACE, {
            **base_color_map,
            'R': (255, 100, 80),  # Hair
            'B': (50, 50, 150)    # Shirt
        }
    
    elif "Ninja" in profile_name:
        return NINJA_FACE, {**base_color_map, 'K': (50, 50, 50)}
    
    else:
        return DEFAULT_FACE, base_color_map
