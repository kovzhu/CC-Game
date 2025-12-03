import pygame
import asyncio
import random
from player import Player, AmmoBox
from enemy import Enemy, SlimeEnemy, BatEnemy
from level import Level
from ui import UI
from bomb import Bomb, Explosion

# Initialize Pygame
pygame.init()

# Initialize mixer and load background music
pygame.mixer.init()
pygame.mixer.music.load("sounds/bg_music.mp3")
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Get screen size
screen_width = pygame.display.Info().current_w
# screen_width = 1440
screen_height = pygame.display.Info().current_h
# screen_height = 900
screen_size = (screen_width, screen_height)
print(f"{screen_width} x {screen_height}")

# Create the screen
screen = pygame.display.set_mode(screen_size)
# background_color = (255, 255, 255)  # White color
bg = pygame.transform.scale(
    pygame.image.load("assets/bg.png"), (screen_width, screen_height)
).convert()

# set the icons
icon = pygame.image.load("assets/taimei1.png").convert()
pygame.display.set_icon(icon)

# Load sound effects
# hit_sound = pygame.mixer.Sound("sounds/hit.wav")
hit_sound = pygame.mixer.Sound("sounds/lv.wav")

# Set window title
pygame.display.set_caption("ZC brothers Game")

# # Create level

level = Level()

# Create player - position 1/3 above bottom
# player = Player(100, int(screen_height * 1 / 5))
# player = Player(100, 180)
player = Player(100, 605, level)
player_group = pygame.sprite.Group()
player_group.add(player)

# Create initial enemy
enemy_group = pygame.sprite.Group()
enemy = Enemy(int(screen_width * 0.9), 605, level)
enemy_group.add(enemy)
level.draw(screen)
# Create UI
ui = UI()

# Create ammo box variables
ammo_box = None
ammo_box_group = pygame.sprite.Group()
last_ammo_box_time = 0
AMMO_BOX_INTERVAL = 5000  # 5 seconds in milliseconds

# Bomb and explosion groups
bomb_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Game states
running = True
game_over = False
last_hit_time = 0
HIT_COOLDOWN = 1000  # 1 second cooldown between hits

async def main():
    global running, game_over, ammo_box, last_ammo_box_time, last_hit_time, player
    
    clock = pygame.time.Clock()
    
    # Camera scroll
    scroll_x = 0
    
    # Game loop
    while running:
        clock.tick(60)  # Cap at 60 FPS
        
        # ... (events) ...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                player.image.set_alpha(255)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        hit_sound.play()
                    else:
                        # Reset game state
                        player_group.empty()
                        player = Player(100, 605, level)
                        player_group.add(player)
                        enemy_group.empty()
                        ui.score = 0
                        ui.update_score()
                        game_over = False
                        scroll_x = 0 # Reset scroll

        # Update game logic
        if not game_over:
            player_group.update()
            if player.health <= 0:
                game_over = True
                print("Game Over!")
                pygame.mixer.Sound("sounds/game-over1.mp3").play()
            enemy_group.update()

            # Update camera scroll
            target_x = player.rect.centerx - screen_width / 2
            scroll_x += (target_x - scroll_x) / 20
            
            # Limit scroll to level bounds
            level_width = len(level.level_data[0]) * level.tile_size
            scroll_x = max(0, min(scroll_x, level_width - screen_width))

            # Only check collisions if not currently invulnerable
            current_time = pygame.time.get_ticks()
            if current_time - last_hit_time > HIT_COOLDOWN:
                collisions = pygame.sprite.spritecollide(player, enemy_group, False)
                if collisions:
                    for enemy in collisions:
                        # Calculate push direction and distance
                        dx = enemy.rect.centerx - player.rect.centerx
                        dy = enemy.rect.centery - player.rect.centery
                        distance = max(1, (dx**2 + dy**2)**0.5)
                        
                        # Normalize and scale pushback
                        push_x = int(150 * dx/distance)
                        push_y = int(80 * dy/distance)
                        
                        # Apply pushback to both sprites
                        player.rect.x -= push_x
                        player.rect.y -= push_y
                        enemy.rect.x += push_x
                        enemy.rect.y += push_y
                        
                        # Clamp positions to screen bounds (only X)
                        # player.rect.x = max(0, min(screen_width - player.rect.width, player.rect.x))
                        enemy.rect.x = max(0, min(level_width - enemy.rect.width, enemy.rect.x))
                        
                        # Make player temporarily invulnerable
                        player.image.set_alpha(100)
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # Reset alpha after 0.5s
                        last_hit_time = current_time  # Start cooldown immediately
                        
                        # Force immediate position update
                        player_group.update()
                        enemy_group.update()
                        
                        # Debug output
                        print(f"Collision at {current_time} - Player pushed by ({push_x},{push_y})")
                        
                        player.hit()
                        last_hit_time = current_time
                        if player.health <= 0:
                            game_over = True
                            print("Game Over!")

        # Spawn new enemy when previous one disappears
        if len(enemy_group) < 3:  # Keep 3 enemies active
            # Spawn enemy ahead of player
            spawn_x = player.rect.x + screen_width + random.randint(0, 200)
            
            # Randomly choose enemy type
            enemy_type = random.choice([Enemy, SlimeEnemy, BatEnemy])
            
            if enemy_type == BatEnemy:
                 spawn_y = random.randint(200, 500) # Higher for bats
            else:
                 spawn_y = random.randint(500, 650) # Ground for others

            if spawn_x < len(level.level_data[0]) * level.tile_size:
                new_enemy = enemy_type(spawn_x, spawn_y, level)
                enemy_group.add(new_enemy)
        
        # Handle bomb placement
        if hasattr(player, 'place_bomb_request') and player.place_bomb_request:
            bomb = Bomb(player.rect.centerx - 20, player.rect.centery, level)
            bomb_group.add(bomb)
        
        # Update bombs and check for explosions
        for bomb in bomb_group:
            if bomb.exploded:
                # Create explosion visual effect
                explosion = Explosion(bomb.rect.centerx, bomb.rect.centery, bomb.explosion_radius)
                explosion_group.add(explosion)
        
        bomb_group.update()
        explosion_group.update()

        # Clear screen with white background
        # screen.fill(background_color)
        screen.blit(bg, (0, 0))

        # Draw level
        level.draw(screen, scroll_x)

        # Helper to draw sprites with offset
        def draw_with_offset(group):
            for sprite in group:
                screen.blit(sprite.image, (sprite.rect.x - scroll_x, sprite.rect.y))

        # Draw player
        draw_with_offset(player_group)
        
        # Draw shield if player is defending
        if hasattr(player, 'is_defending') and player.is_defending:
             # Draw shield effect (e.g., a circle around the player)
             pygame.draw.circle(screen, (0, 255, 255), player.rect.center, 60, 2)
             
        draw_with_offset(enemy_group)
        draw_with_offset(ammo_box_group)
        draw_with_offset(bomb_group)
        draw_with_offset(explosion_group)
        
        # Draw bullets
        for enemy in enemy_group:
            draw_with_offset(enemy.bullets)
            
        # Draw UI
        ui.draw(screen, player.health, player.ammo)

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
