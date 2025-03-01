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

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                hit_sound.play()

    # Update game logic
    player_group.update()
    enemy_group.update()

    # Check for collisions
    collisions = pygame.sprite.spritecollide(player, enemy_group, False)
    if collisions:
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            # Kill enemy, increase score, and spawn new one
            for enemy in collisions:
                enemy.kill()
                ui.score += 1
                ui.update_score()
            new_enemy = Enemy(int(screen_width * 0.9), 605)
            enemy_group.add(new_enemy)

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

    # Draw enemy
    enemy_group.draw(screen)

    # Check for bullet-enemy collisions
    bullet_collisions = pygame.sprite.groupcollide(
        player.bullets, enemy_group, True, True
    )
    if bullet_collisions:
        ui.score += len(bullet_collisions)
        ui.update_score()
        new_enemy = Enemy(int(screen_width * 0.9), 605)
        enemy_group.add(new_enemy)

    # Draw UI
    ui.draw(screen)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
