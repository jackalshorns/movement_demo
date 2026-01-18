import pygame
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from character_profiles import MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, param_name):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.param_name = param_name
        self.label = label
        self.dragging = False
        
        self.handle_width = 8
        self.handle_rect = pygame.Rect(x, y - 2, self.handle_width, height + 4)
        self.update_handle_pos(initial_val)
        
        self.font = pygame.font.SysFont(None, 16)

    def update_handle_pos(self, val):
        val = max(self.min_val, min(val, self.max_val))
        range_val = self.max_val - self.min_val
        pct = (val - self.min_val) / range_val
        px_x = self.rect.x + (pct * self.rect.width) - (self.handle_width / 2)
        self.handle_rect.x = px_x

    def get_value_from_pos(self, mouse_x):
        mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
        pct = (mouse_x - self.rect.left) / self.rect.width
        val = self.min_val + (pct * (self.max_val - self.min_val))
        return val

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

    def draw(self, surface, profile):
        current_val = getattr(profile, self.param_name)
        label_surf = self.font.render(f"{self.label}: {current_val:.1f}", True, (180, 180, 180))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 14))
        
        pygame.draw.rect(surface, (60, 60, 60), self.rect)
        color = (160, 160, 160) if not self.dragging else (255, 220, 0)
        pygame.draw.rect(surface, color, self.handle_rect)

class ControlPanel:
    def __init__(self, player):
        self.player = player
        self.sliders = []
        self.rebind_mode = False
        self.create_sliders()
        
    def create_sliders(self):
        """Create sliders for top-right physics section"""
        self.sliders = []
        profile = self.player.profile
        
        # Top right position
        x_start = SCREEN_WIDTH - 180
        y_start = 20
        spacing = 28
        
        # Core physics sliders (compact)
        self.sliders.append(Slider(x_start, y_start + 0*spacing, 150, 5, 0.1, 2.0, profile.gravity, "Gravity", "gravity"))
        self.sliders.append(Slider(x_start, y_start + 1*spacing, 150, 5, 0.1, 2.5, profile.falling_gravity, "Fall Grav", "falling_gravity"))
        self.sliders.append(Slider(x_start, y_start + 2*spacing, 150, 5, 1.0, 12.0, profile.walk_speed, "Speed", "walk_speed"))
        self.sliders.append(Slider(x_start, y_start + 3*spacing, 150, 5, 0.05, 2.5, profile.acceleration, "Accel", "acceleration"))
        self.sliders.append(Slider(x_start, y_start + 4*spacing, 150, 5, 5.0, 20.0, profile.jump_force, "Jump", "jump_force"))

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
        
        # === CHARACTER SELECTION ===
        header = font_header.render("CHARACTER", True, (255, 220, 100))
        surface.blit(header, (x, y))
        y += 25
        
        # Current character name in their color
        name_surf = font_header.render(profile.name, True, profile.color)
        surface.blit(name_surf, (x, y))
        y += 25
        
        # Hotkey hint
        for i, (name, prof, action) in enumerate([
            ("Mario", MARIO, "char_1"),
            ("Meat Boy", SUPER_MEAT_BOY, "char_2"),
            ("Link", ZELDA_LINK, "char_3"),
            ("Madeline", MADELINE, "char_4"),
            ("Ninja", N_NINJA, "char_5"),
        ]):
            key = keybindings.get_binding_display(action)
            if prof == profile:
                color = prof.color
                txt = font_text.render(f"[{key}] {name} ◀", True, color)
            else:
                color = (100, 100, 100)
                txt = font_small.render(f"[{key}] {name}", True, color)
            surface.blit(txt, (x, y))
            y += 20
        
        y += 10
        
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
        
        y += 10
        
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
        
        for line in desc_lines[:3]:
            txt = font_small.render(line.strip(), True, (150, 150, 150))
            surface.blit(txt, (x, y))
            y += 16

    def draw_right_panel(self, surface, keybindings):
        """Draw physics sliders and controls on right side"""
        font_header = pygame.font.SysFont(None, 20, bold=True)
        font_text = pygame.font.SysFont(None, 16)
        
        x = SCREEN_WIDTH - 195
        y = 15
        
        # === PHYSICS HEADER ===
        header = font_header.render("PHYSICS", True, (100, 180, 255))
        surface.blit(header, (x, y))
        y += 20
        
        # Draw sliders
        for slider in self.sliders:
            slider.draw(surface, self.player.profile)
        
        y = 165
        
        # === CONTROLS ===
        header = font_header.render("CONTROLS", True, (255, 180, 100))
        surface.blit(header, (x, y))
        y += 20
        
        controls = [
            ("Move", "Arrows / Stick"),
            ("Jump", "Space / Btn 0"),
            ("Run", "Shift / R1"),
            ("Dash", "X,C / Btn 2"),
            ("Reset", "R / Select"),
            ("Cycle Char", "LB (Bumper)"),
            ("Cycle Lvl", "RB (Bumper)"),
        ]
        
        for label, keys in controls:
            txt = font_text.render(f"{label}:", True, (150, 150, 150))
            surface.blit(txt, (x, y))
            key_txt = font_text.render(keys, True, (200, 200, 200))
            surface.blit(key_txt, (x + 70, y)) # Increased x offset for longer text
            y += 18
        
        y += 10
        
        # Rebind button hint
        rebind_txt = font_text.render("[K] Key Rebind", True, (180, 180, 100))
        surface.blit(rebind_txt, (x, y))

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
    
    # Randomize hint
    if playground.current_playground in [2, 3, 4, 5]: # SMB, Celeste, N++, Shaft
        hint = font.render("[7/Share] Randomize Layout", True, (180, 180, 100))
        center_text = hint.get_rect(center=(center_x, y + 22))
        surface.blit(hint, center_text)

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
