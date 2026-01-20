"""
Character rendering functions extracted from Player class.
Each function draws a specific character's sprite to the given surface.
"""

import pygame
import math


def add_character_outline(surface):
    """Add a thick outline around non-transparent pixels for High Contrast mode.
    Uses fast blit-based approach. Settings come from accessibility.py constants."""
    from accessibility import get_character_outline_settings
    
    settings = get_character_outline_settings()
    if not settings['enabled']:
        return surface
    
    thickness = settings['thickness']
    outline_color = settings['color']
    use_diamond = settings['diamond']
    
    width, height = surface.get_size()
    result = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Create a colored version of the sprite for the outline
    outline_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    outline_surf.blit(surface, (0, 0))
    # Set all non-transparent pixels to outline color
    outline_surf.fill(outline_color + (255,), special_flags=pygame.BLEND_RGB_MIN)
    
    # Draw the outline by blitting offset copies
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            # Use diamond or square shape based on settings
            if use_diamond:
                if abs(dx) + abs(dy) <= thickness + 1:
                    result.blit(outline_surf, (dx, dy))
            else:
                result.blit(outline_surf, (dx, dy))
    
    # Draw the original sprite on top
    result.blit(surface, (0, 0))
    
    return result


def get_effective_color(profile_color, is_skidding, on_wall, on_ground):
    """Determine the effective color based on player state."""
    if is_skidding:
        return (255, 200, 0)  # Yellow when skidding
    elif on_wall:
        return (200, 100, 255)  # Purple when wall sliding
    elif not on_ground:
        # Slightly lighter when in air
        return tuple(min(c + 30, 255) for c in profile_color)
    return profile_color


def calculate_leg_offset(velocity_x, on_ground, anim_offset):
    """Calculate leg animation offset and return (leg_offset, new_anim_offset)."""
    if abs(velocity_x) > 0.1 and on_ground:
        anim_offset += abs(velocity_x) * 0.15
        return math.sin(anim_offset) * 6, anim_offset
    return 0, anim_offset


def draw_mario(surface, center_x, color, velocity_x, on_ground, anim_offset):
    """Draw Mario character sprite."""
    # Red cap
    pygame.draw.circle(surface, color, (center_x, 9), 9)
    # Cap brim (wider)
    pygame.draw.rect(surface, color, (center_x - 11, 7, 22, 4))
    # "M" emblem on cap (simple)
    pygame.draw.circle(surface, (255, 255, 255), (center_x, 8), 3)
    # Face/head under cap
    pygame.draw.circle(surface, (255, 220, 177), (center_x, 18), 7)
    # Mustache (iconic!)
    pygame.draw.rect(surface, (80, 50, 30), (center_x - 6, 18, 12, 3))
    # Blue overalls body (rotund)
    pygame.draw.ellipse(surface, (40, 100, 220), (center_x - 9, 24, 18, 20))
    # Red shirt sleeves
    pygame.draw.circle(surface, color, (center_x - 11, 30), 4)
    pygame.draw.circle(surface, color, (center_x + 11, 30), 4)
    # Overall straps
    pygame.draw.line(surface, (40, 100, 220), (center_x - 3, 25), (center_x - 3, 28), 2)
    pygame.draw.line(surface, (40, 100, 220), (center_x + 3, 25), (center_x + 3, 28), 2)
    
    # Legs (blue pants)
    leg_offset, anim_offset = calculate_leg_offset(velocity_x, on_ground, anim_offset)
    pygame.draw.line(surface, (40, 100, 220), (center_x, 44), (center_x - 5 + leg_offset, 56), 4)
    pygame.draw.line(surface, (40, 100, 220), (center_x, 44), (center_x + 5 - leg_offset, 56), 4)
    # Brown shoes
    pygame.draw.circle(surface, (120, 70, 30), (center_x - 5 + leg_offset, 57), 3)
    pygame.draw.circle(surface, (120, 70, 30), (center_x + 5 - leg_offset, 57), 3)
    # White gloves on arms
    arm_y = 35 if on_ground else 30
    pygame.draw.circle(surface, (255, 255, 255), (center_x - 12, arm_y), 3)
    pygame.draw.circle(surface, (255, 255, 255), (center_x + 12, arm_y), 3)
    
    return anim_offset


