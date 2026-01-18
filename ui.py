import pygame
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from character_profiles import MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA
from character_faces import get_face_data

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, param_name):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.param_name = param_name
        self.label = label
        self.dragging = False
        self.default_val = initial_val  # Store default for tick mark
        
        self.handle_width = 8
        self.handle_rect = pygame.Rect(x, y - 2, self.handle_width, height + 4)
        self.update_handle_pos(initial_val)
        
        self.font = pygame.font.SysFont(None, 20)  # Larger font

    def update_handle_pos(self, val):
        val = max(self.min_val, min(val, self.max_val))
        range_val = self.max_val - self.min_val
        pct = (val - self.min_val) / range_val
        px_x = self.rect.x + (pct * self.rect.width) - (self.handle_width / 2)
        self.handle_rect.x = px_x

    def get_default_x(self):
        """Get pixel X position for default value tick mark."""
        range_val = self.max_val - self.min_val
        pct = (self.default_val - self.min_val) / range_val
        return self.rect.x + (pct * self.rect.width)

    def get_value_from_pos(self, mouse_x):
        mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
        pct = (mouse_x - self.rect.left) / self.rect.width
        val = self.min_val + (pct * (self.max_val - self.min_val))
        return val
    
    def adjust_by_step(self, direction, profile):
        """Adjust value by a step. direction: -1 or +1"""
        current = getattr(profile, self.param_name)
        step = (self.max_val - self.min_val) / 20  # 5% steps
        new_val = current + (direction * step)
        new_val = max(self.min_val, min(new_val, self.max_val))
        setattr(profile, self.param_name, new_val)
        self.update_handle_pos(new_val)

    def handle_event(self, event, profile):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0], profile)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_val(event.pos[0], profile)

    def update_val(self, mouse_x, profile):
        val = self.get_value_from_pos(mouse_x)
        self.update_handle_pos(val)
        setattr(profile, self.param_name, val)

    def draw(self, surface, profile, highlighted=False):
        current_val = getattr(profile, self.param_name)
        
        # Label with larger font
        label_color = (255, 255, 100) if highlighted else (180, 180, 180)
        label_surf = self.font.render(f"{self.label}: {current_val:.2f}", True, label_color)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 16))
        
        # Track background
        track_color = (100, 100, 60) if highlighted else (60, 60, 60)
        pygame.draw.rect(surface, track_color, self.rect)
        
        # Default tick mark (white line)
        default_x = self.get_default_x()
        pygame.draw.line(surface, (255, 255, 255), 
                        (default_x, self.rect.y - 3), 
                        (default_x, self.rect.y + self.rect.height + 3), 2)
        
        # Handle
        if highlighted:
            handle_color = (255, 220, 0)
        elif self.dragging:
            handle_color = (255, 220, 0)
        else:
            handle_color = (160, 160, 160)
        pygame.draw.rect(surface, handle_color, self.handle_rect)

