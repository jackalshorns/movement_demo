"""
Reusable sprite classes for the game.
"""

import pygame


class Platform(pygame.sprite.Sprite):
    """A solid platform that players can stand on."""
    
    def __init__(self, x, y, width, height, color=(100, 100, 100), is_finish=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_finish = is_finish


class Key(pygame.sprite.Sprite):
    """Victory key that appears at the end of levels."""
    
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


class Hazard(pygame.sprite.Sprite):
    """A hazard that damages or kills the player on contact."""
    
    def __init__(self, x, y, width, height, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Draw spikes/hazard pattern
        spike_count = max(1, width // 10)
        spike_width = width / spike_count
        for i in range(spike_count):
            pygame.draw.polygon(
                self.image, 
                color,
                [
                    (i * spike_width, height),
                    (i * spike_width + spike_width / 2, 0),
                    ((i + 1) * spike_width, height)
                ]
            )
        self.rect = self.image.get_rect(topleft=(x, y))
