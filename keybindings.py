import pygame
import json
import os

class KeyBindings:
    """Manages key bindings with save/load functionality"""
    
    def __init__(self):
        self.config_file = "keybindings.json"
        
        # Default key bindings
        self.bindings = {
            "move_left": [pygame.K_LEFT, pygame.K_a],
            "move_right": [pygame.K_RIGHT, pygame.K_d],
            "jump": [pygame.K_SPACE, pygame.K_w, pygame.K_UP],
            "run": [pygame.K_LSHIFT, pygame.K_RSHIFT],
            "dash": [pygame.K_x, pygame.K_c],
            # Character selection: YUIOP
            "char_1": [pygame.K_y],  # Mario
            "char_2": [pygame.K_u],  # Meat Boy
            "char_3": [pygame.K_i],  # Link
            "char_4": [pygame.K_o],  # Madeline
            "char_5": [pygame.K_p],  # Ninja (N++)
            # Level selection: 123456
            "playground_1": [pygame.K_1],
            "playground_2": [pygame.K_2],
            "playground_3": [pygame.K_3],  # SMB
            "playground_4": [pygame.K_4],  # Celeste
            "playground_5": [pygame.K_5],  # N++
            "playground_6": [pygame.K_6],  # Shaft
            "randomize": [pygame.K_7],
            "reset": [pygame.K_r],
        }
        
        self.load()
    
    def is_pressed(self, action, keys):
        """Check if any key for this action is pressed"""
        if action not in self.bindings:
            return False
        return any(keys[key] for key in self.bindings[action] if key < len(keys))
    
    def is_key_for_action(self, key, action):
        """Check if a specific key is bound to an action"""
        return key in self.bindings.get(action, [])
    
    def rebind(self, action, new_key):
        """Rebind an action to a new key (replaces first binding)"""
        if action in self.bindings:
            self.bindings[action][0] = new_key
            self.save()
    
    def save(self):
        """Save key bindings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.bindings, f, indent=2)
        except Exception as e:
            print(f"Failed to save key bindings: {e}")
    
    def load(self):
        """Load key bindings from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    self.bindings.update(loaded)
            except Exception as e:
                print(f"Failed to load key bindings: {e}")
    
    def get_key_name(self, key):
        """Get human-readable name for a key"""
        return pygame.key.name(key).upper()
    
    def get_binding_display(self, action):
        """Get display string for an action's bindings"""
        if action not in self.bindings or not self.bindings[action]:
            return "None"
        return "/".join(self.get_key_name(k) for k in self.bindings[action])