class ControlPanel:
    def __init__(self, player):
        self.player = player
        self.sliders = []
        self.rebind_mode = False
        self.selected_slider = 0  # Currently selected slider index
        self.physics_adjust_mode = False  # True when RB is held
        self.create_sliders()
        
    def create_sliders(self):
        """Create sliders for top-right physics section"""
        self.sliders = []
        profile = self.player.profile
        
        # Top right position - more spacing for larger font
        x_start = SCREEN_WIDTH - 180
        y_start = 55
        spacing = 32  # Increased spacing
        
        # Core physics sliders (compact)
        self.sliders.append(Slider(x_start, y_start + 0*spacing, 150, 6, 0.1, 2.0, profile.gravity, "Gravity", "gravity"))
        self.sliders.append(Slider(x_start, y_start + 1*spacing, 150, 6, 0.1, 2.5, profile.falling_gravity, "Fall Grav", "falling_gravity"))
        self.sliders.append(Slider(x_start, y_start + 2*spacing, 150, 6, 1.0, 12.0, profile.walk_speed, "Speed", "walk_speed"))
        self.sliders.append(Slider(x_start, y_start + 3*spacing, 150, 6, 0.05, 2.5, profile.acceleration, "Accel", "acceleration"))
        self.sliders.append(Slider(x_start, y_start + 4*spacing, 150, 6, 5.0, 20.0, profile.jump_force, "Jump", "jump_force"))
    
    def set_physics_mode(self, active):
        """Enable/disable physics adjustment mode."""
        self.physics_adjust_mode = active
    
    def navigate_slider(self, direction):
        """Move selection up (-1) or down (+1)."""
        if self.sliders:
            self.selected_slider = (self.selected_slider + direction) % len(self.sliders)
    
    def adjust_selected(self, direction):
        """Adjust selected slider value. direction: -1 (left) or +1 (right)."""
        if self.sliders:
            self.sliders[self.selected_slider].adjust_by_step(direction, self.player.profile)

    def handle_event(self, event):
        for slider in self.sliders:
            slider.handle_event(event, self.player.profile)

    def draw_left_panel(self, surface, keybindings):
        """Draw consolidated character info on left side"""
        profile = self.player.profile
        
        font_header = pygame.font.SysFont(None, 22, bold=True)
        font_text = pygame.font.SysFont(None, 18)
        font_small = pygame.font.SysFont(None, 16)
        
        x = 15
        y = 15
        
        # === CHARACTER ===
        # No header, just name and face
        
        # Face
        self.draw_character_face(surface, x, y, profile)
        
        # Name
        name_surf = font_header.render(profile.name, True, profile.color)
        surface.blit(name_surf, (x + 40, y + 8))
        
        y += 45
        
        # === ABILITIES ===
        header = font_header.render("ABILITIES", True, (100, 255, 150))
        surface.blit(header, (x, y))
        y += 22
        
        abilities = []
        if profile.has_wall_jump:
            abilities.append("Wall Jump")
        if profile.has_double_jump:
            abilities.append("Double Jump")
        if profile.has_dash:
            abilities.append("Dash")
        if profile.variable_jump:
            abilities.append("Variable Jump")
        if profile.has_momentum:
            abilities.append("Momentum")
        
        for ability in abilities:
            txt = font_small.render(f"• {ability}", True, (120, 220, 140))
            surface.blit(txt, (x, y))
            y += 18
        
        y += 8
        
        # === DESCRIPTION ===
        desc_lines = []
        words = profile.description.split()
        line = ""
        for word in words:
            if len(line + word) < 22:
                line += word + " "
            else:
                desc_lines.append(line)
                line = word + " "
        if line:
            desc_lines.append(line)
        
        font_desc = pygame.font.SysFont(None, 17, italic=True)
        for line in desc_lines:
            txt = font_desc.render(line.strip(), True, (180, 180, 180))
            surface.blit(txt, (x, y))
            y += 14
            
        y += 15
        
        # === CONTROLS ===
        header = font_header.render("CONTROLS", True, (255, 180, 100))
        surface.blit(header, (x, y))
        y += 20
        
        controls = [
            ("Move", "Arrows / Stick"),
            ("Jump", "Space / Btn A"),
            ("Run", "Shift / R1"),
            ("Dash", "X,C / Btn Y"),
            ("Reset Game", "R / Select"),
            ("Back to Default", "LB (Bumper)"),
            ("Randomize", "Share / 7"),
        ]
        
        for label, keys in controls:
            txt = font_text.render(f"{label}:", True, (150, 150, 150))
            surface.blit(txt, (x, y))
            key_txt = font_text.render(keys, True, (200, 200, 200))
            surface.blit(key_txt, (x + 70, y))
            y += 18
        
        y += 15
        
        # === SWITCHER ===
        header = font_header.render("SWITCHER", True, (200, 100, 255))
        surface.blit(header, (x, y))
        y += 20
        
        start_x_offset = 80 # Increased offset to accommodate "Char Select"
        
        switchers = [
            ("Char Select", "Hold LT"),
            ("Lvl Select", "Hold RT"),
        ]
        
        for label, keys in switchers:
            txt = font_text.render(f"{label}:", True, (150, 150, 150))
            surface.blit(txt, (x, y))
            key_txt = font_text.render(keys, True, (200, 200, 200))
            surface.blit(key_txt, (x + start_x_offset, y))
            y += 18



    def draw_character_face(self, surface, x, y, profile):
        """Draws a simple 8x8 pixel art face scaled up"""
        scale = 4
        pixels, color_map = get_face_data(profile.name, profile.color)
        
        # Draw
        for row in range(8):
            for col in range(8):
                if row < len(pixels) and col < len(pixels[row]):
                    char = pixels[row][col]
                    color = color_map.get(char, profile.color)
                    if color:
                        pygame.draw.rect(surface, color, (x + col*scale, y + row*scale, scale, scale))

    def draw_right_panel(self, surface, keybindings):
        """Draw physics sliders and controls on right side"""
        font_header = pygame.font.SysFont(None, 22, bold=True)
        font_text = pygame.font.SysFont(None, 18)
        
        x = SCREEN_WIDTH - 195
        y = 15
        
        # === PHYSICS HEADER ===
        header_color = (255, 200, 100) if self.physics_adjust_mode else (100, 180, 255)
        header_text = "PHYSICS (RB)" if self.physics_adjust_mode else "PHYSICS"
        header = font_header.render(header_text, True, header_color)
        surface.blit(header, (x, y))
        y += 25
        
        # Draw sliders with highlight for selected one
        for i, slider in enumerate(self.sliders):
            is_highlighted = self.physics_adjust_mode and i == self.selected_slider
            slider.draw(surface, self.player.profile, highlighted=is_highlighted)
        
        y = 225  # Adjusted for new spacing
        
        # Reset/Adjust Hints
        slider_x = SCREEN_WIDTH - 180
        reset_label = font_text.render("Reset All: LB", True, (150, 150, 150))
        surface.blit(reset_label, (slider_x, y))
        y += 18
        adjust_label = font_text.render("Adjust: Hold RB + D-Pad", True, (150, 150, 150))
        surface.blit(adjust_label, (slider_x, y))


    def draw(self, surface, keybindings):
        self.draw_left_panel(surface, keybindings)
        self.draw_right_panel(surface, keybindings)