def draw_meat_boy(surface, center_x, color, velocity_x, on_ground, anim_offset):
    """Draw Super Meat Boy character sprite - square cube shape."""
    # Main body - SQUARE cube (iconic Meat Boy shape)
    # Body is 28x28, feet add 8px more = 36 total height
    # Surface is 60px tall, so body_y = 60 - 36 - 2 = 22 for proper grounding
    body_size = 28
    body_x = center_x - body_size // 2
    body_y = 22  # Positioned to sit on ground properly
    
    # Main meaty body (square)
    pygame.draw.rect(surface, color, (body_x, body_y, body_size, body_size))
    
    # Meat texture highlights
    pygame.draw.rect(surface, (180, 70, 70), (body_x + 2, body_y + 2, 4, body_size - 4))
    pygame.draw.rect(surface, (180, 70, 70), (body_x + body_size - 6, body_y + 2, 4, body_size - 4))
    
    # Big white eyes (iconic - takes up most of face)
    eye_y = body_y + 8
    pygame.draw.ellipse(surface, (255, 255, 255), (center_x - 10, eye_y, 9, 12))
    pygame.draw.ellipse(surface, (255, 255, 255), (center_x + 1, eye_y, 9, 12))
    
    # Black pupils
    pygame.draw.circle(surface, (0, 0, 0), (center_x - 5, eye_y + 6), 3)
    pygame.draw.circle(surface, (0, 0, 0), (center_x + 5, eye_y + 6), 3)
    
    # Small grimace mouth
    pygame.draw.rect(surface, (60, 15, 15), (center_x - 5, body_y + 22, 10, 3))
    
    # Tiny stubby arms sticking out
    arm_y = body_y + 14
    pygame.draw.rect(surface, color, (body_x - 5, arm_y, 5, 6))
    pygame.draw.rect(surface, color, (body_x + body_size, arm_y, 5, 6))
    
    # Tiny stubby feet (no separate legs - just feet peeking out)
    foot_y = body_y + body_size
    leg_offset = 0
    if abs(velocity_x) > 0.1 and on_ground:
        anim_offset += abs(velocity_x) * 0.2
        leg_offset = math.sin(anim_offset) * 3
    
    pygame.draw.rect(surface, color, (center_x - 8 + leg_offset, foot_y, 7, 8))
    pygame.draw.rect(surface, color, (center_x + 1 - leg_offset, foot_y, 7, 8))
    
    return anim_offset


def draw_link(surface, center_x, color, velocity_x, on_ground, anim_offset):
    """Draw Link character sprite."""
    # Green pointy hat (triangle)
    pygame.draw.polygon(surface, color, [(center_x, 2), (center_x - 9, 13), (center_x + 9, 13)])
    # Hat detail (lighter green stripe)
    pygame.draw.polygon(surface, (60, 210, 60), [(center_x, 4), (center_x - 7, 13), (center_x + 7, 13)])
    # Blonde hair peeking out
    pygame.draw.rect(surface, (220, 190, 100), (center_x - 7, 13, 14, 3))
    # Face (peach/tan skin)
    pygame.draw.circle(surface, (255, 220, 177), (center_x, 20), 6)
    # Eyes (simple dots)
    pygame.draw.circle(surface, (40, 60, 120), (center_x - 2, 19), 1)
    pygame.draw.circle(surface, (40, 60, 120), (center_x + 2, 19), 1)
    # Green tunic body (triangular/trapezoid shape)
    pygame.draw.polygon(surface, color, [(center_x, 25), (center_x - 11, 28), (center_x - 9, 44), (center_x + 9, 44), (center_x + 11, 28)])
    # Belt (brown)
    pygame.draw.rect(surface, (120, 70, 30), (center_x - 9, 36, 18, 3))
    # Belt buckle (gold)
    pygame.draw.rect(surface, (220, 180, 50), (center_x - 2, 36, 4, 3))
    # White undershirt collar
    pygame.draw.rect(surface, (255, 255, 255), (center_x - 5, 25, 10, 2))
    # Green sleeves/arms
    pygame.draw.line(surface, color, (center_x - 10, 28), (center_x - 14, 36), 3)
    pygame.draw.line(surface, color, (center_x + 10, 28), (center_x + 14, 36), 3)
    
    # White tights/legs
    leg_offset, anim_offset = calculate_leg_offset(velocity_x, on_ground, anim_offset)
    pygame.draw.line(surface, (255, 255, 255), (center_x, 44), (center_x - 4 + leg_offset, 57), 3)
    pygame.draw.line(surface, (255, 255, 255), (center_x, 44), (center_x + 4 - leg_offset, 57), 3)
    # Brown boots
    pygame.draw.circle(surface, (120, 70, 30), (center_x - 4 + leg_offset, 58), 3)
    pygame.draw.circle(surface, (120, 70, 30), (center_x + 4 - leg_offset, 58), 3)
    # Hylian Shield (left side, blue and silver)
    pygame.draw.circle(surface, (180, 180, 200), (center_x - 15, 32), 5)
    pygame.draw.circle(surface, (60, 100, 180), (center_x - 15, 32), 3)
    
    return anim_offset


