import pygame
import random
from pygame.math import Vector2
import math


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load("assets/bullet2.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=position)
        self.speed = -3  # Move left
        self.velocity = Vector2(self.speed, 0)

    def update(self):
        self.rect.x += self.velocity.x
        if self.rect.right < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level=None, img1="assets/monster1.png", img2="assets/monster2.png"):
        super().__init__()
        self.health = 10
        self.level = level
        self.image1 = pygame.image.load(img1)
        self.image2 = pygame.image.load(img2)
        self.image1 = pygame.transform.scale(self.image1, (100, 100))
        self.image2 = pygame.transform.scale(self.image2, (100, 100))
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -1
        self.velocity_y = 0
        self.animation_counter = 0

        # Bullet related
        self.bullets = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 5000  # 5 seconds between shots

    def update(self):
        # Apply gravity
        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10

        if self.level:
            old_x = self.rect.x
            self.level.check_collision(self, self.velocity_x, self.velocity_y)
            
            # Turn around at walls
            if self.rect.x == old_x:
                self.velocity_x *= -1
        else:
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y

        # Simple turn around logic if hitting screen edges (optional, but good for testing)
        if self.rect.right > pygame.display.get_surface().get_width():
            self.velocity_x = -1
        elif self.rect.left < 0:
            self.velocity_x = 1
            
        # Animate enemy
        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            if self.image == self.image1:
                self.image = self.image2
            else:
                self.image = self.image1

        # Remove enemy when it falls off screen
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

        # Shooting logic
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

        # Update bullets
        self.bullets.update()

    def shoot(self):
        """Create a new bullet and add it to the bullets group"""
        bullet = Bullet(self.rect.midleft)
        self.bullets.add(bullet)

    def hit(self):
        """Called when enemy is hit by a bullet"""
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def kill(self):
        try:
            death_sound = pygame.mixer.Sound("sounds/die.wav")
            death_sound.play()
        except Exception as e:
            print(f"Error playing death sound: {e}")
        super().kill()


class SlimeEnemy(Enemy):
    def __init__(self, x, y, level=None):
        super().__init__(x, y, level, "assets/monster3.png", "assets/monster4.png")
        self.health = 15  # Tougher
        self.shoot_delay = 1500 # Shoots faster

class BatEnemy(Enemy):
    def __init__(self, x, y, level=None):
        super().__init__(x, y, level, "assets/monster3.png", "assets/monster4.png")
        self.health = 5 # Weaker
        self.shoot_delay = 2500
        self.fly_offset = 0
        self.start_y = y

    def update(self):
        # Flying logic - no gravity
        self.rect.x += self.velocity_x
        
        # Bob up and down
        self.fly_offset += 0.1
        self.rect.y = self.start_y + 50 * math.sin(self.fly_offset)

        # Animate
        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            if self.image == self.image1:
                self.image = self.image2
            else:
                self.image = self.image1

        # Remove if off screen (left)
        if self.rect.right < -100: # Assuming they move left and eventually go off screen
             self.kill()
             
        # Shooting
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

        self.bullets.update()
