import pygame
import random
from pygame.math import Vector2

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load("assets/bullet2.png")
        self.rect = self.image.get_rect(center=position)
        self.speed = -5  # Move left
        self.velocity = Vector2(self.speed, 0)

    def update(self):
        self.rect.x += self.velocity.x
        if self.rect.right < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.health = 3
        self.image1 = pygame.image.load("assets/monster1.png")
        self.image2 = pygame.image.load("assets/monster2.png")
        self.image1 = pygame.transform.scale(self.image1, (100, 100))
        self.image2 = pygame.transform.scale(self.image2, (100, 100))
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -1
        self.animation_counter = 0
        
        # Bullet related
        self.bullets = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 2000  # 2 seconds between shots

    def update(self):
        self.rect.x += self.velocity_x

        # Animate enemy
        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            if self.image == self.image1:
                self.image = self.image2
            else:
                self.image = self.image1

        # Remove enemy when it goes off screen
        if self.rect.right < 0:
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
