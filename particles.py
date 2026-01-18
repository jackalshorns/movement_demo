"""
Particle effects system for movement-based visual feedback.
Optimized for 60 FPS performance with object pooling.
"""

import pygame
import random
import math


class Particle:
    """Lightweight particle with physics simulation."""

    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.lifetime = 0
        self.max_lifetime = 0
        self.color = (255, 255, 255)
        self.size = 2
        self.gravity = 0.2

    def spawn(self, x, y, vx, vy, lifetime, color, size, gravity=0.2):
        """Reinitialize particle for reuse."""
        self.active = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self):
        """Apply physics and decrement lifetime."""
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.active = False


class ParticleSystem:
    """Manager for pooled particle effects."""

    def __init__(self, max_particles=100):
        self.particles = [Particle() for _ in range(max_particles)]
        self.pool_index = 0
        self.run_particle_timer = 0  # Throttle running particles

    def _get_next_particle(self):
        """Get next available particle from pool (ring buffer)."""
        particle = self.particles[self.pool_index]
        self.pool_index = (self.pool_index + 1) % len(self.particles)
        return particle

    def spawn_landing_particles(self, x, y, impact_velocity, character_color):
        """
        Spawn particles for HARD landings only.
        Creates a fan-out effect based on impact velocity.
        """
        # Subtle particle count: 3-6 particles
        particle_count = min(3 + int(impact_velocity / 4), 6)

        for i in range(particle_count):
            particle = self._get_next_particle()

            # Fan-out angles
            angle = math.pi + (i - particle_count / 2) * 0.4
            speed = random.uniform(1.5, 3.5)

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(0.5, 1.5)

            # Subtle particles: smaller size, shorter lifetime
            size = random.uniform(1.5, 3)
            lifetime = random.randint(10, 15)

            # Character-specific color with slight variation
            color = self._vary_color(character_color)

            particle.spawn(x, y, vx, vy, lifetime, color, size, gravity=0.25)

    def spawn_run_particles(self, x, y, velocity_x, character_color):
        """
        Spawn subtle dust particles when running FAST only.
        Throttled to avoid overwhelming particle count.
        """
        # Throttle: Only spawn particles occasionally
        self.run_particle_timer += 1
        if self.run_particle_timer < 4:  # Every 4 frames
            return
        self.run_particle_timer = 0

        # Very subtle: 1-2 small particles
        particle_count = random.randint(1, 2)

        for _ in range(particle_count):
            particle = self._get_next_particle()

            # Small horizontal velocity opposite to movement
            vx = -velocity_x * 0.15 + random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0)

            # Very small and short-lived
            size = random.uniform(1, 2)
            lifetime = random.randint(8, 12)

            # Dust color: lighter version of character color
            color = self._lighten_color(character_color)

            particle.spawn(
                x + random.uniform(-3, 3),
                y + random.uniform(-2, 0),
                vx, vy, lifetime, color, size, gravity=0.15
            )

    def spawn_wall_slide_particles(self, x, y, wall_direction, character_color):
        """
        Spawn subtle spark particles during wall slide.
        Creates a scraping effect.
        """
        # Very subtle: 1-2 particles
        if random.random() > 0.5:  # 50% chance to spawn
            return

        particle_count = random.randint(1, 2)

        for _ in range(particle_count):
            particle = self._get_next_particle()

            # Sparks fly away from wall
            vx = wall_direction * random.uniform(1, 2.5)
            vy = random.uniform(-0.5, 1.5)

            # Small bright particles
            size = random.uniform(1, 2.5)
            lifetime = random.randint(8, 12)

            # Bright spark color
            color = self._brighten_color(character_color)

            particle.spawn(x, y + random.uniform(-5, 5), vx, vy, lifetime, color, size, gravity=0.1)

    def spawn_dash_particles(self, x, y, dash_direction, character_color):
        """
        Spawn particle burst at dash activation.
        Primary visual feedback for dashing.
        """
        # Subtle burst: 8-12 particles
        particle_count = random.randint(8, 12)

        for i in range(particle_count):
            particle = self._get_next_particle()

            # Radial burst with bias opposite to dash direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4.5)

            # Bias away from dash direction
            if dash_direction != 0:
                angle_bias = math.pi if dash_direction > 0 else 0
                angle = angle * 0.4 + angle_bias * 0.6

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            size = random.uniform(1.5, 3)
            lifetime = random.randint(12, 18)

            color = self._vary_color(character_color)

            particle.spawn(x, y, vx, vy, lifetime, color, size, gravity=0.15)

    def spawn_dash_trail(self, x, y, character_color):
        """
        Spawn trail particles during dash movement.
        Creates motion blur effect.
        """
        # Very subtle: 2-3 particles per frame
        particle_count = random.randint(2, 3)

        for _ in range(particle_count):
            particle = self._get_next_particle()

            # Minimal velocity (particles left behind)
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)

            size = random.uniform(1.5, 2.5)
            lifetime = random.randint(8, 12)

            color = self._vary_color(character_color)

            particle.spawn(
                x + random.uniform(-3, 3),
                y + random.uniform(-3, 3),
                vx, vy, lifetime, color, size, gravity=0.05
            )

    def _vary_color(self, base_color):
        """Add slight random variation to color."""
        r = max(0, min(255, base_color[0] + random.randint(-20, 20)))
        g = max(0, min(255, base_color[1] + random.randint(-20, 20)))
        b = max(0, min(255, base_color[2] + random.randint(-20, 20)))
        return (r, g, b)

    def _lighten_color(self, base_color):
        """Create lighter version of color (for dust)."""
        r = min(255, base_color[0] + 60)
        g = min(255, base_color[1] + 60)
        b = min(255, base_color[2] + 60)
        return (r, g, b)

    def _brighten_color(self, base_color):
        """Create brighter version of color (for sparks)."""
        r = min(255, int(base_color[0] * 1.3) + 40)
        g = min(255, int(base_color[1] * 1.3) + 40)
        b = min(255, int(base_color[2] * 1.3) + 40)
        return (r, g, b)

    def update(self):
        """Update all active particles."""
        for particle in self.particles:
            if particle.active:
                particle.update()

    def draw(self, surface):
        """Render all active particles with alpha fade."""
        for particle in self.particles:
            if not particle.active:
                continue

            # Calculate alpha based on lifetime (fade in final 30%)
            alpha_ratio = particle.lifetime / particle.max_lifetime
            if alpha_ratio < 0.3:
                alpha = int((alpha_ratio / 0.3) * 255)
            else:
                alpha = 255

            # Create surface for alpha blending
            particle_surface = pygame.Surface((int(particle.size * 2), int(particle.size * 2)), pygame.SRCALPHA)

            # Draw particle with alpha
            color_with_alpha = (*particle.color, alpha)
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (int(particle.size), int(particle.size)),
                int(particle.size)
            )

            # Blit to main surface
            surface.blit(
                particle_surface,
                (int(particle.x - particle.size), int(particle.y - particle.size))
            )
    def spawn_sword_arc(self, x, y, facing_right):
        """Link's Sword Arc"""
        start_angle = -math.pi/2 if facing_right else -math.pi/2
        end_angle = 0 if facing_right else -math.pi
        
        particle_count = 15
        for i in range(particle_count):
            particle = self._get_next_particle()
            progress = i / particle_count
            angle = start_angle + (end_angle - start_angle) * progress
            
            radius = 30
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            
            # Persist for a bit
            lifetime = 10
            size = 3
            color = (200, 200, 255) # White/Blue steel
            
            particle.spawn(px, py, 0, 0, lifetime, color, size, gravity=0)

    def spawn_glitch_particles(self, x, y):
        """Madeline's Glitch"""
        particle_count = 10
        for _ in range(particle_count):
            particle = self._get_next_particle()
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            
            color = (random.randint(0, 255), random.randint(0, 100), random.randint(100, 255))
            size = random.uniform(2, 5)
            lifetime = 8
            particle.spawn(x, y, vx, vy, lifetime, color, size, gravity=0)

    def spawn_coin_particles(self, x, y):
        """Mario's Coin"""
        # A single coin rising or sparkles
        particle_count = 8
        for _ in range(particle_count):
            particle = self._get_next_particle()
            vx = random.uniform(-2, 2)
            vy = random.uniform(-5, -2)
            color = (255, 215, 0) # Gold
            size = 3
            lifetime = 20
            particle.spawn(x, y, vx, vy, lifetime, color, size, gravity=0.3)

    def spawn_shuriken(self, x, y, direction):
        """Ninja's Shuriken (Simulated by particles moving together)"""
        # Actually, let's just throw a fast stream of grey particles
        particle_count = 5
        for i in range(particle_count):
            particle = self._get_next_particle()
            vx = direction * 10
            vy = 0
            size = 4 if i == 0 else 2
            color = (100, 100, 100)
            lifetime = 30
            particle.spawn(x - i*5*direction, y, vx, vy, lifetime, color, size, gravity=0)
