import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/bullet.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10  # Pixels per frame

    def update(self):
        """Move the bullet right across the screen"""
        self.rect.x += self.speed
        # Remove bullet when it goes off screen
        if self.rect.left > pygame.display.get_surface().get_width():
            self.kill()
