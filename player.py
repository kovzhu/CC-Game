import pygame
import math



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, level=None):
        super().__init__()
        self.health = 3
        self.level = level
        # Initialize joystick if available
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        # Load player images
        # We now use pre-processed PNGs with transparency
        self.images = [
            pygame.image.load("assets/hero1.png").convert_alpha(),
            pygame.image.load("assets/hero2.png").convert_alpha()
        ]
        self.attack_image = pygame.image.load("assets/hero3.png").convert_alpha()
            
        self.images = [pygame.transform.scale(img, (70, 90)) for img in self.images]
        self.attack_image = pygame.transform.scale(self.attack_image, (70, 90))
        self.current_image = 0
        self.image = self.images[self.current_image]
        
        self.rect = self.image.get_rect()
        self.last_shot = 0
        self.shoot_delay = 250
        
        # Melee Attack
        self.last_melee_time = 0
        self.melee_cooldown = 500
        self.is_attacking = False
        self.attack_start_time = 0
        self.attack_duration = 200 # ms
        self.sword_beams = pygame.sprite.Group() # Group for projectile attacks
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.last_change = pygame.time.get_ticks()
        self.change_delay = 200  # Animation frame delay in milliseconds
        self.last_change_time = 0
        self.last_sound_time = 0
        self.sound_cooldown = 200
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 500
        self.last_shot_time = 0
        self.ammo = 30  # Start with some ammo for testing
        self.has_ammo_box = True  # Flag to track if ammo box exists
        self.facing_left = False
        
        # Defense system
        self.is_defending = False
        self.shield_image = pygame.image.load("assets/shield.png")
        self.shield_image = pygame.transform.scale(self.shield_image, (100, 100))
        self.defense_reduction = 0.5  # Reduce damage by 50% when defending
        self.shield_hits = 0  # Track boss attacks blocked
        self.max_shield_hits = 3  # Shield breaks after 3 boss hits
        
        # Bomb system
        self.bombs = 3  # Start with 3 bombs
        self.last_bomb_time = 0
        self.bomb_cooldown = 1000  # 1 second between bombs
        
        # Level system
        self.player_level = 1
        self.damage = 1  # Base damage

        # Ultimate Ability
        self.ultimate_cooldown = 30000  # 30 seconds
        self.last_ultimate_time = -30000  # Ready at start
        self.ultimate_request = False


    def update(self):
        keys = pygame.key.get_pressed()
        moving = False
        now = pygame.time.get_ticks()

        # Handle joystick movement if available
        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            
            # Horizontal movement
            if abs(axis_x) > 0.1:
                self.velocity_x = 5 * axis_x
                moving = True
                if axis_x < 0 and self.facing_left == False:
                    self.facing_left = True
                elif axis_x > 0 and self.facing_left == True:
                    self.facing_left = False
                if now - self.last_sound_time > self.sound_cooldown:
                    pygame.mixer.Sound("sounds/swoosh.wav").play()
                    self.last_sound_time = now
                if now - self.last_change_time > self.change_delay:
                    self.current_image = (self.current_image + 1) % len(self.images)
                    self.image = pygame.transform.flip(
                        self.images[self.current_image], True, False
                    ) if self.facing_left else self.images[self.current_image]
                    self.last_change_time = now
            
            # Vertical movement (jumping)
            if axis_y < -0.5 and not self.is_jumping and self.velocity_y == 0:
                self.velocity_y = -20
                self.is_jumping = True
                moving = True
                pygame.mixer.Sound("sounds/wing.wav").play()
            # Allow finer control while in air
            elif self.is_jumping and abs(axis_y) > 0.1:
                self.velocity_y += -1 * axis_y

        # Handle keyboard movement (fallback)
        if keys[pygame.K_LEFT]:
            self.velocity_x = -5
            moving = True
            if self.facing_left == False:
                self.facing_left = True
            if now - self.last_sound_time > self.sound_cooldown:
                pygame.mixer.Sound("sounds/swoosh.wav").play()
                self.last_sound_time = now
            if now - self.last_change_time > self.change_delay:
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = pygame.transform.flip(
                    self.images[self.current_image], True, False
                )
                self.last_change_time = now
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = 5
            moving = True
            if self.facing_left == True:
                self.facing_left = False
            if now - self.last_sound_time > self.sound_cooldown:
                pygame.mixer.Sound("sounds/swoosh.wav").play()
                self.last_sound_time = now
            if now - self.last_change_time > self.change_delay:
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.last_change_time = now
        else:
            self.velocity_x = 0

        # Handle jumping
        if keys[pygame.K_UP] and not self.is_jumping:
            self.velocity_y = -20
            self.is_jumping = True
            moving = True
            pygame.mixer.Sound("sounds/wing.wav").play()
        
        # Handle defense
        defense_input = (keys[pygame.K_DOWN] or 
                        (self.joystick and self.joystick.get_button(1)))
        
        # Reset shield hits when starting to defend
        if defense_input and not self.is_defending:
            self.shield_hits = 0
            
        self.is_defending = defense_input

        # Handle shooting only if player has ammo
        shoot_input = (keys[pygame.K_SPACE] or 
                      (self.joystick and self.joystick.get_button(0)))
        if shoot_input and self.ammo > 0:
            # Cycle through player images
            if self.current_image < len(self.images) - 1:
                self.current_image += 1
            else:
                self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            # Play sound with cooldown
            if now - self.last_sound_time > self.sound_cooldown:
                pygame.mixer.Sound("sounds/hit.wav").play()
                self.last_sound_time = now
        
        # Handle bomb placement (F key or gamepad button 2)
        bomb_input = (keys[pygame.K_f] or 
                     (self.joystick and self.joystick.get_button(2)))
        if bomb_input and self.bombs > 0:
            if now - self.last_bomb_time > self.bomb_cooldown:
                # Return bomb data to be placed in main game loop
                self.place_bomb_request = True
                self.last_bomb_time = now
                self.bombs -= 1
                pygame.mixer.Sound("sounds/point.wav").play()  # Bomb place sound
                pygame.mixer.Sound("sounds/point.wav").play()  # Bomb place sound
        else:
            self.place_bomb_request = False

        # Handle Ultimate (R key)
        if keys[pygame.K_r]:
             if now - self.last_ultimate_time > self.ultimate_cooldown:
                 self.ultimate_request = True
                 self.last_ultimate_time = now # Set cooldown immediately to prevent spam
        else:
            self.ultimate_request = False

        # Apply gravity
        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10

        # Update position with collision detection
        if self.level:
            self.level.check_collision(self, self.velocity_x, self.velocity_y)
        else:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y

        # Check if fell off screen
        if self.rect.top > pygame.display.get_surface().get_height():
            self.health = 0  # Die if fall off screen

        # Handle image cycling and procedural animation
        if moving:
            # Animation frame update
            if now - self.last_change > self.change_delay:
                self.current_image = (self.current_image + 1) % len(self.images)
                self.last_change = now
            
            # Base image
            base_img = self.images[self.current_image]
            
            # Leaning effect (Rotate forward)
            # Base sprites face Right. We rotate CW (-15) to lean Right (Forward).
            # When flipped for Left movement, the lean also flips to Left (Forward).
            lean_angle = -15 
            
            # Bobbing effect (vertical offset)
            # bob_offset = int(math.sin(now * 0.02) * 2) 
            # Note: Changing rect.y interferes with physics, so we skip positional bobbing 
            # and rely on the sprite animation's natural bob if any, or rotation.
            
            rotated_img = pygame.transform.rotate(base_img, lean_angle)
            
            if self.facing_left:
               self.image = pygame.transform.flip(rotated_img, True, False)
            else:
               self.image = rotated_img
               
            # Adjust rect to keep centered (optional, but good for stability)
            # self.rect = self.image.get_rect(center=self.rect.center)
            
        else:
            self.image = self.images[0]  # Default to standing frame


        # Handle Melee Attack (J key or Spacebar)
        melee_input = (keys[pygame.K_j] or keys[pygame.K_SPACE])
        if melee_input and now - self.last_melee_time > self.melee_cooldown:
            self.is_attacking = True
            self.attack_start_time = now
            self.last_melee_time = now
            pygame.mixer.Sound("sounds/swoosh.wav").play()
            
            # Spawn Sword Beam
            # Start position
            beam_start_x = self.rect.centerx
            beam_start_y = self.rect.centery
            
            # Target position (Mouse + Scroll)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_x = mouse_x + (self.scroll_x if hasattr(self, 'scroll_x') else 0)
            target_y = mouse_y
            
            beam = SwordBeam(beam_start_x, beam_start_y, target_x, target_y)
            self.sword_beams.add(beam)
            
            # Optional: Lunge forward only if not defending
            if not self.is_defending:
                lunge_speed = 10 if not self.facing_left else -10
                self.rect.x += lunge_speed
            
        if self.is_attacking:
            # Overwrite image with attack animation
            # Calculate progress (0.0 to 1.0)
            progress = (now - self.attack_start_time) / self.attack_duration
            
            # Rotation Logic (Degrees)
            # 0.0 - 0.25 (First 50ms): Wind up (Pull back)
            # 0.25 - 0.75 (Next 100ms): Slash! (Swing forward aggressively)
            # 0.75 - 1.00 (Last 50ms): Recovery (Return to center)
            
            angle = 0
            if progress < 0.25:
                # Wind up: 0 to 30 degrees (Backwards)
                # Facing Right: Back is Left (CCW, +)
                p = progress / 0.25
                angle = 30 * p
            elif progress < 0.75:
                # Slash: 30 to -60 degrees (Forward)
                # Facing Right: Forward is Right (CW, -)
                p = (progress - 0.25) / 0.50
                angle = 30 - (90 * p) # Goes from 30 down to -60
            else:
                # Recovery: -60 back to 0
                p = (progress - 0.75) / 0.25
                angle = -60 * (1 - p)
                
            # If facing left, invert the angle (Back is Right -> CW -> -)
            if self.facing_left:
                angle = -angle
                
            # Apply rotation
            # Use the dedicated attack sprite
            base_img = self.attack_image 
            
            rotated_img = pygame.transform.rotate(base_img, angle)
            
            if self.facing_left:
                self.image = pygame.transform.flip(rotated_img, True, False)
            else:
                self.image = rotated_img
                
            # Important: Recenter the rect so rotation doesn't jitter position
            # Use midbottom (feet) as pivot to prevent backward sliding/floating
            old_midbottom = self.rect.midbottom
            self.rect = self.image.get_rect()
            self.rect.midbottom = old_midbottom
            
            # Check attack duration to end state
            if now - self.attack_start_time > self.attack_duration:
                self.is_attacking = False

    def get_melee_hitbox(self):
        """Returns a rect representing the sword swing area"""
        if self.facing_left:
            return pygame.Rect(self.rect.left - 60, self.rect.centery - 40, 60, 80)
        else:
            return pygame.Rect(self.rect.right, self.rect.centery - 40, 60, 80)

    def draw_attack(self, surface):
        """Draws the slash effect"""
        if self.is_attacking:
            hitbox = self.get_melee_hitbox()
            
            # Create a transparent surface for the effect
            effect_surf = pygame.Surface((hitbox.width + 40, hitbox.height + 40), pygame.SRCALPHA)
            
            # Colors
            glow_color = (0, 255, 255, 100)  # Cyan glow, transparent
            core_color = (255, 255, 255, 200) # White core
            
            # Calculate arc points relative to effect_surf
            w, h = effect_surf.get_size()
            
            if self.facing_left:
                # Crescent shape points for Left slash
                points = [
                    (w, 0),         # Top right
                    (0, h//2),      # Middle left (tip)
                    (w, h),         # Bottom right
                    (w - 20, h//2)  # Inner curve point
                ]
            else:
                # Crescent shape points for Right slash
                points = [
                    (0, 0),         # Top left
                    (w, h//2),      # Middle right (tip)
                    (0, h),         # Bottom left
                    (20, h//2)      # Inner curve point
                ]
                
            # Draw Glow (larger)
            pygame.draw.polygon(effect_surf, glow_color, points)
            
            # Draw Core (slightly smaller/thinner lines for style or just same shape brighter)
            # For a sharp blade look, we can draw a line loop
            pygame.draw.lines(effect_surf, core_color, False, points[:3], 3)
            
            # Adjust blit position to center over hitbox
            blit_pos = (hitbox.x - 20, hitbox.y - 20)
            surface.blit(effect_surf, blit_pos)

    def hit(self):
        """Called when player collides with enemy"""
        if self.is_defending:
            # Reduce damage when defending
            if hasattr(self, 'defense_reduction'):
                # Only take partial damage
                damage = 1 * (1 - self.defense_reduction)
                if damage < 1:
                    # Don't take damage if reduction is high enough
                    pygame.mixer.Sound("sounds/point.wav").play()  # Play shield sound
                    return
        
        self.health -= 1
        if self.health <= 0:
            self.kill()

class SwordBeam(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.width = 60
        self.height = 80
        self.hit_enemies = set()
        
        # Calculate Angle
        dx = target_x - x
        dy = target_y - y
        angle_rad = math.atan2(dy, dx)
        angle_deg = -math.degrees(angle_rad) # Pygame rotation is CCW
        
        # Create transparent surface (Base: Pointing RIGHT)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the beam pointing RIGHT
        glow_color = (0, 255, 255, 150)
        core_color = (255, 255, 255, 255)
        w, h = self.width, self.height
        
        # Tip is at (w, h/2), Back is at (0, 0) and (0, h)
        points = [(0, 0), (w, h//2), (0, h), (15, h//2)]
             
        pygame.draw.polygon(self.image, glow_color, points)
        pygame.draw.lines(self.image, core_color, False, points[:3], 3)
        
        # Rotate image
        self.image = pygame.transform.rotate(self.image, angle_deg)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Velocity
        speed = 20
        self.velocity_x = math.cos(angle_rad) * speed
        self.velocity_y = math.sin(angle_rad) * speed
        
        # Float position for smooth movement
        self.float_x = float(x)
        self.float_y = float(y)

    def update(self):
        self.float_x += self.velocity_x
        self.float_y += self.velocity_y
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        
        # Kill if far off screen
        # Using simple bounds relative to player might be better if we had access, 
        # but large absolute bounds are generally safe in this scrolling level.
        if self.rect.right < -1000 or self.rect.left > 10000 or self.rect.bottom < -1000 or self.rect.top > 2000:
            self.kill()

    def shoot(self, mouse_x, mouse_y, scroll_x=0):
        """Create a new bullet that travels toward the mouse position"""
        from bullet import Bullet

        bullet = Bullet(self.rect.centerx, self.rect.centery, mouse_x, mouse_y, scroll_x)
        self.bullets.add(bullet)
