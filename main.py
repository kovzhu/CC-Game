import pygame
from player import Player, AmmoBox
from enemy import Enemy
from level import Level, level_data
from ui import UI

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

level = Level(level_data)

# Create player - position 1/3 above bottom
# player = Player(100, int(screen_height * 1 / 5))
# player = Player(100, 180)
player = Player(100, 605, level)
player_group = pygame.sprite.Group()
player_group.add(player)

# Create initial enemy
enemy_group = pygame.sprite.Group()
enemy = Enemy(int(screen_width * 0.9), 605)
enemy_group.add(enemy)
level.draw(screen)
# Create UI
ui = UI()

# Create ammo box variables
ammo_box = None
ammo_box_group = pygame.sprite.Group()
last_ammo_box_time = 0
AMMO_BOX_INTERVAL = 5000  # 5 seconds in milliseconds

# Game states
running = True
game_over = False
last_hit_time = 0
HIT_COOLDOWN = 1000  # 1 second cooldown between hits

def main():
    global running, game_over, ammo_box, last_ammo_box_time, last_hit_time, player
    # Game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                # Reset player alpha after invulnerability period
                player.image.set_alpha(255)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        hit_sound.play()
                    else:
                        # Reset game state
                        player_group.empty()  # Clear existing player
                        player = Player(100, 605, level)  # Create new player
                        player_group.add(player)  # Add to group
                        enemy_group.empty()
                        ui.score = 0
                        ui.update_score()
                        game_over = False

        # Update game logic
        if not game_over:
            player_group.update()
            enemy_group.update()

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
                        
                        # Clamp positions to screen bounds
                        player.rect.x = max(0, min(screen_width - player.rect.width, player.rect.x))
                        player.rect.y = max(0, min(screen_height - player.rect.height, player.rect.y))
                        enemy.rect.x = max(0, min(screen_width - enemy.rect.width, enemy.rect.x))
                        enemy.rect.y = max(0, min(screen_height - enemy.rect.height, enemy.rect.y))
                        
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
        if len(enemy_group) == 0:
            new_enemy = Enemy(int(screen_width * 0.9), 605)
            enemy_group.add(new_enemy)

        # Clear screen with white background
        # screen.fill(background_color)
        screen.blit(bg, (0, 0))

        # Draw level
        level.draw(screen)

        # Draw player
        player_group.draw(screen)

        # Draw bullets
        player.bullets.draw(screen)
        player.bullets.update()

        # Draw enemy and their bullets
        enemy_group.draw(screen)
        for enemy in enemy_group:
            enemy.bullets.draw(screen)

        # Check for player bullet-enemy collisions
        bullet_collisions = pygame.sprite.groupcollide(
            player.bullets, enemy_group, True, False
        )

        # Check for enemy bullet-player collisions
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(player, enemy.bullets, True):
                player.hit()
                if player.health <= 0:
                    if not game_over:
                        game_over = True
                        print("Game Over!")
                        pygame.mixer.Sound("sounds/game-over1.mp3").play()
        if bullet_collisions:
            for enemy in bullet_collisions.values():
                for e in enemy:
                    e.hit()
            # Only spawn new enemy when all enemies are dead
            if len(enemy_group) == 0:
                ui.score += 1
                ui.update_score()
                new_enemy = Enemy(int(screen_width * 0.9), 605)
                enemy_group.add(new_enemy)

        # Update and draw ammo box
        current_time = pygame.time.get_ticks()

        # Spawn new ammo box if enough time has passed and no box exists
        if ammo_box is None and current_time - last_ammo_box_time > AMMO_BOX_INTERVAL:
            ammo_box = AmmoBox(-50, 550)  # Start off screen
            ammo_box_group.add(ammo_box)
            last_ammo_box_time = current_time

        ammo_box_group.update()
        ammo_box_group.draw(screen)

        # Check for ammo box collisions
        if ammo_box and player.collect_ammo(ammo_box):
            ammo_box = None  # Mark current box as collected

        # Check for level ammo box collisions
        level_ammo_collisions = pygame.sprite.spritecollide(player, level.ammo_group, False)
        for ammo in level_ammo_collisions:
            if ammo.can_collect():
                player.ammo += 20
                pygame.mixer.Sound("sounds/point.wav").play()
                ammo.collect()

        # Draw UI with ammo count
        ui.draw(screen, player.ammo)

        # Draw game over screen
        if game_over:
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(text, text_rect)
            font = pygame.font.Font(None, 36)
            text = font.render("Press SPACE to restart", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
            screen.blit(text, text_rect)

        # Update display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()


main()
