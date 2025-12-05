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

    def draw(self, screen, health, ammo=0, level=1, stage=1, kills=0, kills_needed=5, bombs=3):
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
        
        # Draw level
        level_text = font.render(f"Level: {level}", True, (255, 215, 0))  # Gold color
        screen.blit(level_text, (20, 140))
        
        # Draw bombs count
        bombs_text = font.render(f"Bombs: {bombs}", True, (255, 100, 100))  # Red color
        screen.blit(bombs_text, (20, 180))
        
        # Draw stage info at top center
        stage_text = font.render(f"Stage: {stage}    Enemies: {kills}/{kills_needed}", True, (255, 255, 255))
        screen_width = screen.get_width()
        text_rect = stage_text.get_rect(center=(screen_width // 2, 30))
        screen.blit(stage_text, text_rect)

    
    def draw_stage_clear(self, screen, stage):
        """Draw stage clear message in the center of screen"""
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        
        # Draw "Stage Clear!" message
        clear_text = font_large.render(f"Stage {stage} Clear!", True, (255, 215, 0))
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        text_rect = clear_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        
        # Draw background rectangle for better visibility
        padding = 20
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding, 
                             text_rect.width + padding * 2, text_rect.height + padding * 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, (255, 215, 0), bg_rect, 3)
        
        screen.blit(clear_text, text_rect)
        
        # Draw rewards info
        reward_text = font_small.render("Rewards: +1 HP, +10 Ammo, +1 Bomb, +50 Score", True, (255, 255, 255))
        reward_rect = reward_text.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
        screen.blit(reward_text, reward_rect)


