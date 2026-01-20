import pygame
import sys
from settings import *
from playgrounds import PlaygroundManager
from player import Player
from particles import ParticleSystem

from ui import ControlPanel, draw_level_selector, draw_selection_overlay, draw_pause_screen
from keybindings import KeyBindings
from controller import ControllerInput
from sound_manager import SoundManager

def draw_background(screen):
    """Draws a vertical gradient background that updates with theme."""
    from ui_theme import get_colors, theme
    
    colors = get_colors()
    top_color = colors['bg_top']
    bottom_color = colors['bg_bottom']
    grid_color = colors['grid']
    
    height = screen.get_height()
    width = screen.get_width()
    
    # Cache key includes theme to regenerate when theme changes
    cache_key = theme.current
    if not hasattr(draw_background, "cache_key") or draw_background.cache_key != cache_key:
        draw_background.surface = pygame.Surface((1, height))
        for y in range(height):
            p = y / height
            r = top_color[0] * (1-p) + bottom_color[0] * p
            g = top_color[1] * (1-p) + bottom_color[1] * p
            b = top_color[2] * (1-p) + bottom_color[2] * p
            draw_background.surface.set_at((0, y), (int(r), int(g), int(b)))
        draw_background.surface = pygame.transform.scale(draw_background.surface, (width, height))
        draw_background.cache_key = cache_key
    
    screen.blit(draw_background.surface, (0, 0))
    
    # Faint grid
    for x in range(0, width, 50):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height), 1)
    for y in range(0, height, 50):
        pygame.draw.line(screen, grid_color, (0, y), (width, y), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Movement Comparison")
    clock = pygame.time.Clock()

    # Init Subsystems
    playground = PlaygroundManager()
    particle_system = ParticleSystem(max_particles=100)
    sound_manager = SoundManager()
    
    # Blood decal system (for Meat Boy)
    from blood_decals import BloodDecalSystem
    blood_decals = BloodDecalSystem(max_coating=300)

    # Character List for Selection
    from character_profiles import CHARACTERS, MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA
    char_list = [MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA]

    player = Player((200, SCREEN_HEIGHT - 200), playground, MARIO, sound_manager)
    player.particle_system = particle_system
    player.blood_decals = blood_decals
    
    # UI and Controls
    ui = ControlPanel(player, sound_manager)
    keybindings = KeyBindings()
    
    # Controller (REQUIRED)
    controller = ControllerInput()
    
    if not controller.connected:
        print("\n" + "="*50)
        print("ERROR: No controller detected!")
        print("This game requires a PS5 DualSense controller.")
        print("Please connect your controller and try again.")
        print("="*50 + "\n")
        pygame.quit()
        sys.exit(1)

    # Selection State
    selection_mode = None # None, "CHARACTER", "LEVEL"
    selection_index = 0
    selection_cooldown = 0
    lb_was_pressed = False  # Track LB state for debouncing
    triangle_was_pressed = False   # Track Triangle button for R1+Triangle reset
    x_was_pressed = False  # Track X button for R1+X customize/reset activation
    dpad_was_pressed_x = False  # Track D-pad state for RB mode
    dpad_was_pressed_y = False
    
    # Pause State
    paused = False
    start_was_pressed = False  # Track Start button for debouncing

    running = True
    while running:
        # Check Controller Status
        if controller.connected and not controller.joystick.get_init():
             controller.init_controller()
             
        keys = pygame.key.get_pressed()
        
        # 1. Event Handling (Window & Keybinds)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Check if UI is in text input mode - route keyboard there first
            if ui.text_input_active:
                if event.type == pygame.KEYDOWN:
                    ui.handle_text_input(event)
                continue  # Don't process other inputs while typing
            
            # Keyboard fallbacks for selection (if no controller)
            if event.type == pygame.KEYDOWN:
                # Existing keybinds preserved...
                if keybindings.is_key_for_action(event.key, "char_1"):
                    player.switch_profile(MARIO); ui.create_sliders()
                elif keybindings.is_key_for_action(event.key, "char_2"):
                    player.switch_profile(SUPER_MEAT_BOY); ui.create_sliders()
                elif keybindings.is_key_for_action(event.key, "char_3"):
                    player.switch_profile(ZELDA_LINK); ui.create_sliders()
                elif keybindings.is_key_for_action(event.key, "char_4"):
                    player.switch_profile(MADELINE); ui.create_sliders()
                elif keybindings.is_key_for_action(event.key, "char_5"):
                    player.switch_profile(N_NINJA); ui.create_sliders()
                
                # Playground switching
                elif keybindings.is_key_for_action(event.key, "playground_1"): playground.load_playground(0)
                elif keybindings.is_key_for_action(event.key, "playground_2"): playground.load_playground(1)
                elif keybindings.is_key_for_action(event.key, "playground_3"): playground.load_playground(2)
                elif keybindings.is_key_for_action(event.key, "playground_4"): playground.load_playground(3)
                elif keybindings.is_key_for_action(event.key, "playground_5"): playground.load_playground(4)
                elif keybindings.is_key_for_action(event.key, "playground_6"): playground.load_playground(5)
                
                elif keybindings.is_key_for_action(event.key, "randomize"):
                    playground.randomize_current()
                elif keybindings.is_key_for_action(event.key, "reset"):
                    player.reset()
            
            ui.handle_event(event)

        # 2. Logic Update
        
        # 2. Logic Update
        # Handle Selection Mode Input is handled below in the dedicated state machine block
                
        # Get inputs for the main state machine
        l2, r2 = controller.get_triggers()
        dpad_x, dpad_y = controller.get_dpad_input()
        
        # Check LB for Physics Reset (only trigger once per press)
        # DualSense: L1=9, R1=10, Start=6
        lb_pressed = False
        rb_pressed = False
        if controller.connected and controller.joystick:
            num_buttons = controller.joystick.get_numbuttons()
            # DualSense uses button 9 for L1, Xbox uses button 4 for LB
            if num_buttons > 9:
                lb_pressed = controller.joystick.get_button(9)  # DualSense L1
                rb_pressed = controller.joystick.get_button(10) # DualSense R1
            elif num_buttons > 5:
                lb_pressed = controller.joystick.get_button(4)  # Xbox LB
                rb_pressed = controller.joystick.get_button(5)  # Xbox RB
        
        # L1: VISUALS adjustment mode (hold like RB for physics)
        ui.set_visuals_mode(lb_pressed)
        lb_was_pressed = lb_pressed
        
        # RB: Physics adjustment mode
        ui.set_physics_mode(rb_pressed)
        
        # D-Pad navigation for VISUALS (when L1 held)
        if lb_pressed:
            # Up/Down to navigate options
            if dpad_y != 0 and not dpad_was_pressed_y:
                ui.navigate_visuals(-dpad_y)  # Invert: -1 (up) -> go up
            # Left/Right to adjust value
            if dpad_x != 0 and not dpad_was_pressed_x:
                ui.adjust_visuals(dpad_x)
            # Consume D-pad input so character doesn't move
            dpad_x = 0
            dpad_y = 0
        
        # D-Pad navigation for physics (when RB held)
        elif rb_pressed:
            # Up/Down to navigate sliders (inverted: up=-1 should go up in list)
            if dpad_y != 0 and not dpad_was_pressed_y:
                ui.navigate_slider(-dpad_y)  # Invert: -1 (up) -> go up in list
            # Left/Right to adjust value
            if dpad_x != 0 and not dpad_was_pressed_x:
                ui.adjust_selected(dpad_x)  # -1 = decrease, +1 = increase
            
            # X button to activate Customize or Reset (DualSense X = button 0)
            x_pressed = False
            if controller.joystick and controller.joystick.get_numbuttons() > 0:
                x_pressed = controller.joystick.get_button(0)
            if x_pressed and not x_was_pressed:
                ui.activate_selected()
            x_was_pressed = x_pressed
            
            # R1+Triangle to reset physics (DualSense Triangle = button 2)
            triangle_pressed = False
            if controller.joystick and controller.joystick.get_numbuttons() > 2:
                triangle_pressed = controller.joystick.get_button(2)
            if triangle_pressed and not triangle_was_pressed:
                player.profile.reset_physics()
                ui.create_sliders()
                print(f"Physics reset to defaults for {player.profile.name}")
            triangle_was_pressed = triangle_pressed
            
            # Consume D-pad input so character doesn't move
            dpad_x = 0
            dpad_y = 0
        
        # Track D-pad state for debouncing
        if lb_pressed or rb_pressed:
            dpad_was_pressed_x = controller.get_dpad_input()[0] != 0
            dpad_was_pressed_y = controller.get_dpad_input()[1] != 0
        else:
            dpad_was_pressed_x = False
            dpad_was_pressed_y = False
        
        # Main Selection State Machine
        
        # Detect Mode Start
        is_selecting_char = l2 > 0.5
        is_selecting_level = r2 > 0.5
        
        if is_selecting_char:
            if selection_mode != "CHARACTER":
                selection_mode = "CHARACTER"
                try: selection_index = char_list.index(player.profile)
                except: selection_index = 0
                selection_cooldown = 0
            
            # Navigate
            if selection_cooldown > 0: selection_cooldown -= 1
            
            # Check D-Pad
            change = 0
            # Horizontal or Vertical? Let's allow both for list navigation
            if abs(dpad_x) > 0: change = dpad_x
            elif abs(dpad_y) > 0: change = -dpad_y
            
            if change != 0 and selection_cooldown == 0:
                selection_index = (selection_index + change) % len(char_list)
                selection_cooldown = 12
                
        elif is_selecting_level:
            if selection_mode != "LEVEL":
                selection_mode = "LEVEL"
                selection_index = playground.current_playground
                selection_cooldown = 0
                
            # Navigate
            if selection_cooldown > 0: selection_cooldown -= 1
            
            change = 0
            if abs(dpad_x) > 0: change = dpad_x
            elif abs(dpad_y) > 0: change = -dpad_y
            
            if change != 0 and selection_cooldown == 0:
                selection_index = (selection_index + change) % 6 # Fixed count (0-5)
                selection_cooldown = 12

        else:
            # Not holding triggers
            if selection_mode == "CHARACTER":
                # Apply Character Change
                player.switch_profile(char_list[selection_index])
                ui.create_sliders()
                selection_mode = None
            elif selection_mode == "LEVEL":
                # Apply Level Change
                playground.load_playground(selection_index)
                selection_mode = None

        # Game Logic (Only update if not selecting, or maybe pause?)
        # Usually nice to pause or slow mo. Let's pause updates to prevent moving while selecting.
        if selection_mode is None:
            player.update(controller, ignore_all_input=(rb_pressed or lb_pressed))
            particle_system.update()
            blood_decals.update()  # Update animated blood waves
            playground.platforms.update()  # Update block animations (jiggle, etc.)

            # Check finish
            if playground.check_finish(player.rect, player.profile.color):
                player.rect.topleft = playground.start_pos
                player.velocity = pygame.math.Vector2(0, 0)
                blood_decals.clear()  # Clear blood on level reset
        
        # 3. Draw
        draw_background(screen)
        playground.draw(screen)
        blood_decals.draw(screen)  # Draw blood decals on surfaces
        particle_system.draw(screen)
        screen.blit(player.image, player.rect)
        ui.draw(screen, keybindings, playground)  # Pass playground for level name
        
        # Draw Controller Status (bottom-left per mockup)
        if controller.connected:
            from ui_theme import font_text, get_colors, MARGIN_LEFT
            colors = get_colors()
            status_text = f"Wireless Controller: Connected"
            
            controller_text = font_text().render(status_text, True, colors['text_dim'])
            screen.blit(controller_text, (MARGIN_LEFT, SCREEN_HEIGHT - 30))

        # Draw Selection Overlay
        if selection_mode == "CHARACTER":
            items = [{'name': c.name, 'color': c.color} for c in char_list]
            draw_selection_overlay(screen, "CHARACTER", selection_index, items)
        elif selection_mode == "LEVEL":
            # Playground names aren't easily accessible, let's map them
            level_names = ["Flat", "Wall Test", "Meat Boy", "Celeste", "N++", "Vertical Shaft"]
            items = [{'name': n} for n in level_names]
            # Handle mismatch if playground list size changed
            total_levels = 6
            if len(items) < total_levels:
                items += [{'name': f"Level {i+1}"} for i in range(len(items), total_levels)]
                
            draw_selection_overlay(screen, "LEVEL", selection_index, items)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

