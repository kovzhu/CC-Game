import pygame


class AmmoBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/ammo.jpg")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3  # Movement speed
        self.screen_width = pygame.display.Info().current_w

    def update(self):
        # Move left to right
        self.rect.x += self.speed

        # Wrap around when reaching screen edge
        if self.rect.left > self.screen_width:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = self.screen_width


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.health = 2
        # Load player images
        self.images = [pygame.image.load(f"assets/taimei{i}.png") for i in range(1, 4)]
        self.images = [pygame.transform.scale(img, (70, 110)) for img in self.images]
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.last_change = pygame.time.get_ticks()
        self.change_delay = 10000
        self.last_sound_time = 0
        self.sound_cooldown = 200
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 500
        self.last_shot_time = 0
        self.ammo = 0  # Start with no ammo
        self.has_ammo_box = True  # Flag to track if ammo box exists

    def update(self):
        keys = pygame.key.get_pressed()
        moving = False
        now = pygame.time.get_ticks()

        # Handle movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -5
            moving = True
            if now - self.last_sound_time > self.sound_cooldown:
                pygame.mixer.Sound("sounds/swoosh.wav").play()
                self.last_sound_time = now
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = 5
            moving = True
            if now - self.last_sound_time > self.sound_cooldown:
                pygame.mixer.Sound("sounds/swoosh.wav").play()
                self.last_sound_time = now
        else:
            self.velocity_x = 0

        # Handle jumping
        if keys[pygame.K_UP] and not self.is_jumping:
            self.velocity_y = -15
            self.is_jumping = True
            moving = True
            pygame.mixer.Sound("sounds/wing.wav").play()

        # Handle shooting only if player has ammo
        if keys[pygame.K_SPACE] and self.ammo > 0:
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
                self.shoot()
                self.last_shot_time = now
                self.ammo -= 1

        # Apply gravity
        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10

        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Handle ground collision
        if self.rect.y >= 605:  # Ground level
            self.rect.y = 605
            self.velocity_y = 0
            self.is_jumping = False

        # Handle image cycling
        if moving:
            if now - self.last_change > self.change_delay:
                self.current_image = (self.current_image + 1) % len(self.images)
                self.image = self.images[self.current_image]
                self.last_change = now
        else:
            self.image = self.images[0]  # Default to taimei1.png

    def hit(self):
        """Called when player collides with enemy"""
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def shoot(self):
        """Create a new bullet and add it to the bullets group"""
        from bullet import Bullet

        bullet = Bullet(self.rect.centerx, self.rect.centery)
        self.bullets.add(bullet)

    def collect_ammo(self, ammo_box):
        """Called when player collects ammo box"""
        if self.rect.colliderect(ammo_box.rect) and self.velocity_y < 0:  # Only collect when jumping up
            self.ammo += 200
            ammo_box.kill()
            pygame.mixer.Sound("sounds/point.wav").play()
            return True  # Indicate successful collection
        return False
