import pygame
import os

def create_bat_sprites():
    pygame.init()
    
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    # Bat frame 1 (Wings up/out)
    surf1 = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(surf1, (100, 0, 150), (12, 10, 8, 14))
    # Wings
    pygame.draw.polygon(surf1, (80, 0, 120), [(12, 15), (2, 5), (8, 20)]) # Left wing
    pygame.draw.polygon(surf1, (80, 0, 120), [(20, 15), (30, 5), (24, 20)]) # Right wing
    # Eyes
    pygame.draw.circle(surf1, (255, 0, 0), (14, 14), 1)
    pygame.draw.circle(surf1, (255, 0, 0), (18, 14), 1)
    
    pygame.image.save(surf1, 'assets/bat1.png')
    
    # Bat frame 2 (Wings down)
    surf2 = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(surf2, (100, 0, 150), (12, 12, 8, 14))
    # Wings
    pygame.draw.polygon(surf2, (80, 0, 120), [(12, 17), (2, 25), (8, 15)]) # Left wing
    pygame.draw.polygon(surf2, (80, 0, 120), [(20, 17), (30, 25), (24, 15)]) # Right wing
    # Eyes
    pygame.draw.circle(surf2, (255, 0, 0), (14, 16), 1)
    pygame.draw.circle(surf2, (255, 0, 0), (18, 16), 1)
    
    pygame.image.save(surf2, 'assets/bat2.png')
    
    print("Bat sprites generated!")

if __name__ == "__main__":
    create_bat_sprites()
