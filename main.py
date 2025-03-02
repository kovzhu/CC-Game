import pygame
from player import Player
from enemy import Enemy
from level import Level
from ui import UI

# Initialize Pygame
pygame.init()

# Initialize mixer and load background music
pygame.mixer.init()
pygame.mixer.music.load("sounds/bg_music.mp3")
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Get screen size
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
screen_size = (screen_width, screen_height)
print(f"{screen_width} x {screen_height}")

# Create the screen
screen = pygame.display.set_mode(screen_size)
# background_color = (255, 255, 255)  # White color
bg = pygame.transform.scale(
    pygame.image.load("assets/bg.png"), (screen_width, screen_height)
)

# set the icons
icon = pygame.image.load("assets/taimei1.png")
pygame.display.set_icon(icon)

# Load sound effects
# hit_sound = pygame.mixer.Sound("sounds/hit.wav")
hit_sound = pygame.mixer.Sound("sounds/lv.wav")

# Set window title
pygame.display.set_caption("ZC brothers Game")

# Create player - position 1/3 above bottom
# player = Player(100, int(screen_height * 1 / 5))
# player = Player(100, 180)
player = Player(100, 605)
player_group = pygame.sprite.Group()
player_group.add(player)

# Create initial enemy
enemy_group = pygame.sprite.Group()
enemy = Enemy(int(screen_width * 0.9), 605)
enemy_group.add(enemy)

# Create level
level_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
level = Level(level_data)

# Create UI
ui = UI()

# Game states
running = True
game_over = False

# Game loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    hit_sound.play()
                else:
                    # Reset game state
                    player_group.empty()  # Clear existing player
                    player = Player(100, 605)  # Create new player
                    player_group.add(player)  # Add to group
                    enemy_group.empty()
                    ui.score = 0
                    ui.update_score()
                    game_over = False

    # Update game logic
    if not game_over:
        player_group.update()
        enemy_group.update()

        # Check for collisions
        collisions = pygame.sprite.spritecollide(player, enemy_group, False)
        if collisions:
            for enemy in collisions:
                player.hit()
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
    # level.draw(screen)

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
                game_over = True
                print("Game Over!")
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

    # Draw UI
    ui.draw(screen)

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
