"""
Blood system for Super Meat Boy.
Blood goes UNDERGROUND (into surfaces), not on top.
Only emerges from feet when moving/landing.
"""

import pygame
import random


class BloodDecalSystem:
    """Blood drips that go INTO/UNDER surfaces."""
    
    def __init__(self, max_coating=500):
        self.coating = []  # Persistent blood drips
        self.max_coating = max_coating
        self.blood_color = (150, 20, 20)  # Dark red
        self.last_trail_x = None
    
    def add_floor_drip(self, x, y, velocity_x=5):
        """Add blood drip that goes INTO the floor (below surface level)."""
        # Velocity-based spacing - faster = more spread out
        spacing = max(8, int(abs(velocity_x) * 3))
        
        if self.last_trail_x is None or abs(x - self.last_trail_x) >= spacing:
            # Small drip that goes BELOW the surface (y position is floor, drip goes down)
            width = random.randint(2, 5)
            height = random.randint(2, 6)  # Few pixels going down INTO floor
            
            self.coating.append({
                'x': x - width // 2 + random.randint(-3, 3),
                'y': y,  # Start at floor level, extends DOWN into it
                'width': width,
                'height': height,
                'type': 'floor'
            })
            self.last_trail_x = x
            self._cleanup()
    
    def add_wall_drip(self, x, y, wall_direction):
        """Add blood drip that goes INTO the wall (behind surface level)."""
        # Drip goes INTO wall, not floating in air
        width = random.randint(2, 6)
        height = random.randint(2, 5)
        
        if wall_direction == 1:  # Wall is to the right
            drip_x = x  # Drip extends INTO wall (to the right)
        else:  # Wall is to the left
            drip_x = x - width  # Drip extends INTO wall (to the left)
        
        self.coating.append({
            'x': drip_x,
            'y': y + random.randint(-5, 5),
            'width': width,
            'height': height,
            'type': 'wall'
        })
        self._cleanup()
    
    def add_landing_drips(self, x, y, count=3):
        """Add drips when landing - goes INTO floor."""
        for _ in range(count):
            offset_x = random.randint(-12, 12)
            width = random.randint(2, 4)
            height = random.randint(3, 8)
            self.coating.append({
                'x': x + offset_x,
                'y': y,  # At floor, extends down INTO it
                'width': width,
                'height': height,
                'type': 'floor'
            })
        self._cleanup()
    
    def add_trail(self, x, y, velocity_x=5):
        """Add running trail - only when moving."""
        if abs(velocity_x) > 0.5:  # Only when actually moving
            self.add_floor_drip(x, y, velocity_x)
    
    def add_splatter(self, x, y, count=3):
        """Add impact splatter (for landing)."""
        self.add_landing_drips(x, y, count)
    
    def _cleanup(self):
        """Remove oldest drips if over limit."""
        while len(self.coating) > self.max_coating:
            self.coating.pop(0)
    
    def clear(self):
        """Clear all blood (on level reset)."""
        self.coating.clear()
        self.last_trail_x = None
    
    def update(self):
        """No animation needed - drips are static."""
        pass
    
    def draw(self, surface):
        """Draw blood drips (they go INTO surfaces)."""
        for c in self.coating:
            pygame.draw.rect(surface, self.blood_color,
                           (int(c['x']), int(c['y']), c['width'], c['height']))
