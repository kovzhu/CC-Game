import pygame
import random


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/bomb.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
        except:
            # Fallback if image doesn't exist yet
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 0, 0))  # Red circle as placeholder
            pygame.draw.circle(self.image, (0, 0, 0), (20, 20), 18, 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.level = level
        
        # Explosion timer
        self.placed_time = pygame.time.get_ticks()
        self.explosion_delay = 3000  # 3 seconds before explosion
        self.exploded = False
        
        # Explosion properties
        self.explosion_radius = 100  # pixels

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Flash before explosion
        if current_time - self.placed_time > self.explosion_delay - 1000:
            # Flash in last second
            if (current_time // 100) % 2 == 0:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        
        # Check if it's time to explode
        if current_time - self.placed_time > self.explosion_delay and not self.exploded:
            self.explode()
    
    def explode(self):
        """Trigger explosion and destroy nearby tiles"""
        self.exploded = True
        
        # Play explosion sound
        try:
            explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
            explosion_sound.play()
        except:
            pass
        
        # Destroy tiles within explosion radius
        if self.level:
            self.level.destroy_tiles_in_radius(self.rect.centerx, self.rect.centery, self.explosion_radius)
        
        # Kill the bomb sprite
        self.kill()


class Explosion(pygame.sprite.Sprite):
    """Visual effect for bomb explosion"""
    def __init__(self, x, y, radius):
        super().__init__()
        self.radius = radius
        self.max_radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.lifetime = 500  # milliseconds
        self.created_time = pygame.time.get_ticks()
        
        self.update_image()
    
    def update_image(self):
        """Draw expanding explosion circle"""
        self.image.fill((0, 0, 0, 0))  # Clear
        
        # Draw multiple circles for explosion effect
        colors = [(255, 100, 0, 200), (255, 200, 0, 150), (255, 255, 0, 100)]
        for i, color in enumerate(colors):
            radius = int(self.radius * (1 - i * 0.2))
            if radius > 0:
                pygame.draw.circle(self.image, color, (self.max_radius, self.max_radius), radius)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.created_time
        
        if elapsed > self.lifetime:
            self.kill()
        else:
            # Expand the explosion
            progress = elapsed / self.lifetime
            self.radius = int(self.max_radius * (0.5 + progress * 0.5))
            self.update_image()
