import pygame
from settings import *
import random

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(100, 100, 100), is_finish=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_finish = is_finish

class Key(pygame.sprite.Sprite):
    """Victory key that appears at the end of levels"""
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Draw key shape (circle + rect)
        pygame.draw.circle(self.image, color, (10, 6), 6)
        pygame.draw.rect(self.image, color, (8, 10, 4, 10))
        # Teeth
        pygame.draw.rect(self.image, color, (12, 14, 4, 3))
        pygame.draw.rect(self.image, color, (12, 17, 4, 3))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color

class PlaygroundManager:
    """Manages 4 different playground levels for testing"""
    
    def __init__(self):
        self.current_playground = 0
        self.platforms = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.keys = pygame.sprite.Group() # Replaces shadows
        self.start_pos = (200, SCREEN_HEIGHT - 200)
        self.finish_platform = None
        self.victory_zone = None
        
        # Track collected keys per level: {level_index: [color1, color2]}
        self.collected_keys = {} 
        
        self.load_playground(0)
    
    def load_playground(self, index, randomize=False):
        """Load a specific playground"""
        self.current_playground = index
        self.platforms.empty()
        self.hazards.empty()
        self.keys.empty()
        self.victory_zone = None
        
        if index == 0:
            self.create_flat_playground()
        elif index == 1:
            self.create_two_platform_playground()
        elif index == 2:
            self.create_smb_level(randomize)
        elif index == 3:
            self.create_celeste_level(randomize)
        elif index == 4:
            self.create_npp_level(randomize)
        elif index == 5:
            self.create_dedicated_shaft_level(randomize)
            
        # Re-add collected keys
        if self.finish_platform and index in self.collected_keys:
            center_x = self.finish_platform.rect.centerx
            center_y = self.finish_platform.rect.top - 15
            for i, color in enumerate(self.collected_keys[index]):
                offset_x = (i * 15) - ((len(self.collected_keys[index]) - 1) * 7.5)
                self.keys.add(Key(center_x + offset_x, center_y, color))
    
    def next_playground(self):
        """Switch to next playground"""
        self.load_playground((self.current_playground + 1) % 6)
    
    def previous_playground(self):
        """Switch to previous playground"""
        self.load_playground((self.current_playground - 1) % 6)
    
    def randomize_current(self):
        """re-load current level with randomization if supported"""
        # Supported for SMB(2), Celeste(3), N++(4), Shaft(5)
        if self.current_playground in [2, 3, 4, 5]:
            self.load_playground(self.current_playground, randomize=True)
    
    def get_name(self):
        """Get current playground name"""
        names = [
            "Level 1: Flat Run", 
            "Level 2: Wall Climb", 
            "Level 3: SMB Factory",
            "Level 4: Celeste Summit",
            "Level 5: N++ Void",
            "Level 6: The Shaft"
        ]
        if 0 <= self.current_playground < len(names):
            return names[self.current_playground]
        return "Unknown"
    
    
    def create_flat_playground(self):
        """Playground 1: Flat platform with start and finish"""
        ground_y = SCREEN_HEIGHT - 80
        
        self.platforms.add(Platform(0, ground_y, 300, 80, (60, 100, 60)))
        self.start_pos = (100, ground_y - 10)
        
        self.platforms.add(Platform(300, ground_y, 700, 80, (80, 80, 80)))
        
        finish = Platform(1000, ground_y, 280, 80, (180, 150, 50), is_finish=True)
        self.platforms.add(finish)
        self.finish_platform = finish
    
    def create_two_platform_playground(self):
        """Playground 2: Two platforms with wall jump section"""
        ground_y = SCREEN_HEIGHT - 80
        
        self.platforms.add(Platform(50, ground_y, 250, 80, (60, 100, 60)))
        self.start_pos = (100, ground_y - 10)
        
        self.platforms.add(Platform(500, ground_y, 300, 80, (80, 80, 80)))
        
        # Wall jump section
        shaft_x = 900
        self.platforms.add(Platform(shaft_x, ground_y, 40, 80, (100, 80, 120)))
        self.platforms.add(Platform(shaft_x + 150, ground_y - 100, 40, 180, (100, 80, 120)))
        self.platforms.add(Platform(shaft_x, ground_y - 200, 40, 100, (100, 80, 120)))
        self.platforms.add(Platform(shaft_x + 150, ground_y - 300, 40, 100, (100, 80, 120)))
        
        finish = Platform(shaft_x + 40, ground_y - 350, 110, 20, (180, 150, 50), is_finish=True)
        self.platforms.add(finish)
        self.finish_platform = finish

    def create_smb_level(self, randomize=False):
        """Playground 3: Super Meat Boy Style (Hazards + Tight Walls)"""
        ground_y = SCREEN_HEIGHT - 50
        
        # Start
        self.platforms.add(Platform(50, ground_y, 150, 50, (100, 50, 50)))
        self.start_pos = (80, ground_y - 10)
        
        # Hazard Pit
        self.platforms.add(Platform(200, ground_y + 20, 800, 30, (200, 0, 0)))
        
        # Vertical Shafts
        shaft_x = 300
        
        # Randomize parameters
        num_shafts = 3
        if randomize:
            num_shafts = random.randint(3, 5)
            shaft_gap = random.randint(150, 250)
        else:
            shaft_gap = 200

        for i in range(num_shafts):
            height = 150
            if randomize:
                height = random.randint(120, 180)
                y_base = ground_y - (i * random.randint(150, 200)) - 100
                width_gap = random.randint(90, 140)
            else:
                y_base = ground_y - (i * 180) - 100
                width_gap = 130
            
            # Left Wall
            self.platforms.add(Platform(shaft_x, y_base, 30, height, (80, 50, 50)))
            # Right Wall
            self.platforms.add(Platform(shaft_x + width_gap, y_base, 30, height, (80, 50, 50)))
            
            # Platform between shafts
            if i < num_shafts - 1:
                mid_plat_w = 70
                mid_plat_x = shaft_x + 30
                mid_plat_y = y_base - 30
                self.platforms.add(Platform(mid_plat_x, mid_plat_y, mid_plat_w, 20, (100, 50, 50)))
                
            shaft_x += shaft_gap
            
        # Finish
        finish_x = shaft_x
        finish_y = ground_y - (num_shafts * 150) - 50
        finish = Platform(finish_x, finish_y, 100, 30, (200, 200, 50), is_finish=True)
        self.platforms.add(finish)
        self.finish_platform = finish

    def create_celeste_level(self, randomize=False):
        """Playground 4: Celeste Style (Parkour Climb)"""
        ground_y = SCREEN_HEIGHT - 50
        
        # Start
        self.platforms.add(Platform(50, ground_y, 200, 50, (50, 100, 150)))
        self.start_pos = (100, ground_y - 10)
        
        if not randomize:
            # Fixed Layout
            self.platforms.add(Platform(300, ground_y - 100, 40, 200, (60, 120, 180)))
            self.platforms.add(Platform(450, ground_y - 250, 40, 150, (60, 120, 180)))
            self.platforms.add(Platform(600, ground_y - 350, 40, 300, (80, 140, 200)))
            self.platforms.add(Platform(750, ground_y - 100, 40, 400, (80, 140, 200)))
            finish = Platform(750, ground_y - 550, 100, 20, (200, 200, 50), is_finish=True)
            self.platforms.add(finish)
            self.finish_platform = finish
        else:
            # Random Layout
            x = 300
            y = ground_y - 100
            for i in range(5):
                # Random block type: Wall or Floating
                if random.random() > 0.5:
                    # Wall
                    h = random.randint(150, 300)
                    self.platforms.add(Platform(x, y, 40, h, (60, 120, 180)))
                    x += random.randint(100, 150)
                    y -= random.randint(50, 100)
                else:
                    # Floating
                    w = random.randint(40, 80)
                    h = random.randint(20, 40)
                    self.platforms.add(Platform(x, y, w, h, (80, 140, 200)))
                    x += random.randint(80, 140)
                    y -= random.randint(40, 120)
            
            finish = Platform(x, y - 50, 100, 20, (200, 200, 50), is_finish=True)
            self.platforms.add(finish)
            self.finish_platform = finish

    def create_npp_level(self, randomize=False):
        """Playground 5: N++ Style (Momentum & Flow)"""
        ground_y = SCREEN_HEIGHT - 50
        
        # Start
        self.platforms.add(Platform(50, ground_y, 100, 20, (150, 150, 150)))
        self.start_pos = (70, ground_y - 10)
        
        if not randomize:
            # Fixed
            for i in range(5):
                self.platforms.add(Platform(200 + i*60, ground_y + i*10, 60, 20, (100, 100, 100)))
            self.platforms.add(Platform(600, ground_y - 200, 20, 400, (180, 180, 180)))
            self.platforms.add(Platform(400, ground_y - 300, 100, 20, (150, 150, 150)))
            self.platforms.add(Platform(200, ground_y - 450, 100, 20, (150, 150, 150)))
            finish = Platform(800, ground_y - 300, 50, 50, (200, 200, 50), is_finish=True)
        else:
            # Random
            x = 200
            y = ground_y
            # Build some momentum ramps
            for i in range(random.randint(4, 7)):
                self.platforms.add(Platform(x, y, 60, 20, (100, 100, 100)))
                x += 60
                y += 10 # Downward slope check? N++ usually down then up
            
            # Random islands
            for i in range(5):
                x = random.randint(200, 900)
                y = random.randint(100, 500)
                self.platforms.add(Platform(x, y, random.randint(50, 150), 20, (150, 150, 150)))
                
            finish = Platform(x, y - 50, 50, 50, (200, 200, 50), is_finish=True)
            
        self.platforms.add(finish)
        self.finish_platform = finish
    
    def create_dedicated_shaft_level(self, randomize=False):
        """Playground 7: Dedicated Shaft (Simple Wall Jump Practice)"""
        ground_y = SCREEN_HEIGHT - 50
        
        # Start Area (Long runway for speed)
        self.platforms.add(Platform(50, ground_y, 400, 50, (100, 100, 120)))
        self.start_pos = (80, ground_y - 10)
        
        # --- The Shaft Gauntlet ---
        shaft_x = 450
        start_y = ground_y - 50
        
        # Shaft Base Floor (White box in diagram)
        # Extending from runway into shaft
        self.platforms.add(Platform(450, ground_y, 250, 50, (100, 100, 120)))
        
        # 1. The Entry
        # Right wall start (Low enough to jump onto?)
        # User diagram shows right wall starts lower than left wall
        self.platforms.add(Platform(shaft_x + 180, start_y - 150, 40, 200, (80, 80, 100)))
        
        # 2. Wide Shaft
        width_wide = 180
        height_1 = 200
        y_1 = start_y - 200
        
        # Left wall (Raised to allow walking under)
        # Bottom needs to be ~100px above ground (Char is 60px)
        # Top at y_1 - 50 (ground - 300)
        # Height of 200 puts bottom at ground - 100.
        self.platforms.add(Platform(shaft_x, y_1 - 50, 30, height_1, (80, 80, 100)))
        
        # Right wall extension
        self.platforms.add(Platform(shaft_x + width_wide, y_1 - 200, 30, height_1 + 200, (80, 80, 100)))
        
        # 3. Medium Shaft (Normal)
        width_med = 140
        height_2 = 200
        y_2 = y_1 - 250
        offset_2 = (width_wide - width_med) // 2
        self.platforms.add(Platform(shaft_x + offset_2, y_2, 30, height_2, (90, 90, 110)))
        self.platforms.add(Platform(shaft_x + offset_2 + width_med, y_2 - 50, 30, height_2 + 50, (90, 90, 110)))
        
        # 4. Narrow Shaft (Hard)
        width_narrow = 100
        height_3 = 250
        y_3 = y_2 - 250
        offset_3 = (width_wide - width_narrow) // 2
        self.platforms.add(Platform(shaft_x + offset_3, y_3, 30, height_3, (100, 100, 120)))
        self.platforms.add(Platform(shaft_x + offset_3 + width_narrow, y_3, 30, height_3, (100, 100, 120)))
        
        # Finish Podium at top
        finish_y = y_3 - 50
        self.platforms.add(Platform(shaft_x + offset_3 - 40, finish_y, width_narrow + 110, 30, (210, 180, 50), is_finish=True))
        finish = self.platforms.sprites()[-1] 
        self.finish_platform = finish

    def check_finish(self, player_rect, player_color):
        """Check if player reached finish, add victory key if so"""
        if self.finish_platform and self.finish_platform.rect.colliderect(player_rect):
            # Add key for this character if not already completing closely (debounce?)
            # Actually Main loop handles respawn, so we just add the key here once
            
            # Add to collected keys data
            if self.current_playground not in self.collected_keys:
                self.collected_keys[self.current_playground] = []
            
            self.collected_keys[self.current_playground].append(player_color)
            
            # Add visual key immediately
            keys_count = len(self.collected_keys[self.current_playground])
            
            center_x = self.finish_platform.rect.centerx
            center_y = self.finish_platform.rect.top - 15
            
            # Calculate offset based on how many keys
            # (Stacking them or lining them up)
            # Let's line them up
            offset_x = ((keys_count - 1) * 15) - 0 # Just append to right? Or center?
            # Let's re-center all keys?
            # Simpler: just add new key at calculated pos
            
            # Actually, to center them nicely, we might want to clear and re-add all,
            # but simpler is just piling them up or adding to the side.
            # Let's just stack them with slight offset
            
            # Re-draw all keys to center them
            self.keys.empty()
            total_keys = len(self.collected_keys[self.current_playground])
            start_x = center_x - ((total_keys - 1) * 7.5)
            
            for i, color in enumerate(self.collected_keys[self.current_playground]):
                k_x = start_x + (i * 15)
                self.keys.add(Key(k_x, center_y, color))
            
            return True
        return False
    
    
    def draw(self, surface):
        self.platforms.draw(surface)
        self.hazards.draw(surface)
        self.keys.draw(surface)
