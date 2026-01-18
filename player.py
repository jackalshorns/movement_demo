import pygame
from settings import *
from character_profiles import CharacterProfile
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, level, profile: CharacterProfile):
        super().__init__()
        self.original_pos = pos
        self.level = level
        self.profile = profile
        
        # Visuals (Stickman-ish dimensions)
        self.width = 30
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        
        # Physics State
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.is_jumping = False
        self.is_skidding = False
        self.facing_right = True
        self.on_wall = False  # For wall slide/jump
        self.wall_direction = 0  # -1 for left wall, 1 for right wall
        self.wall_stick_timer = 0
        
        # Input State
        self.run_button_held = False
        self.run_buffer_timer = 0
        self.dash_active = False
        self.dash_timer = 0
        self.dash_direction = 0
        
        # Jump state
        self.has_double_jumped = False
        self.jump_button_was_pressed = False  # Track if jump button was pressed last frame
        
        # Coyote Time & Jump Buffer
        self.air_timer = 0
        self.jump_buffer_timer = 0
        
        # Animation
        self.anim_offset = 0

    def next_character(self):
        """Cycle to the next character in the list"""
        # Get list of profiles
        from character_profiles import MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA
        profiles = [MARIO, SUPER_MEAT_BOY, ZELDA_LINK, MADELINE, N_NINJA]
        
        try:
            current_index = profiles.index(self.profile)
            next_index = (current_index + 1) % len(profiles)
            self.switch_profile(profiles[next_index])
        except ValueError:
            self.switch_profile(MARIO) # Fallback

    def get_input(self, controller=None):
        keys = pygame.key.get_pressed()
        
        # Get controller input if available
        controller_horizontal = 0
        controller_jump = False
        controller_run = False
        controller_dash = False
        
        if controller and controller.connected:
            controller_horizontal, controller_jump, controller_run, controller_dash = controller.get_movement_input()
        
        # Dash input (Zelda/Link only) - keyboard OR controller
        if self.profile.has_dash and not self.dash_active:
            if keys[pygame.K_x] or keys[pygame.K_c] or controller_dash:
                self.dash_active = True
                self.dash_timer = self.profile.dash_duration
                self.dash_direction = 1 if self.facing_right else -1
                # Spawn dash activation particles
                if hasattr(self, 'particle_system'):
                    self.particle_system.spawn_dash_particles(
                        self.rect.centerx, self.rect.centery,
                        self.dash_direction, self.profile.color
                    )

        # If dashing, override normal movement
        if self.dash_active:
            self.velocity.x = self.dash_direction * self.profile.dash_speed
            self.dash_timer -= 1
            # Spawn dash trail particles while dashing
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_dash_trail(
                    self.rect.centerx, self.rect.centery, self.profile.color
                )
            if self.dash_timer <= 0:
                self.dash_active = False
            return  # Skip normal movement input while dashing
        
        # Run button state - keyboard OR controller
        self.run_button_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or controller_run
        
        # Run buffer: maintain run speed after releasing
        if self.run_button_held:
            self.run_buffer_timer = self.profile.run_buffer_frames
        else:
            self.run_buffer_timer = max(0, self.run_buffer_timer - 1)
        
        # Determine if we're "running"
        is_running = self.run_button_held or (self.run_buffer_timer > 0)
        
        # Horizontal Movement Input - keyboard OR controller
        target_speed = 0
        keyboard_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        keyboard_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        # Determine intended direction
        move_dir = 0
        if keyboard_left or controller_horizontal < -0.2: move_dir = -1
        if keyboard_right or controller_horizontal > 0.2: move_dir = 1
        
        # Store input direction for wall jumps
        self.last_input_direction = move_dir
        
        # Handle Wall Stickiness
        # If on wall, and moving AWAY, decrement stick timer. 
        # If timer > 0, don't move horizontally yet.
        if self.on_wall and not self.on_ground:
            if move_dir != 0 and move_dir != self.wall_direction:
                # Moving away from wall
                if self.wall_stick_timer > 0:
                    self.wall_stick_timer -= 1
                    move_dir = 0 # Cancel movement
            else:
                # Moving towards or neutral, reset timer
                self.wall_stick_timer = self.profile.wall_stick_time
        
        # Apply movement
        if move_dir == -1:
            target_speed = -self.profile.run_speed if is_running else -self.profile.walk_speed
            self.facing_right = False
        elif move_dir == 1:
            target_speed = self.profile.run_speed if is_running else self.profile.walk_speed
            self.facing_right = True
        
        # Skidding: Only for momentum-based characters
        self.is_skidding = False
        if self.profile.has_momentum and self.on_ground:
            if (target_speed > 0 and self.velocity.x < -0.5) or (target_speed < 0 and self.velocity.x > 0.5):
                self.is_skidding = True
        
        # Apply acceleration/deceleration
        if target_speed != 0:
            accel = self.profile.acceleration
            if not self.on_ground:
                accel *= self.profile.air_acceleration_multiplier
            
            if self.is_skidding:
                accel = self.profile.skid_deceleration
            
            # For non-momentum characters, snap to target speed
            if not self.profile.has_momentum:
                self.velocity.x = target_speed
            else:
                if self.velocity.x < target_speed:
                    self.velocity.x = min(self.velocity.x + accel, target_speed)
                else:
                    self.velocity.x = max(self.velocity.x - accel, target_speed)
        else:
            # Apply deceleration to stop
            if self.on_ground:
                decel = self.profile.deceleration
                
                # Non-momentum characters stop instantly
                if not self.profile.has_momentum:
                    self.velocity.x = 0
                else:
                    if self.velocity.x > 0:
                        self.velocity.x = max(self.velocity.x - decel, 0)
                    elif self.velocity.x < 0:
                        self.velocity.x = min(self.velocity.x + decel, 0)
            else:
                # Air drag for characters without no_horizontal_drag
                if not self.profile.no_horizontal_drag:
                    air_drag = 0.2
                    if self.velocity.x > 0:
                        self.velocity.x = max(self.velocity.x - air_drag, 0)
                    elif self.velocity.x < 0:
                        self.velocity.x = min(self.velocity.x + air_drag, 0)

        # Jump Input - keyboard OR controller
        # Only register jump on button PRESS, not hold
        jump_button_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP] or controller_jump
        
        # Detect rising edge (button just pressed, wasn't pressed last frame)
        if jump_button_pressed and not self.jump_button_was_pressed:
            self.jump_buffer_timer = self.profile.jump_buffer
        else:
            self.jump_buffer_timer = max(0, self.jump_buffer_timer - 1)
        
        # Update button state for next frame
        self.jump_button_was_pressed = jump_button_pressed

    def apply_gravity(self):
        # Wall slide reduces fall speed
        if self.on_wall and self.profile.has_wall_slide and self.velocity.y > 0:
            self.velocity.y = min(self.velocity.y, self.profile.wall_slide_speed)
            # Spawn wall slide particles
            if hasattr(self, 'particle_system'):
                wall_x = self.rect.left if self.wall_direction == -1 else self.rect.right
                self.particle_system.spawn_wall_slide_particles(
                    wall_x, self.rect.centery, self.wall_direction, self.profile.color
                )
            return
        
        # Variable gravity
        current_gravity = self.profile.gravity
        
        # Use falling gravity if moving down
        if self.velocity.y > 0:
            current_gravity = self.profile.falling_gravity
        
        self.velocity.y += current_gravity
        if self.velocity.y > self.profile.max_fall_speed:
            self.velocity.y = self.profile.max_fall_speed

    def check_wall_contact(self):
        """Check if player is touching a wall (for wall slide/jump)"""
        was_on_wall = self.on_wall
        self.on_wall = False
        self.wall_direction = 0
        
        if not self.profile.has_wall_slide:
            return
        
        # Check left and right for wall contact
        # We expand rect slightly to check for contact
        test_rect = self.rect.inflate(2, 0)
        
        for sprite in self.level.platforms:
            if sprite.rect.colliderect(test_rect):
                # Check if we're on the side of the platform
                # (and not standing on top of it, though collision check handles that mostly)
                if self.rect.bottom > sprite.rect.top + 5: # Ensure we aren't just standing on edge
                    if self.rect.centerx < sprite.rect.left:
                        self.on_wall = True
                        self.wall_direction = 1  # Wall is to the right
                    elif self.rect.centerx > sprite.rect.right:
                        self.on_wall = True
                        self.wall_direction = -1  # Wall is to the left
        
        # Reset stick timer if we just touched a wall
        if self.on_wall and not was_on_wall:
            self.wall_stick_timer = self.profile.wall_stick_time

    def check_collisions(self, direction):
        if direction == 'horizontal':
            for sprite in self.level.platforms:
                if sprite.rect.colliderect(self.rect):
                    if self.velocity.x > 0:
                        self.rect.right = sprite.rect.left
                        self.velocity.x = 0
                    if self.velocity.x < 0:
                        self.rect.left = sprite.rect.right
                        self.velocity.x = 0

        if direction == 'vertical':
            for sprite in self.level.platforms:
                if sprite.rect.colliderect(self.rect):
                    if self.velocity.y > 0:
                        # Store landing velocity before it's zeroed
                        landing_velocity = abs(self.velocity.y)
                        self.rect.bottom = sprite.rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                        self.air_timer = 0
                        self.has_double_jumped = False  # Reset double jump on landing
                        # Spawn particles only for hard landings
                        if hasattr(self, 'particle_system') and landing_velocity > 8:
                            self.particle_system.spawn_landing_particles(
                                self.rect.centerx, self.rect.bottom,
                                landing_velocity, self.profile.color
                            )
                    if self.velocity.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.velocity.y = 0

    def jump(self):
        # Wall jump takes priority
        if self.profile.has_wall_jump and self.on_wall and self.jump_buffer_timer > 0:
            # Check directional input relative to wall
            # wall_direction is 1 (right) or -1 (left)
            # input_direction is 1 (right) or -1 (left) or 0
            
            # Use stored input direction from controller/keyboard
            input_direction = getattr(self, 'last_input_direction', 0)
            
            # --- STYLE 1: SUPER MEAT BOY (SMB) ---
            if self.profile.wall_jump_style == "smb":
                # Must jump away from wall. Cannot jump neutral or towards.
                # Actually SMB allows jumping up if you hold running?
                # Simplified SMB: Always kicks you away with fixed force
                
                # Base jump force
                self.velocity.y = -self.profile.jump_force
                
                # Kick away from wall (strong horizontal)
                self.velocity.x = -self.wall_direction * self.profile.run_speed * 1.2
                
                # Cannot control horizontal immediately (handled in update via 'no_horizontal_drag')
                
            # --- STYLE 2: CELESTE (Parkour) ---
            elif self.profile.wall_jump_style == "celeste":
                # Neutral jump = Climb up
                # Away jump = Kick away
                # Towards jump = Re-grab
                
                self.velocity.y = -self.profile.jump_force
                
                if input_direction == -self.wall_direction: # Moving away
                    # Big horizontal boost (Escape)
                    self.velocity.x = -self.wall_direction * self.profile.run_speed * 1.0
                elif input_direction == self.wall_direction: # Moving towards
                    # Tiny boost towards wall (Re-grab)
                    self.velocity.x = self.wall_direction * self.profile.walk_speed * 0.3
                else: # Neutral
                    # Moderate boost away (Climb)
                    self.velocity.x = -self.wall_direction * self.profile.walk_speed * 0.6
            
            # --- STYLE 3: N++ (Momentum) ---
            elif self.profile.wall_jump_style == "npp":
                # Triangle jump physics
                # 45 degree angle, preserves momentum but redirects it
                
                # Force is purely additive to momentum in N++, but here we emulate it
                self.velocity.y = -self.profile.jump_force * 0.9
                
                # Kick away based on current speed (bounce)
                kick_speed = max(abs(self.velocity.x), self.profile.walk_speed)
                self.velocity.x = -self.wall_direction * kick_speed * 1.1
            
            self.jump_buffer_timer = 0
            self.on_wall = False
            return
        
        # Regular jump or double jump
        can_jump = self.on_ground or (self.air_timer < self.profile.coyote_time)
        can_double_jump = self.profile.has_double_jump and not self.on_ground and not self.has_double_jumped and not can_jump
        
        if self.jump_buffer_timer > 0 and (can_jump or can_double_jump):
            # Base jump force
            jump_strength = self.profile.jump_force
            
            # Speed-dependent jump (Mario only)
            if self.profile.jump_force_run_bonus > 0:
                speed_ratio = abs(self.velocity.x) / self.profile.run_speed
                jump_strength += self.profile.jump_force_run_bonus * speed_ratio
            
            # Dash jump bonus (Link)
            if self.dash_active:
                jump_strength *= 1.2
            
            self.velocity.y = -jump_strength
            self.jump_buffer_timer = 0
            self.on_ground = False
            self.air_timer = self.profile.coyote_time
            
            if can_double_jump:
                self.has_double_jumped = True

    def update_visuals(self):
        self.image.fill((0, 0, 0, 0))
        
        # Base color from profile
        color = self.profile.color
        
        # State-based color modifications
        if self.is_skidding:
            color = (255, 200, 0)  # Yellow when skidding
        elif self.on_wall:
            color = (200, 100, 255)  # Purple when wall sliding
        elif not self.on_ground:
            # Slightly lighter when in air
            color = tuple(min(c + 30, 255) for c in self.profile.color)
        
        center_x = self.width // 2
        
        # Character-specific silhouettes
        if self.profile.name == "Mario":
            # Mario: Iconic plumber look with mustache and overalls
            # Red cap
            pygame.draw.circle(self.image, color, (center_x, 9), 9)
            # Cap brim (wider)
            pygame.draw.rect(self.image, color, (center_x - 11, 7, 22, 4))
            # "M" emblem on cap (simple)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x, 8), 3)
            # Face/head under cap
            pygame.draw.circle(self.image, (255, 220, 177), (center_x, 18), 7)
            # Mustache (iconic!)
            pygame.draw.rect(self.image, (80, 50, 30), (center_x - 6, 18, 12, 3))
            # Blue overalls body (rotund)
            pygame.draw.ellipse(self.image, (40, 100, 220), (center_x - 9, 24, 18, 20))
            # Red shirt sleeves
            pygame.draw.circle(self.image, color, (center_x - 11, 30), 4)
            pygame.draw.circle(self.image, color, (center_x + 11, 30), 4)
            # Overall straps
            pygame.draw.line(self.image, (40, 100, 220), (center_x - 3, 25), (center_x - 3, 28), 2)
            pygame.draw.line(self.image, (40, 100, 220), (center_x + 3, 25), (center_x + 3, 28), 2)
            # Legs (blue pants)
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 6
            pygame.draw.line(self.image, (40, 100, 220), (center_x, 44), (center_x - 5 + leg_offset, 56), 4)
            pygame.draw.line(self.image, (40, 100, 220), (center_x, 44), (center_x + 5 - leg_offset, 56), 4)
            # Brown shoes
            pygame.draw.circle(self.image, (120, 70, 30), (center_x - 5 + leg_offset, 57), 3)
            pygame.draw.circle(self.image, (120, 70, 30), (center_x + 5 - leg_offset, 57), 3)
            # White gloves on arms
            arm_y = 35 if self.on_ground else 30
            pygame.draw.circle(self.image, (255, 255, 255), (center_x - 12, arm_y), 3)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x + 12, arm_y), 3)
            
        elif self.profile.name == "Super Meat Boy":
            # Meat Boy: Cube of meat with iconic features
            # Main meaty body (darker red, cube-like)
            pygame.draw.rect(self.image, color, (center_x - 10, 5, 20, 38))
            # Lighter meat highlights (giving it texture)
            pygame.draw.rect(self.image, (160, 60, 60), (center_x - 8, 7, 3, 34))
            pygame.draw.rect(self.image, (160, 60, 60), (center_x + 5, 7, 3, 34))
            # Big white eyes (iconic Meat Boy look)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x - 4, 14), 4)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x + 4, 14), 4)
            # Black pupils (looking forward)
            pygame.draw.circle(self.image, (0, 0, 0), (center_x - 3, 14), 2)
            pygame.draw.circle(self.image, (0, 0, 0), (center_x + 3, 14), 2)
            # Determined mouth/grimace
            pygame.draw.rect(self.image, (80, 20, 20), (center_x - 4, 22, 8, 2))
            # Stubby arms
            pygame.draw.rect(self.image, color, (center_x - 14, 26, 4, 8))
            pygame.draw.rect(self.image, color, (center_x + 10, 26, 4, 8))
            # Stubby legs with animation
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 5
            pygame.draw.rect(self.image, color, (center_x - 8 + leg_offset, 43, 6, 16))
            pygame.draw.rect(self.image, color, (center_x + 2 - leg_offset, 43, 6, 16))
            # Feet (slightly darker)
            pygame.draw.rect(self.image, (100, 30, 30), (center_x - 8 + leg_offset, 57, 6, 3))
            pygame.draw.rect(self.image, (100, 30, 30), (center_x + 2 - leg_offset, 57, 6, 3))
            
        elif self.profile.name == "Link":
            # Link: Iconic green tunic and hat
            # Green pointy hat (triangle)
            pygame.draw.polygon(self.image, color, [(center_x, 2), (center_x - 9, 13), (center_x + 9, 13)])
            # Hat detail (lighter green stripe)
            pygame.draw.polygon(self.image, (60, 210, 60), [(center_x, 4), (center_x - 7, 13), (center_x + 7, 13)])
            # Blonde hair peeking out
            pygame.draw.rect(self.image, (220, 190, 100), (center_x - 7, 13, 14, 3))
            # Face (peach/tan skin)
            pygame.draw.circle(self.image, (255, 220, 177), (center_x, 20), 6)
            # Eyes (simple dots)
            pygame.draw.circle(self.image, (40, 60, 120), (center_x - 2, 19), 1)
            pygame.draw.circle(self.image, (40, 60, 120), (center_x + 2, 19), 1)
            # Green tunic body (triangular/trapezoid shape)
            pygame.draw.polygon(self.image, color, [(center_x, 25), (center_x - 11, 28), (center_x - 9, 44), (center_x + 9, 44), (center_x + 11, 28)])
            # Belt (brown)
            pygame.draw.rect(self.image, (120, 70, 30), (center_x - 9, 36, 18, 3))
            # Belt buckle (gold)
            pygame.draw.rect(self.image, (220, 180, 50), (center_x - 2, 36, 4, 3))
            # White undershirt collar
            pygame.draw.rect(self.image, (255, 255, 255), (center_x - 5, 25, 10, 2))
            # Green sleeves/arms
            pygame.draw.line(self.image, color, (center_x - 10, 28), (center_x - 14, 36), 3)
            pygame.draw.line(self.image, color, (center_x + 10, 28), (center_x + 14, 36), 3)
            # White tights/legs
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 6
            pygame.draw.line(self.image, (255, 255, 255), (center_x, 44), (center_x - 4 + leg_offset, 57), 3)
            pygame.draw.line(self.image, (255, 255, 255), (center_x, 44), (center_x + 4 - leg_offset, 57), 3)
            # Brown boots
            pygame.draw.circle(self.image, (120, 70, 30), (center_x - 4 + leg_offset, 58), 3)
            pygame.draw.circle(self.image, (120, 70, 30), (center_x + 4 - leg_offset, 58), 3)
            # Hylian Shield (left side, blue and silver)
            pygame.draw.circle(self.image, (180, 180, 200), (center_x - 15, 32), 5)
            pygame.draw.circle(self.image, (60, 100, 180), (center_x - 15, 32), 3)
            
        elif self.profile.name == "Madeline":
            # Madeline: Iconic pink/red hair and blue jacket from Celeste
            # Face (peach skin)
            pygame.draw.circle(self.image, (255, 220, 177), (center_x, 12), 6)
            # Eyes (simple dots, looking determined)
            pygame.draw.circle(self.image, (60, 40, 30), (center_x - 2, 11), 1)
            pygame.draw.circle(self.image, (60, 40, 30), (center_x + 2, 11), 1)
            # Iconic flowing strawberry-pink hair
            hair_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3
            # Main hair body
            pygame.draw.circle(self.image, color, (center_x, 10), 7)
            # Hair direction based on facing
            hair_direction = 1 if self.facing_right else -1
            pygame.draw.circle(self.image, color, (center_x - 5 * hair_direction, 8), 4)
            # Flowing hair strands (animated, trail behind based on facing direction)
            pygame.draw.circle(self.image, color, (center_x + hair_direction * (7 + hair_offset), 8), 4)
            pygame.draw.circle(self.image, color, (center_x + hair_direction * (10 + hair_offset), 11), 3)
            pygame.draw.circle(self.image, color, (center_x + hair_direction * (12 + hair_offset), 14), 2)
            # Blue jacket/hoodie body
            pygame.draw.rect(self.image, (100, 160, 200), (center_x - 7, 17, 14, 20))
            # Jacket details (darker blue outline)
            pygame.draw.line(self.image, (70, 120, 160), (center_x - 7, 17), (center_x - 7, 37), 1)
            pygame.draw.line(self.image, (70, 120, 160), (center_x + 7, 17), (center_x + 7, 37), 1)
            # Zipper (white)
            pygame.draw.line(self.image, (255, 255, 255), (center_x, 18), (center_x, 36), 1)
            # Arms with blue jacket sleeves
            arm_y = 25
            pygame.draw.line(self.image, (100, 160, 200), (center_x - 7, arm_y), (center_x - 12, 35), 3)
            pygame.draw.line(self.image, (100, 160, 200), (center_x + 7, arm_y), (center_x + 12, 35), 3)
            # Hands (peach)
            pygame.draw.circle(self.image, (255, 220, 177), (center_x - 12, 35), 2)
            pygame.draw.circle(self.image, (255, 220, 177), (center_x + 12, 35), 2)
            # Dark blue pants/legs
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 7
            pygame.draw.line(self.image, (40, 50, 100), (center_x, 37), (center_x - 4 + leg_offset, 58), 3)
            pygame.draw.line(self.image, (40, 50, 100), (center_x, 37), (center_x + 4 - leg_offset, 58), 3)
            # Shoes (white/grey)
            pygame.draw.circle(self.image, (220, 220, 220), (center_x - 4 + leg_offset, 59), 2)
            pygame.draw.circle(self.image, (220, 220, 220), (center_x + 4 - leg_offset, 59), 2)
            
        elif self.profile.name == "Ninja (N++)":
            # N++ Ninja: Sleek minimalist ninja with iconic gold scarf
            # Dynamic leaning based on velocity
            lean = -self.velocity.x * 0.5

            # Head (small, sleek black circle)
            pygame.draw.circle(self.image, (20, 20, 20), (center_x + int(lean * 0.3), 8), 6)
            # White eyes (ninja eyes visible through mask)
            eye_offset = int(self.velocity.x * 0.1)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x - 2 + eye_offset, 7), 1)
            pygame.draw.circle(self.image, (255, 255, 255), (center_x + 2 + eye_offset, 7), 1)

            # Body (thin, sleek black ninja suit)
            body_top = (center_x + int(lean * 0.2), 14)
            body_bottom = (center_x, 40)
            pygame.draw.line(self.image, (40, 40, 40), body_top, body_bottom, 2)

            # Ninja suit torso (slightly wider for body)
            pygame.draw.ellipse(self.image, (40, 40, 40), (center_x - 5, 20, 10, 16))

            # Legs (long and sleek, animated)
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 8

            pygame.draw.line(self.image, (40, 40, 40), body_bottom, (center_x - 4 + leg_offset + int(lean), 60), 2)
            pygame.draw.line(self.image, (40, 40, 40), body_bottom, (center_x + 4 - leg_offset + int(lean), 60), 2)

            # Arms (long, fluid ninja arms)
            arm_back = (center_x - 12 + int(lean), 32)
            arm_forward = (center_x + 12 + int(lean), 28)
            pygame.draw.line(self.image, (40, 40, 40), (center_x, 22), arm_back, 2)
            pygame.draw.line(self.image, (40, 40, 40), (center_x, 22), arm_forward, 2)

            # Hands (small circles)
            pygame.draw.circle(self.image, (40, 40, 40), arm_back, 2)
            pygame.draw.circle(self.image, (40, 40, 40), arm_forward, 2)

            # ICONIC GOLD SCARF (signature N++ feature, flowing dynamically)
            scarf_color = (255, 200, 50)  # Gold/yellow scarf
            # Scarf trails behind based on movement or facing direction
            if abs(self.velocity.x) > 0.5:
                # When moving, scarf trails behind opposite to velocity
                scarf_end_x = center_x - int(self.velocity.x * 2.5)
                scarf_mid_x = center_x - int(self.velocity.x * 1.2)
            else:
                # When stationary, scarf hangs based on facing direction
                facing_offset = -12 if self.facing_right else 12
                scarf_end_x = center_x + facing_offset
                scarf_mid_x = center_x + facing_offset // 2
            scarf_end_y = 12 + int(abs(self.velocity.y) * 0.3)
            scarf_mid_y = 11 + int(abs(self.velocity.y) * 0.15)
            # Scarf base (attached to neck)
            pygame.draw.circle(self.image, scarf_color, (center_x, 13), 3)
            # Flowing scarf trail (multiple segments for flow effect)
            pygame.draw.line(self.image, scarf_color, (center_x, 13), (scarf_mid_x, scarf_mid_y), 3)
            pygame.draw.line(self.image, scarf_color, (scarf_mid_x, scarf_mid_y), (scarf_end_x, scarf_end_y), 2)
            # Scarf tip
            pygame.draw.circle(self.image, scarf_color, (scarf_end_x, scarf_end_y), 2)

        else:
            # Default stickman
            pygame.draw.circle(self.image, color, (center_x, 10), 8)
            pygame.draw.line(self.image, color, (center_x, 18), (center_x, 40), 2)
            leg_offset = 0
            if abs(self.velocity.x) > 0.1 and self.on_ground:
                self.anim_offset += abs(self.velocity.x) * 0.15
                leg_offset = math.sin(self.anim_offset) * 6
            pygame.draw.line(self.image, color, (center_x, 40), (center_x - 5 + leg_offset, 60), 2)
            pygame.draw.line(self.image, color, (center_x, 40), (center_x + 5 - leg_offset, 60), 2)
            pygame.draw.line(self.image, color, (center_x, 25), (center_x - 10, 35), 2)
            pygame.draw.line(self.image, color, (center_x, 25), (center_x + 10, 35), 2)

    def update(self, controller=None):
        self.get_input(controller)
        
        # Horizontal
        self.rect.x += self.velocity.x
        self.check_collisions('horizontal')
        
        # Check wall contact after horizontal movement
        self.check_wall_contact()
        
        # Gravity
        self.apply_gravity()
        
        # Vertical
        self.on_ground = False
        self.rect.y += self.velocity.y
        self.check_collisions('vertical')
        
        # Coyote Timer
        if not self.on_ground:
            self.air_timer += 1
        
        # Jump
        self.jump()
        
        # Hazard Check
        if pygame.sprite.spritecollide(self, self.level.hazards, False):
            self.reset()
            
        # Fell off world
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

        self.update_visuals()

        # Spawn running particles when moving fast
        if abs(self.velocity.x) > 5 and self.on_ground:
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_run_particles(
                    self.rect.centerx - (self.velocity.x * 2),
                    self.rect.bottom, self.velocity.x, self.profile.color
                )
    
    def reset(self):
        """Reset player to starting position"""
        self.rect.topleft = self.original_pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.dash_active = False
        self.has_double_jumped = False
    
    def switch_profile(self, new_profile: CharacterProfile):
        """Switch to a different character profile"""
        self.profile = new_profile
        # Reset state
        self.has_double_jumped = False
        self.dash_active = False
