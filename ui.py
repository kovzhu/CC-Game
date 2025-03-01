import pygame  # Imports the Pygame library


class UI:  # Creates a UI class
    def __init__(self):  # Defines the constructor for the UI class
        self.score = 0  # Initialize score
        self.lives = 3  # Initialize lives

    def update_score(self):
        """Update the score display"""
        pass

    def draw(self, screen):  # Defines a method to draw the UI on the screen
        font = pygame.font.Font(
            None, 36
        )  # Creates a font object with the default font and size 36
        score_text = font.render(
            f"Score: {self.score}", True, (0, 0, 0)
        )  # Renders the score text with white color
        lives_text = font.render(
            f"Lives: {self.lives}", True, (0, 0, 0)
        )  # Renders the lives text with white color
        screen.blit(
            score_text, (10, 10)
        )  # Draws the score text on the screen at position (10, 10)
        screen.blit(
            lives_text, (10, 50)
        )  # Draws the lives text on the screen at position (10, 50)
