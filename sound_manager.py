import pygame
import os
import sound_generator

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        
        # Init mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Could not initialize sound: {e}")
                self.enabled = False
                return

        self.load_sounds()
    
    def load_sounds(self):
        sound_dir = "sounds"
        
        # Check if sounds exist, if not generate them
        if not os.path.exists(sound_dir) or not os.listdir(sound_dir):
            print("Generating sounds...")
            sound_generator.generate_all_sounds(sound_dir)
            
        sound_files = {
            "jump": "jump.wav",
            "land": "land.wav",
            "skid": "skid.wav",
            "dash": "dash.wav",
            "wall_slide": "wall_slide.wav",
            # Signature sounds
            "sword": "sword.wav",
            "shuriken": "shuriken.wav",
            "coin": "coin.wav",
            "laugh": "laugh.wav",
            "squish": "squish.wav"
        }
        
        for name, filename in sound_files.items():
            path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.7)
                except: pass
                
        # Load all other generated files dynamically (like jump_Mario.wav)
        for filename in os.listdir(sound_dir):
            if filename.endswith(".wav") and filename not in sound_files.values():
                name = os.path.splitext(filename)[0] # e.g. "jump_Mario"
                path = os.path.join(sound_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.7)
                except: pass
    
    def play(self, sound_name):
        if not self.enabled: return
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def stop(self, sound_name):
        if not self.enabled: return
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
