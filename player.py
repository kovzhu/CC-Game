import pygame


class AmmoBox(pygame.sprite.Sprite):
    def __init__(self, x, y, level=None):
        super().__init__()
        self.image = pygame.image.load("assets/ammo.jpg")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.level = level
        self.velocity_y = 0

    def update(self):
        # Apply gravity
        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10
        
        # Update position with collision detection
        if self.level:
            self.level.check_collision(self, 0, self.velocity_y)
        else:
            self.rect.y += self.velocity_y
        
        # Remove if falls off screen
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()



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
        self.images = [pygame.image.load(f"assets/taimei{i}.png") for i in range(1, 4)]
        self.images = [pygame.transform.scale(img, (70, 90)) for img in self.images]
        self.current_image = 0
        self.image = self.images[self.current_image]
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
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
        
        # Bomb system
        self.bombs = 3  # Start with 3 bombs
        self.last_bomb_time = 0
        self.bomb_cooldown = 1000  # 1 second between bombs
        
        # Level system
        self.player_level = 1
        self.damage = 1  # Base damage


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
            # Shoot bullet if cooldown has passed
            if now - self.last_shot_time > self.shoot_cooldown:
                # Get mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Get scroll offset from level if available
                scroll_x = getattr(self, 'scroll_x', 0)
                self.shoot(mouse_x, mouse_y, scroll_x)
                self.last_shot_time = now
                self.ammo -= 1
        
        # Handle bomb placement (B key or gamepad button 2)
        bomb_input = (keys[pygame.K_b] or 
                     (self.joystick and self.joystick.get_button(2)))
        if bomb_input and self.bombs > 0:
            if now - self.last_bomb_time > self.bomb_cooldown:
                # Return bomb data to be placed in main game loop
                self.place_bomb_request = True
                self.last_bomb_time = now
                self.bombs -= 1
                pygame.mixer.Sound("sounds/point.wav").play()  # Bomb place sound
        else:
            self.place_bomb_request = False

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

        # Handle image cycling
        if moving:
            if now - self.last_change > self.change_delay:
                self.current_image = (self.current_image + 1) % len(self.images)
                if self.facing_left:
                    self.image = pygame.transform.flip(
                        self.images[self.current_image], True, False
                    )
                else:
                    self.image = self.images[self.current_image]
                self.last_change = now
        else:
            self.image = self.images[0]  # Default to taimei1.png

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

    def shoot(self, mouse_x, mouse_y, scroll_x=0):
        """Create a new bullet that travels toward the mouse position"""
        from bullet import Bullet

        bullet = Bullet(self.rect.centerx, self.rect.centery, mouse_x, mouse_y, scroll_x)
        self.bullets.add(bullet)


    def collect_ammo(self, ammo_box):
        """Called when player collects ammo box"""
        if (
            self.rect.colliderect(ammo_box.rect) and self.velocity_y < 0
        ):  # Only collect when jumping up
            if ammo_box.can_collect():
                self.ammo += 20
                ammo_box.collect()
                pygame.mixer.Sound("sounds/point.wav").play()
                return True  # Indicate successful collection
        return False
