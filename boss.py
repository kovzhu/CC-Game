import pygame
import random
import math
from enemy import Bullet, Enemy

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((30, 10))
        self.image.fill((255, 0, 0)) # Red laser
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction
        self.damage = 1

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > 3000: # Arbitrary large limit
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, level, is_final=False):
        super().__init__()
        self.level = level
        self.is_final = is_final
        
        # Load Boss Image
        # Using a distinct image or reusing with tint/scale
        try:
            if is_final:
                img = pygame.image.load("assets/taimei.png") # Special boss
                self.health = 1180
            else:
                img = pygame.image.load("assets/monster3.PNG") # Mini boss
                self.health = 600
        except:
             img = pygame.image.load("assets/monster1.png")
             self.health = 100

        self.max_health = self.health # Store max health for UI scaling

        # Scale up
        self.image = pygame.transform.scale(img, (200, 200))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = -1 # Facing left initially
        self.move_counter = 0
        self.move_state = "idle" # idle, move, attack
        
        # Combat
        self.bullets = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        
        self.last_attack_time = pygame.time.get_ticks()
        self.attack_cooldown = 2000
        
        self.last_summon_time = pygame.time.get_ticks()
        self.summon_cooldown = 5000
        
        # Jump mechanics
        self.last_jump_time = pygame.time.get_ticks()
        self.jump_cooldown = 3000  # Jump every 3 seconds
        self.is_jumping = False

    def update(self, player):
        # Apply Gravity
        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10
            
        # Collision with Level
        if self.level:
            old_x = self.rect.x
            self.level.check_collision(self, self.velocity_x, self.velocity_y)
            if self.rect.x == old_x:
                self.velocity_x *= -1

        # AI Logic
        self.ai_behavior(player)
        
        # Updates
        self.bullets.update()
        self.lasers.update()

    def ai_behavior(self, player):
        now = pygame.time.get_ticks()
        
        # Simple tracking: Face player
        if player.rect.centerx < self.rect.centerx:
            self.direction = -1
        else:
            self.direction = 1
            
        # Movement phases
        self.move_counter += 1
        if self.move_counter < 100:
            self.velocity_x = 0 # Idle
        elif self.move_counter < 300:
             # Move slowly towards player? Or patrol?
             # Let's just hover/move slightly
             self.velocity_x = 2 * self.direction
        else:
            self.move_counter = 0
            
        # Attack Logic
        if now - self.last_attack_time > self.attack_cooldown:
            attack_choice = random.choice(["bullet", "laser"])
            if attack_choice == "bullet":
                self.shoot_bullet()
            elif attack_choice == "laser":
                self.shoot_laser()
            self.last_attack_time = now
            
        # Summon Logic (Final Boss Only)
        if self.is_final:
            if now - self.last_summon_time > self.summon_cooldown:
                self.summon_minions()
                self.last_summon_time = now
        
        # Jump Logic
        if now - self.last_jump_time > self.jump_cooldown:
            # Check if on ground (velocity_y is small or zero after collision)
            if abs(self.velocity_y) < 2:
                self.velocity_y = -15  # Jump upward
                self.is_jumping = True
                self.last_jump_time = now

    def shoot_bullet(self):
        # Shoot 3 bullets in a spread
        for i in range(-1, 2):
            b = Bullet(self.rect.center)
            # Override bullet velocity for boss?
            # Existing Bullet class moves left (-3). 
            # We might need custom boss bullets if we want them to aim.
            # For now, let's just make new bullet logic inline or use simple ones.
            # Actually, standard Bullet just goes left. We need aimed bullets.
            
            # Let's just use our own Bullet logic here or subclass.
            # We'll rely on the update loop update logic? 
            # The 'Bullet' imported from enemy updates itself.
            # Let's modify the bullet instance
            
            b.speed = 5 * self.direction
            b.velocity.x = b.speed
            b.velocity.y = i * 2 # Spread
            self.bullets.add(b)

    def shoot_laser(self):
        # Shoot a beam
        l = Laser(self.rect.centerx, self.rect.centery, self.direction)
        self.lasers.add(l)

    def summon_minions(self):
        # We need a way to return these to the main loop, 
        # or we just spawn them here and let Main pick them up?
        # Main updates 'enemy_group'.
        # We can add a property 'spawn_queue' that main checks.
        self.spawn_queue = []
        for _ in range(3):
             # Just signal main to spawn
             pass
        # Actually simplest is to return a list or have a flag.
        # Let's use a public list 'minions_to_add'
        if not hasattr(self, 'minions_to_add'):
            self.minions_to_add = []
        
        # Add 3 enemies
        for _ in range(3):
            # We don't have access to Level object fully initialized with enemies?
            # We'll store simple data: (type, x, y)
             self.minions_to_add.append("random")
             
    def draw(self, screen):
         screen.blit(self.image, self.rect)
         self.bullets.draw(screen)
         self.lasers.draw(screen)
         
         # Health Bar
         pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 20, self.rect.width, 10))
         current_health_width = int(self.rect.width * (self.health / (500 if self.is_final else 200)))
         pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 20, current_health_width, 10))

