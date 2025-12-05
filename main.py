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

# Stage system
current_stage = 1
enemies_killed_this_stage = 0
enemies_needed_per_stage = 5  # Start with 5 enemies per stage
stage_clear = False
stage_clear_time = 0
STAGE_CLEAR_DISPLAY_TIME = 3000  # Show "Stage Clear" for 3 seconds


async def main():
    global running, game_over, ammo_box, last_ammo_box_time, last_hit_time, player
    global current_stage, enemies_killed_this_stage, enemies_needed_per_stage, stage_clear, stage_clear_time

    
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
            
            # Set scroll_x on player for bullet shooting
            player.scroll_x = scroll_x


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

                # Check collision with enemy bullets
                for enemy in enemy_group:
                    bullet_hits = pygame.sprite.spritecollide(player, enemy.bullets, True)
                    if bullet_hits:
                        player.hit()
                        hit_sound.play()
                        
                        # Make player temporarily invulnerable
                        player.image.set_alpha(100)
                        pygame.time.set_timer(pygame.USEREVENT, 500)
                        last_hit_time = current_time
                        
                        if player.health <= 0:
                            game_over = True
                            print("Game Over!")
                            pygame.mixer.Sound("sounds/game-over1.mp3").play()
                        
                        break

            # Spawn ammo box periodically
            if current_time - last_ammo_box_time > AMMO_BOX_INTERVAL:
                if len(ammo_box_group) == 0:  # Only one ammo box at a time
                    # Spawn ahead of player
                    spawn_x = player.rect.x + screen_width // 2 + random.randint(100, 300)
                    spawn_y = random.randint(400, 650)
                    ammo_box = AmmoBox(spawn_x, spawn_y, level)
                    ammo_box_group.add(ammo_box)
                    last_ammo_box_time = current_time

            # Update ammo boxes
            ammo_box_group.update()
            
            # Check ammo box collision
            for box in ammo_box_group:
                if player.rect.colliderect(box.rect):
                    player.ammo += 20
                    pygame.mixer.Sound("sounds/point.wav").play()
                    box.kill()

            # Update player bullets
            player.bullets.update()
            
            # Track enemy count before damage
            enemies_before = len(enemy_group)
            
            # Check player bullet collision with enemies
            for bullet in player.bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
                if hit_enemies:
                    bullet.kill()
                    for enemy in hit_enemies:
                        # Apply damage based on player level
                        for _ in range(player.damage):
                            enemy.hit()
                        # Add score when hitting enemy
                        ui.score += 10
                        ui.update_score()
            
            # Track enemy count after damage to detect kills
            enemies_after = len(enemy_group)
            enemies_killed = enemies_before - enemies_after
            if enemies_killed > 0:
                enemies_killed_this_stage += enemies_killed
                print(f"Killed {enemies_killed} enemies. Progress: {enemies_killed_this_stage}/{enemies_needed_per_stage}")
                
                # Check if stage is complete
                if enemies_killed_this_stage >= enemies_needed_per_stage:
                    stage_clear = True
                    stage_clear_time = pygame.time.get_ticks()
                    current_stage += 1
                    enemies_killed_this_stage = 0
                    # Increase difficulty: more enemies needed per stage
                    enemies_needed_per_stage += 3
                    
                    # Stage rewards
                    if player.health < 3:
                        player.health += 1
                    player.ammo += 10
                    player.bombs += 1
                    ui.score += 50
                    
                    # Clear all existing enemies
                    enemy_group.empty()
                    
                    # Spawn new enemies for next stage (target + 10)
                    enemies_to_spawn = enemies_needed_per_stage + 10
                    for i in range(enemies_to_spawn):
                        # Spawn enemies around the player
                        spawn_x = player.rect.x + random.randint(-500, 1500)
                        
                        # Randomly choose enemy type
                        enemy_type = random.choice([Enemy, SlimeEnemy, BatEnemy])
                        
                        if enemy_type == BatEnemy:
                            spawn_y = random.randint(200, 500)
                        else:
                            spawn_y = random.randint(500, 650)
                        
                        # Create enemy with stage-based health bonus
                        new_enemy = enemy_type(spawn_x, spawn_y, level)
                        health_bonus = ((current_stage - 1) // 3) * 5
                        new_enemy.health += health_bonus
                        enemy_group.add(new_enemy)
                    
                    pygame.mixer.Sound("sounds/point.wav").play()
                    print(f"Stage {current_stage - 1} Clear! Next stage needs {enemies_needed_per_stage} kills")
                    print(f"Spawned {enemies_to_spawn} enemies for Stage {current_stage}")

            
            # Check for level up (every 100 points)
            new_level = (ui.score // 100) + 1
            if new_level > player.player_level:
                player.player_level = new_level
                player.damage = player.player_level
                # Play level up sound
                pygame.mixer.Sound("sounds/point.wav").play()
                print(f"Level Up! Now Level {player.player_level}, Damage: {player.damage}")








        # Spawn new enemy when previous one disappears
        # Keep enemies at target + 10 for consistency with stage clear
        max_enemies = enemies_needed_per_stage + 10
        if len(enemy_group) < max_enemies:
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
                
                # Increase enemy health based on stage (every 3 stages, +5 health)
                health_bonus = ((current_stage - 1) // 3) * 5
                new_enemy.health += health_bonus
                
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
             shield_center = (player.rect.centerx - scroll_x, player.rect.centery)
             pygame.draw.circle(screen, (0, 255, 255), shield_center, 60, 2)
             
        draw_with_offset(enemy_group)
        draw_with_offset(ammo_box_group)
        draw_with_offset(bomb_group)
        draw_with_offset(explosion_group)
        
        # Draw bullets
        for enemy in enemy_group:
            draw_with_offset(enemy.bullets)
        
        # Draw player bullets
        draw_with_offset(player.bullets)

            
        # Draw UI
        ui.draw(screen, player.health, player.ammo, player.player_level, 
                current_stage, enemies_killed_this_stage, enemies_needed_per_stage, player.bombs)
        
        # Draw stage clear message if stage was just cleared
        if stage_clear and pygame.time.get_ticks() - stage_clear_time < STAGE_CLEAR_DISPLAY_TIME:
            ui.draw_stage_clear(screen, current_stage - 1)
        elif stage_clear and pygame.time.get_ticks() - stage_clear_time >= STAGE_CLEAR_DISPLAY_TIME:
            stage_clear = False


        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
