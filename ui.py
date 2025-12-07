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

    def draw(self, screen, health, level=1, stage=1, kills=0, kills_needed=5, bombs=3, ult_ready=True):
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
        
        # Draw level
        level_text = font.render(f"Level: {level}", True, (255, 215, 0))  # Gold color
        screen.blit(level_text, (20, 100))
        
        # Draw bombs count
        bombs_text = font.render(f"Bombs: {bombs}", True, (255, 100, 100))  # Red color
        screen.blit(bombs_text, (20, 180))
        
        # Draw stage info at top center
        stage_text = font.render(f"Stage: {stage}    Enemies: {kills}/{kills_needed}", True, (255, 255, 255))
        screen_width = screen.get_width()
        text_rect = stage_text.get_rect(center=(screen_width // 2, 30))
        screen.blit(stage_text, text_rect)

        # Draw Ultimate Status
        self.draw_ultimate_status(screen, screen_width, is_ready=ult_ready)

    def draw_ultimate_status(self, screen, screen_width, is_ready=True, cooldown_percent=0):
        font = pygame.font.Font(None, 36)
        if is_ready:
            text = font.render("ULTIMATE READY (R)", True, (0, 255, 0)) # Green
        else:
            text = font.render("ULTIMATE CHARGING...", True, (100, 100, 100)) # Grey
            
        text_rect = text.get_rect(topright=(screen_width - 20, 20))
        screen.blit(text, text_rect)

        text_rect = text.get_rect(topright=(screen_width - 20, 20))
        screen.blit(text, text_rect)

    def draw_boss_health(self, screen, current_hp, max_hp, is_final=False):
        """Draw a large, fixed boss health bar at top of screen"""
        screen_width = screen.get_width()
        bar_width = 600
        bar_height = 30
        x = (screen_width - bar_width) // 2
        y = 80 # Below score/stage info
        
        # Draw Name
        font = pygame.font.Font(None, 48)
        name = "FINAL BOSS" if is_final else "BOSS"
        text = font.render(name, True, (255, 50, 50))
        text_rect = text.get_rect(center=(screen_width//2, y - 25))
        screen.blit(text, text_rect)
        
        # Draw Background (Dark Red)
        pygame.draw.rect(screen, (50, 0, 0), (x, y, bar_width, bar_height))
        
        # Draw Health (Bright Red)
        if max_hp > 0:
            ratio = max(0, current_hp / max_hp)
            current_width = int(bar_width * ratio)
            pygame.draw.rect(screen, (255, 0, 0), (x, y, current_width, bar_height))
            
        # Draw Border (White)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 3)

    
    def draw_stage_clear(self, screen, stage):
        """Draw stage clear message in the center of screen"""
        font = pygame.font.Font(None, 74)
        text = font.render(f"STAGE {stage} CLEAR!", True, (255, 215, 0)) # Gold
        screen_width = screen.get_width()
        text_rect = text.get_rect(center=(screen_width // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)

    def draw_start_screen(self, screen, screen_width, screen_height):
        """Draw the start menu with Title and Start Button"""
        # Dim background
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 100)
        title_text = title_font.render("ZC brothers Game", True, (0, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_text, title_rect)

        # Start Button
        button_font = pygame.font.Font(None, 60)
        button_text = button_font.render("START", True, (255, 255, 255))
        
        # Create button rect
        button_rect = button_text.get_rect(center=(screen_width // 2, screen_height // 2))
        button_rect.inflate_ip(40, 20) # Add padding
        
        # Draw button background
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
             pygame.draw.rect(screen, (50, 200, 50), button_rect, border_radius=10) # Lighter green hover
        else:
             pygame.draw.rect(screen, (0, 150, 0), button_rect, border_radius=10) # Green normal
             
        # Draw button text
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        return button_rect

    def draw_level_selection(self, screen, screen_width, screen_height):
        """Draw Level Selection Screen - 100 Levels Grid"""
        # Dim background
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200) # Darker for better visibility of many buttons
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 60)
        title_text = title_font.render("SELECT LEVEL (1-50)", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(title_text, title_rect)

        buttons = []
        font = pygame.font.Font(None, 24)
        
        # 10x5 Grid for 50 levels
        rows = 5
        cols = 10
        
        # Layout calculation
        margin_x = 100
        margin_y = 100
        available_width = screen_width - 2 * margin_x
        available_height = screen_height - 2 * margin_y
        
        btn_width = available_width // cols - 10
        btn_height = available_height // rows - 10
        
        mouse_pos = pygame.mouse.get_pos()
        
        for r in range(rows):
            for c in range(cols):
                stage_num = r * cols + c + 1
                
                x = margin_x + c * (btn_width + 10)
                y = margin_y + r * (btn_height + 10)
                
                rect = pygame.Rect(x, y, btn_width, btn_height)
                
                # Check hover
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (50, 200, 50), rect, border_radius=5)
                else:
                    pygame.draw.rect(screen, (0, 100, 0), rect, border_radius=5)
                
                text = font.render(str(stage_num), True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                
                buttons.append((rect, stage_num))
            
        return buttons

        
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