def draw_madeline(surface, center_x, color, velocity_x, on_ground, facing_right, anim_offset):
    """Draw Madeline character sprite."""
    # Face (peach skin)
    pygame.draw.circle(surface, (255, 220, 177), (center_x, 12), 6)
    # Eyes (simple dots, looking determined)
    pygame.draw.circle(surface, (60, 40, 30), (center_x - 2, 11), 1)
    pygame.draw.circle(surface, (60, 40, 30), (center_x + 2, 11), 1)
    
    # Iconic flowing strawberry-pink hair
    hair_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3
    # Main hair body
    pygame.draw.circle(surface, color, (center_x, 10), 7)
    # Hair direction: flows opposite to facing direction
    hair_direction = -1 if facing_right else 1
    pygame.draw.circle(surface, color, (center_x - 5 * hair_direction, 8), 4)
    # Flowing hair strands (animated, trail behind based on facing direction)
    pygame.draw.circle(surface, color, (center_x + hair_direction * (7 + hair_offset), 8), 4)
    pygame.draw.circle(surface, color, (center_x + hair_direction * (10 + hair_offset), 11), 3)
    pygame.draw.circle(surface, color, (center_x + hair_direction * (12 + hair_offset), 14), 2)
    
    # Blue jacket/hoodie body
    pygame.draw.rect(surface, (100, 160, 200), (center_x - 7, 17, 14, 20))
    # Jacket details (darker blue outline)
    pygame.draw.line(surface, (70, 120, 160), (center_x - 7, 17), (center_x - 7, 37), 1)
    pygame.draw.line(surface, (70, 120, 160), (center_x + 7, 17), (center_x + 7, 37), 1)
    # Zipper (white)
    pygame.draw.line(surface, (255, 255, 255), (center_x, 18), (center_x, 36), 1)
    # Arms with blue jacket sleeves
    arm_y = 25
    pygame.draw.line(surface, (100, 160, 200), (center_x - 7, arm_y), (center_x - 12, 35), 3)
    pygame.draw.line(surface, (100, 160, 200), (center_x + 7, arm_y), (center_x + 12, 35), 3)
    # Hands (peach)
    pygame.draw.circle(surface, (255, 220, 177), (center_x - 12, 35), 2)
    pygame.draw.circle(surface, (255, 220, 177), (center_x + 12, 35), 2)
    
    # Dark blue pants/legs
    leg_offset = 0
    if abs(velocity_x) > 0.1 and on_ground:
        anim_offset += abs(velocity_x) * 0.15
        leg_offset = math.sin(anim_offset) * 7
    pygame.draw.line(surface, (40, 50, 100), (center_x, 37), (center_x - 4 + leg_offset, 58), 3)
    pygame.draw.line(surface, (40, 50, 100), (center_x, 37), (center_x + 4 - leg_offset, 58), 3)
    # Shoes (white/grey)
    pygame.draw.circle(surface, (220, 220, 220), (center_x - 4 + leg_offset, 59), 2)
    pygame.draw.circle(surface, (220, 220, 220), (center_x + 4 - leg_offset, 59), 2)
    
    return anim_offset


