"""
Reusable sprite classes for the game.
"""

import pygame


class Platform(pygame.sprite.Sprite):
    """A solid platform that players can stand on."""
    
    def __init__(self, x, y, width, height, color=(100, 100, 100), is_finish=False, block_type=None):
        super().__init__()
        self.base_image = pygame.Surface((width, height))
        self.base_image.fill(color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_finish = is_finish
        self.block_type = block_type  # None, 'question', or 'brick'
        self.color = color
        self.width = width
        self.height = height
        
        # Animation state
        self.base_y = y
        self.jiggle_timer = 0
        self.jiggle_offset = 0
        self.is_hit = False
        self.is_broken = False
    
    def hit_from_below(self):
        """Called when player headbutts this block from below."""
        if self.block_type == 'question' and not self.is_hit:
            self.is_hit = True
            self.jiggle_timer = 15  # 15 frames of jiggle
            return 'jiggle'
        elif self.block_type == 'brick':
            self.is_broken = True
            return 'break'
        return None
    
    def update(self):
        """Update animation state."""
        if self.jiggle_timer > 0:
            self.jiggle_timer -= 1
            # Bounce up then down
            if self.jiggle_timer > 10:
                self.jiggle_offset = -6
            elif self.jiggle_timer > 5:
                self.jiggle_offset = -3
            else:
                self.jiggle_offset = 0
            self.rect.y = self.base_y + self.jiggle_offset
            
            # Dim the question block when hit (used)
            if self.jiggle_timer == 0 and self.block_type == 'question':
                self.base_image.fill((100, 80, 40))  # Darker "used" color
                self.image = self.base_image.copy()
    
    def draw(self, surface):
        """Draw platform with colorblind adjustments and high contrast outlines."""
        from accessibility import get_platform_outline_settings, accessibility
        
        # Apply colorblind color adjustment if any mode is active
        if accessibility.is_active:
            adjusted_color = accessibility.adjust_color(self.color)
            # Create adjusted image
            adjusted_image = pygame.Surface((self.width, self.height))
            adjusted_image.fill(adjusted_color)
            surface.blit(adjusted_image, self.rect)
        else:
            # Draw the platform normally
            surface.blit(self.image, self.rect)
        
        # Add outline in High Contrast mode using centralized settings
        settings = get_platform_outline_settings()
        if settings['enabled']:
            # Draw bold outer outline
            pygame.draw.rect(surface, settings['color'], self.rect, settings['thickness'])
            # Draw inner highlight line for extra contrast
            inner_rect = self.rect.inflate(-settings['thickness'] * 2, -settings['thickness'] * 2)
            if inner_rect.width > 0 and inner_rect.height > 0:
                pygame.draw.rect(surface, settings['inner_color'], inner_rect, settings['inner_thickness'])



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
