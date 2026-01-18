import pygame

class ControllerInput:
    """Wrapper for PS5 (or any) controller input with debugging"""
    
    def __init__(self):
        self.joystick = None
        self.connected = False
        self.debug_mode = True  # Enable debugging
        self.init_controller()
    
    def init_controller(self):
        """Try to initialize the first available controller"""
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
            print(f"Number of axes: {self.joystick.get_numaxes()}")
            print(f"Number of buttons: {self.joystick.get_numbuttons()}")
            print(f"Number of hats: {self.joystick.get_numhats()}")
        else:
            print("No controller detected. Using keyboard only.")
    
    def get_movement_input(self):
        """
        Returns (horizontal, jump, run, dash) as booleans/values
        horizontal: -1 (left), 0 (neutral), 1 (right)
        """
        if not self.connected:
            return 0, False, False, False
        
        # Left stick horizontal axis (usually axis 0)
        horizontal = self.joystick.get_axis(0)
        
        # Debug: Print axis values when they change
        if self.debug_mode and abs(horizontal) > 0.1:
            print(f"Axis 0 (horizontal): {horizontal:.2f}")
        
        # Deadzone
        if abs(horizontal) < 0.2:
            horizontal = 0
        else:
            horizontal = 1 if horizontal > 0 else -1
            
        # D-Pad Support (Buttons 11-14 or Hat)
        if horizontal == 0:  # Only check dpad if stick is neutral
            # Method 1: D-pad as buttons (Common on macOS)
            # Typically: 11=Up, 12=Down, 13=Left, 14=Right (check your logs for exact mapping)
            # Based on logs: 11, 13, 14 being pressed
            
            # Check button count to avoid errors
            num_buttons = self.joystick.get_numbuttons()
            if num_buttons >= 15:
                # Mapping might vary, checking expected indices
                if self.joystick.get_button(13): # Left?
                    horizontal = -1
                elif self.joystick.get_button(14): # Right? 
                    horizontal = 1
                    
            # Method 2: D-pad as Hat (if supported)
            if horizontal == 0 and self.joystick.get_numhats() > 0:
                hat = self.joystick.get_hat(0)
                horizontal = hat[0]  # First element is usually X axis
        
        # Try multiple button mappings for different controllers
        jump = False
        run = False
        dash = False
        
        # Check all buttons and print when pressed (for debugging)
        if self.debug_mode:
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    print(f"Button {i} pressed")
        
        # Common button mappings (try multiple)
        # PS5: X=0, Circle=1, Square=2, Triangle=3, L1=4, R1=5, L2=6, R2=7
        # Xbox: A=0, B=1, X=2, Y=3, LB=4, RB=5, LT=6, RT=7
        
        # Jump: Try buttons 0, 1, 2 (X, Circle, Square on PS5 / A, B, X on Xbox)
        jump = (self.joystick.get_button(0) or 
                self.joystick.get_button(1) or 
                self.joystick.get_button(2))
        
        # Run: Try shoulder buttons (4, 5, 6, 7)
        run = (self.joystick.get_button(4) or 
               self.joystick.get_button(5) or
               self.joystick.get_button(6) or 
               self.joystick.get_button(7))
        
        # Dash: Try button 3 (Triangle/Y)
        dash = self.joystick.get_button(3) if self.joystick.get_numbuttons() > 3 else False
        
        return horizontal, jump, run, dash
    
    def get_cycling_input(self):
        """
        Returns (prev_char, next_char, prev_level, next_level)
        Based on LB/RB (Shoulder buttons)
        """
        if not self.connected:
            return False, False, False, False
        
        # Mapping:
        # Standard SDL: LB=4, RB=5
        # Mac/PS5 often: L1=9, R1=10
        
        cycle_char = False
        cycle_level = False
        
        num_buttons = self.joystick.get_numbuttons()
        
        # Check Character Cycle (LB / L1)
        # Standard SDL is 4. 
        # Avoid 9 if it clashes with Share/Select on some devices, unless we are sure.
        # Let's stick to 4 (Left Bumper) which is standard.
        # DEBUG: Print everything if button pressed
        # if num_buttons > 0:
        #     for i in range(num_buttons):
        #         if self.joystick.get_button(i):
        #             print(f"DEBUG: Button {i} pressed")
        
        # Check Character Cycle (LB / L1 ... OR Left Trigger LT)
        # LB is Button 4. LT is Axis 4 or 5 depending on OS.
        if num_buttons > 4 and self.joystick.get_button(4): cycle_char = True
        
        # Check Axis for LT (usually Axis 4 on Mac/Linux, Axis 2 on Windows?)
        if self.joystick.get_numaxes() > 4:
            if self.joystick.get_axis(4) > 0.5: cycle_char = True
        if self.joystick.get_numaxes() > 2: # Check Axis 2 (L2 on some mappings?)
             if self.joystick.get_axis(2) > 0.5: cycle_char = True

        # Check Level Cycle (RB / R1 ... OR Right Trigger RT)
        # RB is Button 5. RT is Axis 5.
        if num_buttons > 5 and self.joystick.get_button(5): cycle_level = True
        
        if self.joystick.get_numaxes() > 5:
             if self.joystick.get_axis(5) > 0.5: cycle_level = True
        if self.joystick.get_numaxes() > 2: # Check Axis 3? (R2 on some mappings?) or Axis 5
             if (self.joystick.get_numaxes() > 3) and self.joystick.get_axis(3) > 0.5: cycle_level = True
        
        return cycle_char, cycle_level
    
    def get_randomize_input(self):
        """Returns True if Share/Create button is pressed"""
        if not self.connected:
            return False
            
        # PS5 "Create" button is typically Button 8
        # "Options" is 9 (already used for Char cycle on Mac?)
        # Let's check 8 (Share) and 6 (User observed in logs)
        
        if self.joystick.get_numbuttons() > 8 and self.joystick.get_button(8):
            return True
        if self.joystick.get_numbuttons() > 6 and self.joystick.get_button(6):
            return True
            
        return False

    
    def get_name(self):
        """Get controller name if connected"""
        if self.connected:
            return self.joystick.get_name()
        return "No Controller"
    
    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        print(f"Controller debug mode: {'ON' if self.debug_mode else 'OFF'}")

    def get_triggers(self):
        """Returns (L2_value, R2_value) normalized 0.0 to 1.0"""
        if not self.connected:
            return 0.0, 0.0
            
        # PS5/Xbox Triggers are usually Axis 4 (Left) and 5 (Right)
        # Verify mapping: often ranges from -1.0 (released) to 1.0 (pressed)
        # OR 0.0 to 1.0 depending on OS driver.
        
        # Taking a safe bet: Axis 4 and 5.
        l2 = 0.0
        r2 = 0.0
        
        if self.joystick.get_numaxes() > 4:
            l2_raw = self.joystick.get_axis(4)
            # Normalize -1..1 to 0..1
            l2 = (l2_raw + 1) / 2
            
        if self.joystick.get_numaxes() > 5:
            r2_raw = self.joystick.get_axis(5)
            # Normalize -1..1 to 0..1
            r2 = (r2_raw + 1) / 2
            
        return l2, r2

    def get_dpad_input(self):
        """Returns (x, y) for D-pad: -1, 0, 1"""
        if not self.connected:
            return 0, 0
            
        dx, dy = 0, 0
        
        # Method 1: Hat
        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            dx, dy = hat[0], hat[1]
            
        # Method 2: Buttons (Override if detected)
        # 11=Up, 12=Down, 13=Left, 14=Right
        if self.joystick.get_numbuttons() >= 15:
            if self.joystick.get_button(11): dy = 1
            if self.joystick.get_button(12): dy = -1
            if self.joystick.get_button(13): dx = -1
            if self.joystick.get_button(14): dx = 1
            
        return dx, dy