def draw_ninja(surface, center_x, color, velocity_x, velocity_y, on_ground, facing_right, anim_offset):
    """Draw N++ Ninja character sprite."""
    # Dynamic leaning based on velocity
    lean = -velocity_x * 0.5

    # Head (small, sleek black circle)
    pygame.draw.circle(surface, (20, 20, 20), (center_x + int(lean * 0.3), 8), 6)
    # White eyes (ninja eyes visible through mask)
    eye_offset = int(velocity_x * 0.1)
    pygame.draw.circle(surface, (255, 255, 255), (center_x - 2 + eye_offset, 7), 1)
    pygame.draw.circle(surface, (255, 255, 255), (center_x + 2 + eye_offset, 7), 1)

    # Body (thin, sleek black ninja suit)
    body_top = (center_x + int(lean * 0.2), 14)
    body_bottom = (center_x, 40)
    pygame.draw.line(surface, (40, 40, 40), body_top, body_bottom, 2)

    # Ninja suit torso (slightly wider for body)
    pygame.draw.ellipse(surface, (40, 40, 40), (center_x - 5, 20, 10, 16))

    # Legs (long and sleek, animated)
    leg_offset = 0
    if abs(velocity_x) > 0.1 and on_ground:
        anim_offset += abs(velocity_x) * 0.15
        leg_offset = math.sin(anim_offset) * 8

    pygame.draw.line(surface, (40, 40, 40), body_bottom, (center_x - 4 + leg_offset + int(lean), 60), 2)
    pygame.draw.line(surface, (40, 40, 40), body_bottom, (center_x + 4 - leg_offset + int(lean), 60), 2)

    # Arms (long, fluid ninja arms)
    arm_back = (center_x - 12 + int(lean), 32)
    arm_forward = (center_x + 12 + int(lean), 28)
    pygame.draw.line(surface, (40, 40, 40), (center_x, 22), arm_back, 2)
    pygame.draw.line(surface, (40, 40, 40), (center_x, 22), arm_forward, 2)

    # Hands (small circles)
    pygame.draw.circle(surface, (40, 40, 40), arm_back, 2)
    pygame.draw.circle(surface, (40, 40, 40), arm_forward, 2)

    # ICONIC GOLD SCARF (signature N++ feature, flowing dynamically)
    scarf_color = (255, 200, 50)  # Gold/yellow scarf
    # Scarf trails behind based on movement or facing direction
    if abs(velocity_x) > 0.5:
        # When moving, scarf trails behind opposite to velocity
        scarf_end_x = center_x - int(velocity_x * 2.5)
        scarf_mid_x = center_x - int(velocity_x * 1.2)
    else:
        # When stationary, scarf hangs based on facing direction
        facing_offset = -12 if facing_right else 12
        scarf_end_x = center_x + facing_offset
        scarf_mid_x = center_x + facing_offset // 2
    scarf_end_y = 12 + int(abs(velocity_y) * 0.3)
    scarf_mid_y = 11 + int(abs(velocity_y) * 0.15)
    # Scarf base (attached to neck)
    pygame.draw.circle(surface, scarf_color, (center_x, 13), 3)
    # Flowing scarf trail (multiple segments for flow effect)
    pygame.draw.line(surface, scarf_color, (center_x, 13), (scarf_mid_x, scarf_mid_y), 3)
    pygame.draw.line(surface, scarf_color, (scarf_mid_x, scarf_mid_y), (scarf_end_x, scarf_end_y), 2)
    # Scarf tip
    pygame.draw.circle(surface, scarf_color, (scarf_end_x, scarf_end_y), 2)
    
    return anim_offset


