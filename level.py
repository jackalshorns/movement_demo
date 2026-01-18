import pygame
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(100, 100, 100)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 50, 50))  # Red for danger
        self.rect = self.image.get_rect(topleft=(x, y))

class Label(pygame.sprite.Sprite):
    """Text label for level sections"""
    def __init__(self, x, y, text, color=(200, 200, 255)):
        super().__init__()
        self.font = pygame.font.SysFont(None, 28)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Level:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.labels = pygame.sprite.Group()
        self.setup_comparison_playground()

    def setup_comparison_playground(self):
        """
        Design a level with distinct sections that highlight each character's strengths:
        1. Momentum Section - Wide gaps requiring running jumps (Mario excels)
        2. Wall Jump Section - Vertical shaft (Super Meat Boy only)
        3. Precision Section - Tight platforms (Zelda/SMB excel)
        4. Dash Section - Long gap (Zelda only)
        5. Speed Section - Platforms requiring speed-dependent jump height (Mario only)
        """
        
        # Ground
        ground_y = SCREEN_HEIGHT - 60
        self.platforms.add(Platform(0, ground_y, 400, 60))
        
        # === SECTION 1: MOMENTUM SECTION (Mario excels) ===
        self.labels.add(Label(50, ground_y - 200, "MOMENTUM ZONE", (255, 100, 100)))
        
        # Starting platform
        self.platforms.add(Platform(100, ground_y - 100, 150, 20))
        
        # Wide gap - need running jump
        self.platforms.add(Platform(400, ground_y - 100, 150, 20))
        
        # Even wider gap
        self.platforms.add(Platform(700, ground_y - 150, 150, 20))
        
        # === SECTION 2: WALL JUMP SECTION (Super Meat Boy only) ===
        self.labels.add(Label(900, ground_y - 400, "WALL JUMP", (150, 100, 100)))
        
        # Vertical shaft with alternating walls
        shaft_x = 950
        self.platforms.add(Platform(shaft_x, ground_y, 40, 60))  # Bottom left wall
        self.platforms.add(Platform(shaft_x + 150, ground_y - 100, 40, 160))  # Right wall
        self.platforms.add(Platform(shaft_x, ground_y - 200, 40, 100))  # Left wall
        self.platforms.add(Platform(shaft_x + 150, ground_y - 300, 40, 100))  # Right wall
        self.platforms.add(Platform(shaft_x, ground_y - 400, 40, 100))  # Left wall
        
        # Top platform (goal)
        self.platforms.add(Platform(shaft_x + 50, ground_y - 450, 100, 20, (100, 255, 100)))
        
        # === SECTION 3: PRECISION SECTION (Zelda/SMB excel) ===
        # Continue ground
        self.platforms.add(Platform(400, ground_y, 880, 60))
        
        self.labels.add(Label(450, ground_y - 150, "PRECISION", (100, 255, 100)))
        
        # Tight platforms requiring instant stops
        prec_x = 500
        self.platforms.add(Platform(prec_x, ground_y - 80, 40, 20))
        self.platforms.add(Platform(prec_x + 80, ground_y - 120, 40, 20))
        self.platforms.add(Platform(prec_x + 160, ground_y - 80, 40, 20))
        self.platforms.add(Platform(prec_x + 240, ground_y - 120, 40, 20))
        self.platforms.add(Platform(prec_x + 320, ground_y - 80, 40, 20))
        
        # === SECTION 4: DASH SECTION (Zelda only) ===
        # Ground continues
        self.platforms.add(Platform(1100, ground_y, 180, 60))
        
        self.labels.add(Label(450, ground_y - 300, "DASH ZONE", (100, 255, 100)))
        
        # Very long gap - requires dash jump
        self.platforms.add(Platform(450, ground_y - 250, 100, 20))
        self.platforms.add(Platform(850, ground_y - 250, 100, 20, (100, 255, 100)))  # Goal platform
        
        # === SECTION 5: SPEED-DEPENDENT JUMP (Mario only) ===
        # Add a section at the far right
        self.platforms.add(Platform(1100, ground_y - 150, 100, 20))
        
        self.labels.add(Label(1100, ground_y - 300, "SPEED JUMP", (255, 100, 100)))
        
        # High platform that requires speed-boosted jump
        self.platforms.add(Platform(1100, ground_y - 280, 100, 20, (255, 100, 100)))
        
        # Some hazards
        self.hazards.add(Hazard(300, ground_y - 20, 80, 20))
        self.hazards.add(Hazard(600, ground_y - 20, 80, 20))

    def reset(self):
        self.platforms.empty()
        self.hazards.empty()
        self.labels.empty()
        self.setup_comparison_playground()
    
    def draw(self, surface):
        self.platforms.draw(surface)
        self.hazards.draw(surface)
        self.labels.draw(surface)
