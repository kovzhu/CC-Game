import pygame

class UI:
    def __init__(self):
        self.score = 0
        self.health = 2
        # Load heart images
        self.heart_full = pygame.image.load("assets/heart_full.png")
        self.heart_empty = pygame.image.load("assets/heart_empty.png")
        # Scale heart images
        self.heart_full = pygame.transform.scale(self.heart_full, (30, 30))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (30, 30))

    def update_score(self):
        """Update the score display"""
        pass

    def draw(self, screen, health, ammo=0):
        # Draw score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(text, (20, 20))

        # Draw health
        for i in range(3):
            if i < health:
                screen.blit(self.heart_full, (20 + i * 40, 60))
            else:
                screen.blit(self.heart_empty, (20 + i * 40, 60))

        # Draw ammo count
        ammo_text = font.render(f"Ammo: {ammo}", True, (255, 255, 255))
        screen.blit(ammo_text, (20, 100))