def draw_default_stickman(surface, center_x, color, velocity_x, on_ground, anim_offset):
    """Draw default stickman character sprite."""
    pygame.draw.circle(surface, color, (center_x, 10), 8)
    pygame.draw.line(surface, color, (center_x, 18), (center_x, 40), 2)
    
    leg_offset, anim_offset = calculate_leg_offset(velocity_x, on_ground, anim_offset)
    pygame.draw.line(surface, color, (center_x, 40), (center_x - 5 + leg_offset, 60), 2)
    pygame.draw.line(surface, color, (center_x, 40), (center_x + 5 - leg_offset, 60), 2)
    pygame.draw.line(surface, color, (center_x, 25), (center_x - 10, 35), 2)
    pygame.draw.line(surface, color, (center_x, 25), (center_x + 10, 35), 2)
    
    return anim_offset


# Mapping of character names to their render functions
RENDERERS = {
    "Mario": draw_mario,
    "Super Meat Boy": draw_meat_boy,
    "Link": draw_link,
    "Madeline": draw_madeline,
    "Ninja (N++)": draw_ninja,
}


def render_character(player):
    """
    Main rendering function - dispatches to character-specific renderer.
    
    Args:
        player: Player object with all necessary state
        
    Returns:
        Updated anim_offset value
    """
    # Draw to temp surface first, then apply outline
    temp_surface = pygame.Surface((player.width, player.height), pygame.SRCALPHA)
    
    # Calculate effective color based on state
    color = get_effective_color(
        player.profile.color,
        player.is_skidding,
        player.on_wall,
        player.on_ground
    )
    
    # Apply colorblind adjustments to character color
    from accessibility import accessibility
    color = accessibility.adjust_color(color)
    
    center_x = player.width // 2
    name = player.profile.name
    anim_offset = player.anim_offset
    
    # Dispatch to character-specific renderer
    if name == "Mario":
        anim_offset = draw_mario(temp_surface, center_x, color, 
                         player.velocity.x, player.on_ground, player.anim_offset)
    elif name == "Super Meat Boy":
        # SMB needs rotation - draw to another temp surface then rotate
        smb_surface = pygame.Surface((player.width, player.height), pygame.SRCALPHA)
        anim_offset = draw_meat_boy(smb_surface, center_x, color,
                            player.velocity.x, player.on_ground, player.anim_offset)
        
        # Determine rotation angle based on surface contact
        rotation = 0
        if player.on_ceiling:
            rotation = 180  # Upside down on ceiling
        elif player.on_wall:
            if player.wall_direction == 1:  # Wall on right
                rotation = -90  # Feet point right
            else:  # Wall on left
                rotation = 90  # Feet point left
        
        if rotation != 0:
            rotated = pygame.transform.rotate(smb_surface, rotation)
            # Center the rotated surface
            rot_rect = rotated.get_rect(center=(player.width // 2, player.height // 2))
            temp_surface.blit(rotated, rot_rect)
        else:
            temp_surface.blit(smb_surface, (0, 0))
    elif name == "Link":
        anim_offset = draw_link(temp_surface, center_x, color,
                        player.velocity.x, player.on_ground, player.anim_offset)
    elif name == "Madeline":
        anim_offset = draw_madeline(temp_surface, center_x, color,
                            player.velocity.x, player.on_ground, player.facing_right, 
                            player.anim_offset)
    elif name == "Ninja (N++)":
        anim_offset = draw_ninja(temp_surface, center_x, color,
                         player.velocity.x, player.velocity.y, player.on_ground,
                         player.facing_right, player.anim_offset)
    else:
        anim_offset = draw_default_stickman(temp_surface, center_x, color,
                                     player.velocity.x, player.on_ground, player.anim_offset)
    
    # Apply High Contrast outline if enabled (settings from accessibility.py)
    outlined = add_character_outline(temp_surface)
    
    # Copy to player.image
    player.image.fill((0, 0, 0, 0))
    player.image.blit(outlined, (0, 0))
    
    return anim_offset