def draw_level_selector(surface, playground, keybindings):
    """Draw horizontal level selector at top center"""
    font = pygame.font.SysFont(None, 18)
    font_header = pygame.font.SysFont(None, 20, bold=True)
    
    # Header
    header = font_header.render("LEVELS", True, (100, 200, 255))
    center_x = SCREEN_WIDTH // 2
    surface.blit(header, (center_x - 30, 15))
    
    # Horizontal list
    y = 38
    levels = [
        ("1", "Flat", 0, "playground_1"),
        ("2", "Wall", 1, "playground_2"),
        ("3", "SMB", 2, "playground_3"),
        ("4", "Cel", 3, "playground_4"),
        ("5", "N++", 4, "playground_5"),
        ("6", "Shaft", 5, "playground_6"),
    ]
    
    x_offset = center_x - 210
    for key, name, index, action in levels:
        if playground.current_playground == index:
            color = (255, 255, 100)
            bg = pygame.Rect(x_offset - 3, y - 2, 60, 20)
            pygame.draw.rect(surface, (50, 50, 50), bg)
            pygame.draw.rect(surface, color, bg, 1)
        else:
            color = (120, 120, 120)
        
        txt = font.render(f"[{key}] {name}", True, color)
        surface.blit(txt, (x_offset, y))
        x_offset += 70

def draw_selection_overlay(surface, mode_type, current_index, items):
    """
    Draw a large overlay for Character (LT) or Level (RT) selection
    mode_type: "CHARACTER" or "LEVEL"
    current_index: index of currently highlighted item
    items: list of (name, color, description) or similar info
    """
    # Semi-transparent background
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    font_header = pygame.font.SysFont(None, 48, bold=True)
    font_item = pygame.font.SysFont(None, 36)
    font_desc = pygame.font.SysFont(None, 24)
    
    # Header
    color = (255, 220, 100) if mode_type == "CHARACTER" else (100, 200, 255)
    header = font_header.render(f"SELECT {mode_type}", True, color)
    header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, 80))
    surface.blit(header, header_rect)
    
    # Draw items in a vertical list or grid
    start_y = 150
    spacing = 50
    
    for i, item in enumerate(items):
        name = item['name']
        
        # Highlight current selection
        if i == current_index:
            item_color = (255, 255, 255)
            # Arrow or Box
            arrow = font_item.render(">", True, (255, 255, 0))
            surface.blit(arrow, (SCREEN_WIDTH // 2 - 150, start_y + i * spacing))
        else:
            item_color = (150, 150, 150)
            
        text = font_item.render(name, True, item_color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
        surface.blit(text, rect)
        
    # Helper Text
    helper = font_desc.render("Use D-Pad to Select • Release Trigger to Confirm", True, (200, 200, 200))
    helper_rect = helper.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    surface.blit(helper, helper_rect)
