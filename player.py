import pygame
from settings import *
from character_profiles import CharacterProfile
import math
import player_renderer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, level, profile: CharacterProfile, sound_manager=None):
        super().__init__()
        self.sound_manager = sound_manager
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
                
                # Sound & Haptics
                if self.sound_manager:
                    self.sound_manager.play("dash")
                if controller and controller.connected:
                    controller.rumble(0.5, 0.8, 200)

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
                
                # Sound & Haptics (continuous)
                if self.sound_manager and pygame.time.get_ticks() % 10 == 0: # Limit frequency
                   pass # Looping sound handling is tricky without channels, maybe just one-shot for now or noise
                   # self.sound_manager.play("skid") # Too spammy if not handled carefully
                
                if controller and controller.connected and pygame.time.get_ticks() % 5 == 0:
                    controller.rumble(0.2, 0.0, 50)
        
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

    def apply_gravity(self, controller=None):
        # Wall slide reduces fall speed
        if self.on_wall and self.profile.has_wall_slide and self.velocity.y > 0:
            self.velocity.y = min(self.velocity.y, self.profile.wall_slide_speed)
            # Spawn wall slide particles
            if hasattr(self, 'particle_system'):
                wall_x = self.rect.left if self.wall_direction == -1 else self.rect.right
                self.particle_system.spawn_wall_slide_particles(
                    wall_x, self.rect.centery, self.wall_direction, self.profile.color
                )
            
            # Wall Slide Haptics
            if controller and controller.connected and pygame.time.get_ticks() % 10 == 0:
                 controller.rumble(0.1, 0.0, 50)
            
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

    def check_collisions(self, direction, controller=None):
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
                        
                        # Land Sound & Haptics
                        if landing_velocity > 2: # Ignore tiny bumps
                            if self.sound_manager:
                                self.sound_manager.play("land")
                            
                            if controller and controller.connected:
                                intensity = min(landing_velocity / 20.0, 1.0)
                                controller.rumble(intensity, intensity * 0.5, 200)
                    if self.velocity.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.velocity.y = 0

    def jump(self, controller=None):
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

            # Jump Sound & Haptics
            if self.sound_manager:
                sound_name = f"jump_{self.profile.name}"
                if sound_name in self.sound_manager.sounds:
                    self.sound_manager.play(sound_name)
                else:
                    self.sound_manager.play("jump")
            
            if controller and controller.connected:
                 controller.rumble(0.0, 0.3, 100)

    def update_visuals(self):
        """Update player sprite using the renderer module."""
        self.anim_offset = player_renderer.render_character(self)

    def perform_signature_move(self):
        if not self.sound_manager: return
        
        name = self.profile.name
        
        if name == "Link":
            self.sound_manager.play("sword")
            # Sword particles (arc)
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_sword_arc(
                    self.rect.centerx, self.rect.centery, self.facing_right
                )
                
        elif name == "Madeline":
            self.sound_manager.play("laugh")
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_glitch_particles(
                    self.rect.centerx, self.rect.centery
                )
                
        elif name == "Mario":
            self.sound_manager.play("coin")
            # Coin particles
            self.velocity.y = -5 # Small hop
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_coin_particles(
                    self.rect.centerx, self.rect.top - 10
                )

        elif name == "Super Meat Boy":
            # Squish/Blood
            self.sound_manager.play("squish")
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_landing_particles(
                    self.rect.centerx, self.rect.centery, 15, (255, 0, 0) # Red blood
                )

        elif name == "Ninja (N++)":
            self.sound_manager.play("shuriken")
            # Throw particles
            if hasattr(self, 'particle_system'):
                self.particle_system.spawn_shuriken(
                    self.rect.centerx, self.rect.centery, 1 if self.facing_right else -1
                )

    def update(self, controller=None):
        self.get_input(controller)
        
        # Check Signature Input
        if controller and controller.connected:
            if controller.get_signature_input():
                # Debounce: simplistic check, ideally we'd track prev state
                # But let's assume rapid fire or add a cooldown if needed
                # For now, let's just do it, maybe add a timer to prevent spam
                if not hasattr(self, 'signature_cooldown') or self.signature_cooldown == 0:
                    self.perform_signature_move()
                    self.signature_cooldown = 20 # Frames
        
        if hasattr(self, 'signature_cooldown') and self.signature_cooldown > 0:
            self.signature_cooldown -= 1
        
        # Horizontal
        self.rect.x += self.velocity.x
        self.check_collisions('horizontal', controller)
        
        # Check wall contact after horizontal movement
        self.check_wall_contact()
        
        # Gravity
        self.apply_gravity(controller)
        
        # Vertical
        self.on_ground = False
        self.rect.y += self.velocity.y
        self.check_collisions('vertical', controller)
        
        # Coyote Timer
        if not self.on_ground:
            self.air_timer += 1
        
        # Jump
        self.jump(controller)
        
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
