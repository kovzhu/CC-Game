import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/monster2.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -1  # Move left at speed of 5 pixels per frame

    def update(self):
        self.rect.x += self.velocity_x
        # Remove enemy when it goes off screen
        if self.rect.right < 0:
            self.kill()

    def kill(self):
        try:
            # Play death sound
            death_sound = pygame.mixer.Sound("sounds/die.wav")
            death_sound.play()
        except Exception as e:
            print(f"Error playing death sound: {e}")
        super().kill()
