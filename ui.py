import pygame
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from character_profiles import MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA
from character_faces import get_face_data

# Cached fonts for PS5 button icons (avoid creating every frame)
_ps5_button_fonts = {}

def _get_ps5_font(size, bold=False):
    """Get cached font for PS5 button text."""
    key = (size, bold)
    if key not in _ps5_button_fonts:
        _ps5_button_fonts[key] = pygame.font.SysFont(None, size, bold=bold)
    return _ps5_button_fonts[key]


# Cache for pre-rendered PS5 button icons
_ps5_button_cache = {}

def _create_ps5_button_surface(button_type, size):
    """Create a high-quality PS5 button icon using supersampling."""
    # Supersample at 4x for anti-aliasing
    scale = 4
    big_size = size * scale
    
    # Create surface with alpha
    big_surface = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
    
    circle_color = (58, 58, 62)  # Dark charcoal like official PS5
    symbol_color = (255, 255, 255)  # White symbol
    
    center = big_size // 2
    radius = (big_size - 4) // 2
    
    # Draw filled circle background
    pygame.draw.circle(big_surface, circle_color, (center, center), radius)
    
    if button_type == 'x':
        # X cross - two diagonal lines (BOLD)
        offset = big_size // 4
        thickness = max(6, big_size // 8)  # Much thicker
        pygame.draw.line(big_surface, symbol_color, 
                        (center - offset, center - offset), 
                        (center + offset, center + offset), thickness)
        pygame.draw.line(big_surface, symbol_color, 
                        (center + offset, center - offset), 
                        (center - offset, center + offset), thickness)
                        
    elif button_type == 'square':
        # Hollow square (BOLD)
        sq_size = big_size // 3
        thickness = max(5, big_size // 9)  # Much thicker
        pygame.draw.rect(big_surface, symbol_color, 
                        (center - sq_size, center - sq_size, sq_size * 2, sq_size * 2), thickness)
                        
    elif button_type == 'circle':
        # Hollow circle (BOLD)
        inner_radius = big_size // 4
        thickness = max(5, big_size // 9)  # Much thicker
        pygame.draw.circle(big_surface, symbol_color, (center, center), inner_radius, thickness)
        
    elif button_type == 'triangle':
        # Hollow equilateral triangle pointing up (BOLD)
        tri_size = big_size // 3
        tri_width = int(tri_size * 1.1)
        thickness = max(5, big_size // 9)  # Much thicker
        y_offset = big_size // 24
        
        points = [
            (center, center - tri_size - y_offset),
            (center - tri_width, center + tri_size // 2 - y_offset),
            (center + tri_width, center + tri_size // 2 - y_offset),
        ]
        pygame.draw.polygon(big_surface, symbol_color, points, thickness)
    
    elif button_type in ('l1', 'r1', 'l2', 'r2'):
        # Shoulder/trigger buttons - sized to match target height
        # Work at 4x scale for anti-aliasing, then scale down
        scale = 4
        target_height = size * scale
        
        # Font fills 85% of height (minimal padding)
        font_size = int(target_height * 0.85)
        font = pygame.font.SysFont(None, font_size, bold=True)
        txt = font.render(button_type.upper(), True, symbol_color)
        
        # Minimal padding
        padding_x = int(target_height * 0.12)
        padding_y = int(target_height * 0.05)
        
        rect_width = txt.get_width() + padding_x * 2
        rect_height = txt.get_height() + padding_y * 2
        
        # Create surface
        big_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        
        # Draw rounded rectangle background
        pygame.draw.rect(big_surface, circle_color, (0, 0, rect_width, rect_height), border_radius=rect_height // 4)
        
        # Draw text
        big_surface.blit(txt, (padding_x, padding_y))
        
        # Scale down to target size
        final_height = size
        final_width = int(rect_width * size / rect_height)
        small_surface = pygame.transform.smoothscale(big_surface, (final_width, final_height))
        return small_surface
    
    # Scale down with smooth anti-aliasing
    small_surface = pygame.transform.smoothscale(big_surface, (size, size))
    return small_surface

def draw_ps5_button(surface, x, y, button_type, size=20):
    """
    Draw a PS5-style button icon at the given position.
    button_type: 'x', 'square', 'circle', 'triangle', 'l1', 'r1', 'l2', 'r2', 'options'
    Returns the width of the drawn element for text positioning.
    """
    if button_type in ('x', 'square', 'circle', 'triangle'):
        # Use cached high-quality icon
        cache_key = (button_type, size)
        if cache_key not in _ps5_button_cache:
            _ps5_button_cache[cache_key] = _create_ps5_button_surface(button_type, size)
        
        icon = _ps5_button_cache[cache_key]
        surface.blit(icon, (x, y))
        return size + 4
        
    elif button_type in ('l1', 'r1', 'l2', 'r2'):
        # Use cached high-quality shoulder/trigger icon
        cache_key = (button_type, size)
        if cache_key not in _ps5_button_cache:
            _ps5_button_cache[cache_key] = _create_ps5_button_surface(button_type, size)
        
        icon = _ps5_button_cache[cache_key]
        surface.blit(icon, (x, y))
        return icon.get_width() + 4
        
    elif button_type == 'options':
        font = _get_ps5_font(14)
        txt = font.render("OPTIONS", True, (80, 82, 90))
        surface.blit(txt, (x, y + 2))
        return txt.get_width() + 4
        
    return 0

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
        self._current_value = val  # Store internally
        if profile is not None:
            setattr(profile, self.param_name, val)
    
    def get_value(self):
        """Get current slider value."""
        return getattr(self, '_current_value', self.default_val)

    def draw(self, surface, profile, highlighted=False):
        if profile is not None:
            current_val = getattr(profile, self.param_name)
        else:
            current_val = self.get_value()
        
        # Label with better contrast
        if highlighted:
            label_color = (255, 255, 100)  # Yellow when selected
        else:
            label_color = (60, 60, 70)  # Dark gray for light theme readability
        
        # Format differently for integer vs float values
        if current_val == int(current_val):
            label_surf = self.font.render(f"{self.label}: {int(current_val)}", True, label_color)
        else:
            label_surf = self.font.render(f"{self.label}: {current_val:.2f}", True, label_color)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 18))
        
        # Track background
        track_color = (100, 100, 60) if highlighted else (140, 145, 160)
        pygame.draw.rect(surface, track_color, self.rect)
        
        # Default tick mark - ALWAYS GREEN per user request
        default_x = self.get_default_x()
        tick_color = (50, 180, 80)  # Green for default position
        pygame.draw.line(surface, tick_color, 
                        (default_x, self.rect.y - 4), 
                        (default_x, self.rect.y + self.rect.height + 4), 3)
        
        # Handle
        if highlighted:
            handle_color = (255, 220, 0)
        elif self.dragging:
            handle_color = (255, 220, 0)
        else:
            handle_color = (160, 160, 160)
        pygame.draw.rect(surface, handle_color, self.handle_rect)

class ControlPanel:
    def __init__(self, player, sound_manager=None):
        self.player = player
        self.sound_manager = sound_manager
        self.sliders = []
        self.rebind_mode = False
        self.selected_slider = 0  # Currently selected slider index
        self.physics_adjust_mode = False  # True when RB is held
        self.volume = 70  # Default volume 0-100
        
        # SETTINGS mode state (L1 held, like physics RB)
        self.visuals_adjust_mode = False
        self.visuals_selected = 0  # 0 = Color Blind, 1 = Theme, 2 = Sound
        self.sound_volume = 0.0  # 0.0 to 1.0, default muted
        
        # Reset toggle state (Current/Reset)
        self.reset_toggle_state = "Current"  # or "Reset"
        
        # Text input state for LLM customization
        self.text_input_active = False  # True when typing in customize box
        self.customize_text = ""  # User's typed text
        self.cursor_blink_timer = 0  # For blinking cursor animation
        self.llm_processing = False  # True while waiting for LLM response
        self.llm_status = ""  # Status message ("Processing...", "Error: ...", etc.)
        
        # Import accessibility settings
        from accessibility import accessibility
        self.accessibility = accessibility
        
        self.create_sliders()
        
    def create_sliders(self):
        """Create sliders for physics widget"""
        from ui_theme import RIGHT_PANEL_Y, SLIDER_WIDTH, MARGIN_RIGHT
        
        self.sliders = []
        profile = self.player.profile
        
        # Position inside physics widget (more generous spacing)
        x_start = SCREEN_WIDTH - SLIDER_WIDTH - MARGIN_RIGHT - 30
        y_start = RIGHT_PANEL_Y + 20  # Inside widget
        spacing = 40  # More breathing room
        
        # Core physics sliders (5 sliders)
        self.sliders.append(Slider(x_start, y_start + 0*spacing, 155, 10, 0.1, 2.0, profile.gravity, "Gravity", "gravity"))
        self.sliders.append(Slider(x_start, y_start + 1*spacing, 155, 10, 0.1, 2.5, profile.falling_gravity, "Fall Grav", "falling_gravity"))
        self.sliders.append(Slider(x_start, y_start + 2*spacing, 155, 10, 1.0, 12.0, profile.walk_speed, "Speed", "walk_speed"))
        self.sliders.append(Slider(x_start, y_start + 3*spacing, 155, 10, 0.05, 2.5, profile.acceleration, "Accel", "acceleration"))
        self.sliders.append(Slider(x_start, y_start + 4*spacing, 155, 10, 5.0, 20.0, profile.jump_force, "Jump", "jump_force"))
        
        # Volume slider not in this panel
        self.volume_slider_index = len(self.sliders)
        
        # Customize text box is selectable (index = len(sliders))
        self.customize_index = len(self.sliders)
        
        # Reset to Default is selectable (index = len(sliders) + 1)
        self.reset_index = len(self.sliders) + 1
        
        # Total includes sliders + Customize + Reset
        self.total_settings_count = len(self.sliders) + 2
        
    def set_physics_mode(self, active):
        """Enable/disable physics adjustment mode."""
        self.physics_adjust_mode = active
    
    def set_visuals_mode(self, active):
        """Enable/disable VISUALS adjustment mode (L1 held)."""
        self.visuals_adjust_mode = active
    
    def navigate_visuals(self, direction):
        """Navigate up/down in SETTINGS options."""
        self.visuals_selected = (self.visuals_selected + direction) % 3  # 3 items now
    
    def adjust_visuals(self, direction):
        """Adjust selected SETTINGS option."""
        from ui_theme import theme
        
        if self.visuals_selected == 0:  # Color Blind
            mode = self.accessibility.cycle_mode(direction)
            print(f"Color Blind mode: {mode}")
        elif self.visuals_selected == 1:  # Light/Dark
            new_theme = theme.toggle()
            print(f"Theme: {new_theme}")
        elif self.visuals_selected == 2:  # Sound (log scale)
            # Log scale steps: 0, 0.01, 0.03, 0.1, 0.3, 1.0
            log_steps = [0.0, 0.01, 0.03, 0.1, 0.3, 1.0]
            # Find current step
            current_idx = 0
            for i, val in enumerate(log_steps):
                if self.sound_volume <= val:
                    current_idx = i
                    break
                current_idx = len(log_steps) - 1
            # Move to next/prev step
            new_idx = max(0, min(len(log_steps) - 1, current_idx + direction))
            self.sound_volume = log_steps[new_idx]
            # Apply to sound manager if available
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.set_volume(self.sound_volume)
            print(f"Sound: {int(self.sound_volume * 100)}%")
    
    def navigate_slider(self, direction):
        """Move selection up (-1) or down (+1)."""
        self.selected_slider = (self.selected_slider + direction) % self.total_settings_count
    
    def adjust_selected(self, direction):
        """Adjust selected physics slider value or trigger actions."""
        
        # Customize - no adjustment (X button to activate in future)
        if self.selected_slider == self.customize_index:
            return
        
        # Reset - no D-pad toggle, use X button to activate
        if self.selected_slider == self.reset_index:
            return  # Don't do anything on D-pad, wait for X button
        
        # Regular sliders
        if self.selected_slider < len(self.sliders):
            slider = self.sliders[self.selected_slider]
            # Volume slider is handled differently (no profile)
            if self.selected_slider == self.volume_slider_index:
                step = 5  # 5% steps for volume
                new_val = slider.get_value() + (direction * step)
                new_val = max(slider.min_val, min(new_val, slider.max_val))
                slider._current_value = new_val
                slider.update_handle_pos(new_val)
                if self.sound_manager:
                    self.sound_manager.set_volume(new_val / 100.0)
            else:
                slider.adjust_by_step(direction, self.player.profile)

    def activate_selected(self):
        """Handle X button press on selected item."""
        # Reset button - X activates reset
        if self.selected_slider == self.reset_index:
            self.player.profile.reset_physics()
            self.create_sliders()
            print(f"Physics reset to defaults for {self.player.profile.name}")
            return True
        
        # Customize - X opens text input mode
        if self.selected_slider == self.customize_index:
            self.text_input_active = True
            self.customize_text = ""  # Clear for new input
            self.llm_status = ""
            print("Text input mode activated - type your physics description")
            return True
        
        return False
    
    def handle_text_input(self, event):
        """Handle keyboard input when text input mode is active."""
        if not self.text_input_active:
            return False
        
        if event.type != pygame.KEYDOWN:
            return True  # Consume event but do nothing
        
        if event.key == pygame.K_RETURN:
            # Submit text to LLM
            if self.customize_text.strip():
                self._submit_to_llm()
            else:
                self.text_input_active = False
            return True
        
        elif event.key == pygame.K_ESCAPE:
            # Cancel text input
            self.text_input_active = False
            self.customize_text = ""
            self.llm_status = ""
            return True
        
        elif event.key == pygame.K_BACKSPACE:
            # Delete last character
            self.customize_text = self.customize_text[:-1]
            return True
        
        elif event.unicode and event.unicode.isprintable():
            # Add character (limit length)
            if len(self.customize_text) < 60:
                self.customize_text += event.unicode
            return True
        
        return True
    
    def _submit_to_llm(self):
        """Submit text to LLM for processing."""
        import llm_physics
        
        self.llm_processing = True
        self.llm_status = "Processing..."
        self.text_input_active = False
        
        def on_llm_response(result, error):
            self.llm_processing = False
            if error:
                self.llm_status = f"Error: {error[:30]}"
                print(f"[LLM] Error: {error}")
            else:
                self.llm_status = "Applied!"
                llm_physics.apply_physics(self.player.profile, result, self)
                print(f"[LLM] Applied physics: {result}")
        
        llm_physics.process_description(self.customize_text, callback=on_llm_response)

    def handle_event(self, event):
        for i, slider in enumerate(self.sliders):
            if i == self.volume_slider_index:
                # Handle volume slider with None profile
                old_val = slider.get_value()
                slider.handle_event(event, None)
                new_val = slider.get_value()
                if old_val != new_val and self.sound_manager:
                    self.sound_manager.set_volume(new_val / 100.0)
            else:
                slider.handle_event(event, self.player.profile)

    def draw_left_panel(self, surface, keybindings):
        """Draw left panel with Abilities, Controls, Accessibility sections"""
        from ui_theme import (font_header, font_text, font_small, get_colors, theme,
                              LEFT_PANEL_X, LEFT_PANEL_Y, LEFT_PANEL_WIDTH,
                              SPACING_LINE, SPACING_ITEM, SPACING_SECTION,
                              draw_widget_background)
        
        colors = get_colors()
        profile = self.player.profile
        
        # Draw boxed widget background
        widget_height = 340
        draw_widget_background(surface, LEFT_PANEL_X, LEFT_PANEL_Y, LEFT_PANEL_WIDTH, widget_height)
        
        x = LEFT_PANEL_X + 10
        y = LEFT_PANEL_Y + 12
        
        # === ABILITIES ===
        header = font_header().render("ABILITIES", True, colors['header_red'])
        surface.blit(header, (x, y))
        y += SPACING_ITEM
        
        abilities = []
        if profile.variable_jump:
            abilities.append("Variable Jump")
        if profile.has_momentum:
            abilities.append("Momentum")
        if profile.has_wall_jump:
            abilities.append("Wall Jump")
        if profile.has_double_jump:
            abilities.append("Double Jump")
        if profile.has_dash:
            abilities.append("Dash")
        
        for ability in abilities[:3]:  # Limit to 3 for space
            txt = font_text().render(f"• {ability}", True, colors['text_bright'])
            surface.blit(txt, (x, y))
            y += SPACING_LINE - 2
        
        y += SPACING_SECTION
        
        # === CONTROLS ===
        header = font_header().render("CONTROLS", True, colors['header_red'])
        surface.blit(header, (x, y))
        y += SPACING_ITEM
        
        # Controls with icons
        # Move: Stick / D-Pad (text only)
        txt = font_text().render("Move: Stick / D-Pad", True, colors['text_bright'])
        surface.blit(txt, (x, y))
        y += SPACING_LINE - 2
        
        # Jump: [X icon] - 1.5x size for visibility
        txt = font_text().render("Jump:", True, colors['text_bright'])
        surface.blit(txt, (x, y))
        btn_size = int(txt.get_height() * 1.5)
        draw_ps5_button(surface, x + txt.get_width() + 5, y - (btn_size - txt.get_height()) // 2, 'x', btn_size)
        y += SPACING_LINE - 2
        
        # Run/Dash: [Square icon] - 1.5x size for visibility
        txt = font_text().render("Run/Dash:", True, colors['text_bright'])
        surface.blit(txt, (x, y))
        btn_size = int(txt.get_height() * 1.5)
        draw_ps5_button(surface, x + txt.get_width() + 5, y - (btn_size - txt.get_height()) // 2, 'square', btn_size)
        y += SPACING_LINE - 2
        
        y += SPACING_SECTION
        
        # === SETTINGS with L1 icon ===
        header_color = colors['header_orange'] if self.visuals_adjust_mode else colors['header_red']
        header = font_header().render("SETTINGS", True, header_color)
        surface.blit(header, (x, y))
        draw_ps5_button(surface, x + header.get_width() + 8, y, 'l1', header.get_height())
        y += SPACING_ITEM
        
        # Color Blind toggle (index 0)
        is_selected = self.visuals_adjust_mode and self.visuals_selected == 0
        color = colors['highlight'] if is_selected else colors['text_bright']
        cb_value = self.accessibility.colorblind_mode
        if is_selected:
            txt = font_text().render(f"< Color Blind: {cb_value} >", True, color)
        else:
            txt = font_text().render(f"Color Blind: {cb_value}", True, color)
        surface.blit(txt, (x, y))
        y += SPACING_LINE
        
        # Light/Dark toggle (index 1)
        is_selected = self.visuals_adjust_mode and self.visuals_selected == 1
        color = colors['highlight'] if is_selected else colors['text_bright']
        theme_value = theme.current
        if is_selected:
            txt = font_text().render(f"< Theme: {theme_value} >", True, color)
        else:
            txt = font_text().render(f"Theme: {theme_value}", True, color)
        surface.blit(txt, (x, y))
        y += SPACING_LINE
        
        # Sound volume (index 2)
        is_selected = self.visuals_adjust_mode and self.visuals_selected == 2
        color = colors['highlight'] if is_selected else colors['text_bright']
        # Get volume as percentage (0-100)
        volume_pct = int(self.sound_volume * 100)
        if is_selected:
            txt = font_text().render(f"< Sound: {volume_pct}% >", True, color)
        else:
            txt = font_text().render(f"Sound: {volume_pct}%", True, color)
        surface.blit(txt, (x, y))



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
        """Draw settings widget on right side - one unified panel"""
        from ui_theme import (font_header, font_text, font_small, get_colors, theme,
                              MARGIN_RIGHT, SPACING_ITEM, RIGHT_PANEL_Y,
                              SLIDER_WIDTH, draw_widget_background)
        
        colors = get_colors()
        
        # === ONE UNIFIED PANEL ===
        widget_x = SCREEN_WIDTH - SLIDER_WIDTH - MARGIN_RIGHT - 45
        widget_y = RIGHT_PANEL_Y
        widget_width = SLIDER_WIDTH + 60
        # Calculate total height for sliders + customize + reset
        total_height = 400  # Enough for sliders + customize box + reset
        
        # Draw single unified background
        draw_widget_background(surface, widget_x, widget_y, widget_width, total_height)
        
        # === SLIDERS ===
        for i, slider in enumerate(self.sliders):
            is_highlighted = self.physics_adjust_mode and i == self.selected_slider
            if i == self.volume_slider_index:
                continue  # Skip volume slider in this panel
            slider.draw(surface, self.player.profile, highlighted=is_highlighted)
        
        # === CUSTOMIZE SECTION ===
        customize_y = widget_y + 225  # After sliders
        
        # Check if Customize is selected
        is_customize_selected = self.physics_adjust_mode and self.selected_slider == self.customize_index
        
        # Header "Customize" - highlight when selected
        if is_customize_selected or self.text_input_active:
            customize_color = (255, 220, 100)  # Yellow when selected
        else:
            customize_color = colors['header_blue']
        customize_txt = font_header().render("Customize", True, customize_color)
        surface.blit(customize_txt, (widget_x + 12, customize_y))
        
        # Show X button hint when selected
        if is_customize_selected and not self.text_input_active:
            hint_txt = font_small().render("Press", True, colors['text_dim'])
            surface.blit(hint_txt, (widget_x + 12 + customize_txt.get_width() + 8, customize_y + 4))
            draw_ps5_button(surface, widget_x + 12 + customize_txt.get_width() + 8 + hint_txt.get_width() + 4, customize_y, 'x', customize_txt.get_height())
        
        # Light grey text box for description
        textbox_y = customize_y + 30
        textbox_height = 75
        
        # Textbox color changes based on state
        if self.text_input_active:
            textbox_color = (255, 255, 240)  # Bright when editing
            border_color = (255, 200, 0)  # Yellow border
            border_width = 2
        elif is_customize_selected:
            textbox_color = (240, 245, 255)  # Slightly highlighted
            border_color = (150, 160, 200)
            border_width = 2
        else:
            textbox_color = (225, 228, 235)  # Light grey
            border_color = (180, 185, 195)
            border_width = 1
        
        pygame.draw.rect(surface, textbox_color, 
                        (widget_x + 10, textbox_y, widget_width - 20, textbox_height))
        pygame.draw.rect(surface, border_color, 
                        (widget_x + 10, textbox_y, widget_width - 20, textbox_height), border_width)
        
        # Determine what text to show
        if self.text_input_active or self.customize_text:
            # Show user's typed text
            display_text = self.customize_text
            text_color = (30, 30, 40)  # Dark text
            
            # Word wrap the text
            desc_lines = []
            words = display_text.split() if display_text else []
            line = ""
            for word in words:
                if len(line + word) < 22:
                    line += word + " "
                else:
                    desc_lines.append(line)
                    line = word + " "
            if line or not words:
                desc_lines.append(line)
            
            text_y = textbox_y + 10
            for i, line in enumerate(desc_lines[:3]):
                txt = font_text().render(line, True, text_color)
                surface.blit(txt, (widget_x + 18, text_y))
                text_y += 22
            
            # Draw blinking cursor when active
            if self.text_input_active:
                self.cursor_blink_timer = (self.cursor_blink_timer + 1) % 60
                if self.cursor_blink_timer < 30:
                    # Calculate cursor position
                    last_line = desc_lines[-1] if desc_lines else ""
                    cursor_x = widget_x + 18 + font_text().size(last_line)[0]
                    cursor_y = textbox_y + 10 + (len(desc_lines) - 1) * 22
                    pygame.draw.line(surface, (0, 0, 0), 
                                    (cursor_x, cursor_y), 
                                    (cursor_x, cursor_y + 18), 2)
        
        elif self.llm_processing or self.llm_status:
            # Show LLM status
            if self.llm_processing:
                status_text = "Processing..."
                status_color = (100, 150, 255)
            elif "Error" in self.llm_status:
                status_text = self.llm_status
                status_color = (255, 100, 100)
            else:
                status_text = self.llm_status
                status_color = (100, 200, 100)
            
            txt = font_text().render(status_text, True, status_color)
            surface.blit(txt, (widget_x + 18, textbox_y + 28))
        
        else:
            # Show default description
            profile = self.player.profile
            desc_lines = []
            words = profile.description.split()
            line = ""
            for word in words:
                if len(line + word) < 24:
                    line += word + " "
                else:
                    desc_lines.append(line)
                    line = word + " "
            if line:
                desc_lines.append(line)
            
            text_y = textbox_y + 10
            text_color = (60, 65, 75)  # Dark text on light bg
            for line in desc_lines[:3]:  # Limit to 3 lines
                txt = font_text().render(line.strip(), True, text_color)
                surface.blit(txt, (widget_x + 18, text_y))
                text_y += 22
        
        # === RESET SECTION ===
        reset_y = textbox_y + textbox_height + 15
        reset_color = colors['header_blue']
        
        reset_txt = font_header().render("Reset", True, reset_color)
        surface.blit(reset_txt, (widget_x + 12, reset_y))
        
        # Draw R1 + Triangle icons - sized to match Reset text height
        icon_size = reset_txt.get_height()
        icon_x = widget_x + 12 + reset_txt.get_width() + 12
        icon_y = reset_y
        
        # "Press" text
        press_txt = font_small().render("Press", True, colors['text_dim'])
        surface.blit(press_txt, (icon_x, icon_y + (icon_size - press_txt.get_height()) // 2))
        icon_x += press_txt.get_width() + 5
        
        # R1 button
        r1_width = draw_ps5_button(surface, icon_x, icon_y, 'r1', icon_size)
        icon_x += r1_width + 2
        
        # + text
        plus_txt = font_small().render("+", True, colors['text_dim'])
        surface.blit(plus_txt, (icon_x, icon_y + (icon_size - plus_txt.get_height()) // 2))
        icon_x += plus_txt.get_width() + 2
        
        # Triangle button
        draw_ps5_button(surface, icon_x, icon_y, 'triangle', icon_size)

    def draw_top_row(self, surface, playground):
        """Draw top row: Character (L2) | Level (R2) | PHYSICS (R1)"""
        from ui_theme import (font_header, font_large, font_text, get_colors,
                              TOP_ROW_Y, MARGIN_LEFT, MARGIN_RIGHT)
        
        colors = get_colors()
        y = TOP_ROW_Y
        
        # === LEFT: Character name with face ===
        x = MARGIN_LEFT
        profile = self.player.profile
        self.draw_character_face(surface, x, y - 5, profile)
        
        # Character name
        name_surf = font_header().render(profile.name, True, profile.color)
        surface.blit(name_surf, (x + 42, y))
        
        # L2 icon hint - sized to match name text height
        draw_ps5_button(surface, x + 45 + name_surf.get_width() + 10, y, 'l2', name_surf.get_height())
        
        # === CENTER: Level name ===
        if playground:
            level_name = playground.get_name().upper()
            level_surf = font_large().render(level_name, True, colors['text_bright'])
            level_rect = level_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 10))
            surface.blit(level_surf, level_rect)
            
            # R2 icon hint - sized to match level text height
            draw_ps5_button(surface, level_rect.right + 10, level_rect.top, 'r2', level_surf.get_height())
        
        # === RIGHT: PHYSICS header ===
        physics_txt = font_header().render("PHYSICS", True, colors['header_blue'])
        physics_x = SCREEN_WIDTH - MARGIN_RIGHT - physics_txt.get_width() - 50
        surface.blit(physics_txt, (physics_x, y))
        
        # R1 icon hint - sized to match PHYSICS text height
        draw_ps5_button(surface, physics_x + physics_txt.get_width() + 5, y, 'r1', physics_txt.get_height())

    def draw(self, surface, keybindings, playground=None):
        """Draw UI panels with top row layout"""
        self.draw_top_row(surface, playground)
        self.draw_left_panel(surface, keybindings)
        self.draw_right_panel(surface, keybindings)

def draw_level_selector(surface, playground, keybindings):
    """Draw current level name at top center (simplified)"""
    font_header = pygame.font.SysFont(None, 22, bold=True)
    
    # Just show current level name
    level_name = playground.get_name()
    center_x = SCREEN_WIDTH // 2
    
    # Draw level name centered
    name_surf = font_header.render(level_name, True, (100, 200, 255))
    name_rect = name_surf.get_rect(center=(center_x, 25))
    surface.blit(name_surf, name_rect)

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


def draw_pause_screen(surface):
    """Draw the pause/help screen overlay."""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Fonts
    font_title = pygame.font.SysFont(None, 48, bold=True)
    font_header = pygame.font.SysFont(None, 28, bold=True)
    font_text = pygame.font.SysFont(None, 20)
    
    # Title
    title = font_title.render("PAUSE / HELP", True, (255, 255, 100))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
    surface.blit(title, title_rect)
    
    y = 80
    
    # === CONTROLS SECTION ===
    controls_header = font_header.render("CONTROLS", True, (100, 200, 255))
    surface.blit(controls_header, (50, y))
    y += 30
    
    controls = [
        ("Left Stick / D-Pad", "Move character left and right"),
        ("X Button", "Jump - hold longer to jump higher (variable jump characters)"),
        ("Square Button", "Run - hold to move faster"),
        ("L2 (Hold) + D-Pad", "Select Character - release to confirm"),
        ("R2 (Hold) + D-Pad", "Select Level - release to confirm"),
        ("L1", "Reset all physics sliders to character defaults"),
        ("R1 (Hold) + D-Pad", "Adjust physics - Up/Down to select, Left/Right to change"),
        ("Options", "Toggle this pause/help screen"),
    ]
    
    for button, desc in controls:
        btn_surf = font_text.render(button, True, (255, 220, 100))
        desc_surf = font_text.render(desc, True, (200, 200, 200))
        surface.blit(btn_surf, (60, y))
        surface.blit(desc_surf, (250, y))
        y += 22
    
    y += 15
    
    # === PHYSICS SECTION ===
    physics_header = font_header.render("PHYSICS SETTINGS", True, (100, 255, 150))
    surface.blit(physics_header, (50, y))
    y += 30
    
    physics = [
        ("Gravity", "How fast you fall down. Higher = heavier, falls faster."),
        ("Fall Grav", "Extra gravity when falling (not jumping). Makes falls snappier."),
        ("Speed", "How fast you run left and right. Higher = faster movement."),
        ("Accel", "How quickly you speed up. Low = slippery ice, High = instant control."),
        ("Jump", "How high you jump. Higher = can reach taller platforms."),
    ]
    
    for param, desc in physics:
        param_surf = font_text.render(param, True, (150, 255, 150))
        desc_surf = font_text.render(desc, True, (200, 200, 200))
        surface.blit(param_surf, (60, y))
        surface.blit(desc_surf, (150, y))
        y += 22
    
    y += 20
    
    # Footer
    footer = font_text.render("Press Start/Options to resume", True, (180, 180, 180))
    footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
    surface.blit(footer, footer_rect)
