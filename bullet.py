import pygame
import math


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, scroll_x=0):
        """
        Create a bullet that travels toward the target position.
        
        Args:
            x, y: Starting position (player position)
            target_x, target_y: Target position (mouse position)
            scroll_x: Camera scroll offset to convert screen coords to world coords
        """
        super().__init__()
        self.image = pygame.image.load("assets/bullet.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        # Calculate direction vector from player to mouse
        # Adjust target_x for camera scroll to get world coordinates
        world_target_x = target_x + scroll_x
        dx = world_target_x - x
        dy = target_y - y
        
        # Calculate distance and normalize
        distance = math.sqrt(dx**2 + dy**2)
        if distance == 0:
            distance = 1  # Avoid division by zero
        
        # Set velocity (speed = 10 pixels per frame)
        speed = 10
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed

    def update(self):
        """Move the bullet in its direction"""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Remove bullet when it goes way off screen
        if self.rect.x < -1000 or self.rect.x > 100000 or self.rect.y < -1000 or self.rect.y > 10000:
            self.kill()
