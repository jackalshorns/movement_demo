import pygame
import sys
from settings import *
from playgrounds import PlaygroundManager
from player import Player
from particles import ParticleSystem

from ui import ControlPanel, draw_level_selector, draw_selection_overlay
from keybindings import KeyBindings
from controller import ControllerInput

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Movement Comparison")
    clock = pygame.time.Clock()

    # Init Subsystems
    playground = PlaygroundManager()
    particle_system = ParticleSystem(max_particles=100)

    # Character List for Selection
    from character_profiles import CHARACTERS, MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA
    char_list = [MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA]

    player = Player((200, SCREEN_HEIGHT - 200), playground, MARIO)
    player.particle_system = particle_system
    
    # UI and Controls
    ui = ControlPanel(player)
    keybindings = KeyBindings()
    
    # Controller
    controller = ControllerInput()

    # Selection State
    selection_mode = None # None, "CHARACTER", "LEVEL"
    selection_index = 0
    selection_cooldown = 0

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
            player.update(controller)
            particle_system.update()

            # Check finish
            if playground.check_finish(player.rect, player.profile.color):
                player.rect.topleft = playground.start_pos
                player.velocity = pygame.math.Vector2(0, 0)
        
        # 3. Draw
        screen.fill((25, 25, 35))
        playground.draw(screen)
        particle_system.draw(screen)
        screen.blit(player.image, player.rect)
        ui.draw(screen, keybindings)
        draw_level_selector(screen, playground, keybindings)
        
        # Draw Controller Status
        if controller.connected:
            font_small = pygame.font.SysFont(None, 18)
            status_text = f"Controller: {controller.get_name()}"
            if selection_mode: status_text += f" | Selecting {selection_mode}"
            
            controller_text = font_small.render(status_text, True, (100, 255, 100))
            screen.blit(controller_text, (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 25))

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

