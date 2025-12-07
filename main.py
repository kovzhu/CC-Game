import pygame
import asyncio
import random
from player import Player
from enemy import Enemy, SlimeEnemy, BatEnemy
from level import Level
from ui import UI
from boss import Boss
from bomb import Bomb, Explosion

# Initialize Pygame
pygame.init()

# Initialize mixer and load background music
pygame.mixer.init()
pygame.mixer.music.load("sounds/mixkit-complex-desire-1093.mp3")
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
    pygame.image.load("assets/bg_new.png"), (screen_width, screen_height)
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
    global running, game_over, last_hit_time, player
    global current_stage, enemies_killed_this_stage, enemies_needed_per_stage, stage_clear, stage_clear_time
    
    game_active = False # Start in menu
    level_selection_active = False

    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    boss_lasers = pygame.sprite.Group()
    
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
            
            # Handle Start Menu Events
            # Handle Start Menu Events
            if not game_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if level_selection_active:
                         # Get buttons from UI helper logic (simulated or recalled)
                         # Since we don't store the button rects from the draw call in a persistent state easily accessible here (unless we made it a class member of UI or Main),
                         # we should just recalculate them. The UI code is deterministic.
                         # OR better: call a helper function in UI that returns the button at a pos.
                         # But for now, let's just use the same logic iteration.
                         
                         rows = 5
                         cols = 10
                         margin_x = 100
                         margin_y = 100
                         available_width = screen_width - 2 * margin_x
                         available_height = screen_height - 2 * margin_y
                         btn_width = available_width // cols - 10
                         btn_height = available_height // rows - 10
                         
                         start_stage = -1
                         
                         # Check clicks
                         for r in range(rows):
                            for c in range(cols):
                                x = margin_x + c * (btn_width + 10)
                                y = margin_y + r * (btn_height + 10)
                                rect = pygame.Rect(x, y, btn_width, btn_height)
                                
                                if rect.collidepoint(event.pos):
                                    stage_num = r * cols + c + 1
                                    start_stage = stage_num
                                    break
                            if start_stage != -1:
                                break
                        
                         if start_stage != -1:
                                current_stage = start_stage
                                enemies_killed_this_stage = 0
                                # Formula: 5 + (Stage - 1) * 4
                                enemies_needed_per_stage = 15 + ((current_stage - 1) // 10) * 5
                                
                                level_selection_active = False
                                game_active = True
                                pygame.mixer.Sound("sounds/point.wav").play()
                                
                                # Reset game state for new stage
                                player_group.empty()
                                player = Player(100, 605, level)
                                player_group.add(player)
                                enemy_group.empty()
                                boss_group.empty()
                                ui.score = 0
                                ui.update_score()
                                
                                # Boss Check for direct jump
                                if current_stage in [10, 20, 30, 40, 50]:
                                     is_final = (current_stage == 50)
                                     boss = Boss(player.rect.x + 600, 500, level, is_final)
                                     boss_group.add(boss)
                                     enemies_needed_per_stage = 9999
                                else:
                                     # Normal spawn logic... handled by update loop? 
                                     # Main loop handles respawn if low count.
                                     pass
                                
                                
                    else:
                        # Start Screen Button
                        button_rect = pygame.Rect(0, 0, 300, 100)
                        button_rect.center = (screen_width // 2, screen_height // 2)
                        
                        if button_rect.collidepoint(event.pos):
                             # Go to Level Selection
                             level_selection_active = True
                             pygame.mixer.Sound("sounds/point.wav").play()

                if event.type == pygame.KEYDOWN:
                    if not level_selection_active:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                             level_selection_active = True
                             pygame.mixer.Sound("sounds/point.wav").play()
                continue
            
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
                        
            elif event.type == pygame.KEYDOWN:
                # B key to return to level selection
                if event.key == pygame.K_b and game_active and not game_over:
                    game_active = False
                    level_selection_active = True
                    # Reset game state
                    player_group.empty()
                    player = Player(100, 605, level)
                    player_group.add(player)
                    enemy_group.empty()
                    boss_group.empty()
                    ui.score = 0
                    ui.update_score()
                    scroll_x = 0
                    pygame.mixer.Sound("sounds/point.wav").play()
                         
        if not game_active:
            screen.blit(bg, (0, 0))
            
            if level_selection_active:
                # helper to get buttons
                stage_buttons = ui.draw_level_selection(screen, screen_width, screen_height)
            else:
                ui.draw_start_screen(screen, screen_width, screen_height)

            pygame.display.flip()

            # Handle events specifically for menu to avoid complex nesting
            # Ideally we handle all events at top, but let's stick to this structure
            continue

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
                        # Make player temporarily invulnerable
                        player.image.set_alpha(100)
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # Reset alpha after 0.5s
                        last_hit_time = current_time  # Start cooldown immediately
                        
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



                        break

            # Update Bosses
            boss_group.update(player)
            for boss in boss_group:
                 # Add boss projectiles to groups to draw/update?
                 # Actually boss.bullets are in boss object. We need to draw/update them or move them to global group.
                 # Boss.update calls internal group updates. We just need to check collisions.
                 
                 # Boss Bullets hitting Player
                 hits = pygame.sprite.spritecollide(player, boss.bullets, True)
                 if hits:
                     # Check if player is defending with shield
                     if player.is_defending and player.shield_hits < player.max_shield_hits:
                         player.shield_hits += 1
                         pygame.mixer.Sound("sounds/hit.wav").play()
                         # Shield breaks after 3 hits
                         if player.shield_hits >= player.max_shield_hits:
                             player.is_defending = False  # Force shield down
                     else:
                         player.health -= 1
                         pygame.mixer.Sound("sounds/hit.wav").play()
                     
                 # Boss Lasers hitting Player
                 hits = pygame.sprite.spritecollide(player, boss.lasers, False) # Don't kill laser
                 if hits:
                     if pygame.time.get_ticks() % 10 == 0: # Damage tick
                         # Check if player is defending with shield
                         if player.is_defending and player.shield_hits < player.max_shield_hits:
                             player.shield_hits += 1
                             pygame.mixer.Sound("sounds/hit.wav").play()
                             # Shield breaks after 3 hits
                             if player.shield_hits >= player.max_shield_hits:
                                 player.is_defending = False  # Force shield down
                         else:
                             player.health -= 1
                             pygame.mixer.Sound("sounds/hit.wav").play()

                 # Summon Minions (Final Boss)
                 if hasattr(boss, 'minions_to_add') and boss.minions_to_add:
                     for m in boss.minions_to_add:
                         # Spawn minion
                         spawn_x = boss.rect.x + random.randint(-200, 200)
                         spawn_y = 600
                         new_enemy = Enemy(spawn_x, spawn_y, level)
                         enemy_group.add(new_enemy)
                     boss.minions_to_add = []

                 # Check Boss Death -> Stage Clear
                 if boss.health <= 0:
                     boss.kill()
                     # Instant Clear
                     stage_clear = True
                     stage_clear_time = pygame.time.get_ticks()
                     current_stage += 1
                     enemies_killed_this_stage = 0
                     enemies_needed_per_stage = 15 + ((current_stage - 1) // 10) * 5
                     
                     print(f"BOSS DEFEATED! Stage {current_stage-1} Clear!")
                     
                     # Big Reward
                     player.health = 3
                     player.bombs += 5
                     ui.score += 1000
                     
                     enemy_group.empty()
                     boss_group.empty()
                     
                     # Resume normal play
                     enemies_to_spawn = enemies_needed_per_stage + 10
                     for i in range(enemies_to_spawn):
                        spawn_x = player.rect.x + random.randint(-500, 1500)
                        enemy_type = random.choice([Enemy, SlimeEnemy, BatEnemy])
                        if enemy_type == BatEnemy:
                            spawn_y = random.randint(200, 500)
                        else:
                            spawn_y = random.randint(500, 650)
                        new_enemy = enemy_type(spawn_x, spawn_y, level)
                        new_enemy.health += ((current_stage - 1) // 3) * 5
                        enemy_group.add(new_enemy)


            # Update player bullets and beams
            player.bullets.update()
            player.sword_beams.update()
            
            # Check collisions with Boss
            for beam in player.sword_beams:
                hits = pygame.sprite.spritecollide(beam, boss_group, False)
                if hits:
                    for boss in hits:
                        boss.health -= 10 # Beam damage
                        beam.kill() # Destroy beam on boss hit
            
            # Melee hitting Boss
            if player.is_attacking:
                hitbox = player.get_melee_hitbox()
                for boss in boss_group:
                    if hitbox.colliderect(boss.rect):
                        boss.health -= 2 # Melee DPS
            
            # Ultimate hitting Boss
            if player.ultimate_request:
                # (Logic handled below in ultimate block, but we need to target boss group too)
                pass

            
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

            # Check sword beam collision (Piercing)
            for beam in player.sword_beams:
                hit_enemies = pygame.sprite.spritecollide(beam, enemy_group, False)
                if hit_enemies:
                    for enemy in hit_enemies:
                         if enemy not in beam.hit_enemies:
                             # Beams do massive damage but don't disappear (Piercing)
                             enemy.health -= 2 
                             beam.hit_enemies.add(enemy)
                             if enemy.health <= 0:
                                 enemy.kill()
                                 explosion_group.add(Explosion(enemy.rect.centerx, enemy.rect.centery, 50))
                                 ui.score += 10
                                 ui.update_score()
            
            # Track enemy count after damage to detect kills
            enemies_after = len(enemy_group)
            enemies_killed = enemies_before - enemies_after
            if enemies_killed > 0:
                enemies_killed_this_stage += enemies_killed
                print(f"Killed {enemies_killed} enemies. Progress: {enemies_killed_this_stage}/{enemies_needed_per_stage}")
                
                # Check for stage clear
                if enemies_killed_this_stage >= enemies_needed_per_stage:
                    stage_clear = True
                    stage_clear_time = pygame.time.get_ticks()
                    current_stage += 1
                    enemies_killed_this_stage = 0
                    enemies_needed_per_stage = 15 + ((current_stage - 1) // 10) * 5
                    
                    print(f"Stage {current_stage-1} Clear! Next stage needs {enemies_needed_per_stage} kills")
                    
                    # Rewards
                    if player.health < 3:
                        player.health += 1
                    player.bombs += 1
                    ui.score += 50
                    
                    # Level Up Player
                    player.player_level += 1
                    player.damage += 1 # Simple scaling
                    
                    enemy_group.empty()
                    
                    enemies_to_spawn = enemies_needed_per_stage + 10

                    # BOSS ROUND CHECK
                    if current_stage in [10, 20, 30, 40, 50]:
                        print(f"WARNING: BOSS APPROACHING! Stage {current_stage}")
                        # Clear any lingering enemies
                        enemy_group.empty()
                        enemies_to_spawn = 0 # No normal enemies initially
                        
                        is_final = (current_stage == 50)
                        # Spawn Boss at end of screen? Or middle?
                        spawn_x = player.rect.x + 600
                        spawn_y = 500 # Ground level-ish
                        
                        boss = Boss(spawn_x, spawn_y, level, is_final)
                        boss_group.add(boss)
                        
                        # Stop normal spawning
                        enemies_needed_per_stage = 9999 # Pseudo-infinite until boss dies
                    else:
                        boss_group.empty() # Cleanup previous bosses if any
                        
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
        # Infinite Map Extension
        # Check if player is near the edge (e.g., within 1000 pixels)
        level_width = len(level.level_data[0]) * level.tile_size
        if player.rect.right > level_width - 1000:
             print("Extending Level...")
             level.extend_level()
             
             # Also visual extension: we need to handle background if it's not tiling?
             # Background is blitted based on screen size, so it's fine.
             
        # Spawn new enemy when previous one disappears
        # Keep enemies at target + 10 for consistency with stage clear
        # STRICTLY DISABLE for Boss Stages
        if current_stage not in [10, 20, 30, 40, 50]:
            max_enemies = enemies_needed_per_stage + 10
            if len(enemy_group) < max_enemies:
                # Spawn enemy ahead AND behind to disperse
                # Widen range: -1000 to +2500 relative to player
                offset = random.randint(-1000, 2500)
                spawn_x = player.rect.x + offset
                
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

        # Handle Ultimate Execution
        if player.ultimate_request:
            if len(enemy_group) > 0:
                print("HEAVENLY STRIKE!")
                try:
                    pygame.mixer.Sound("sounds/grenade blast.wav").play()
                except:
                    pass
                
                # Screen Shake / Flash effect (simple implementation)
                screen.fill((255, 255, 255)) # Flash white
                
                # Damage ALL enemies
                for enemy in enemy_group:
                    # Create explosion at enemy position
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 100)
                    explosion_group.add(explosion)
                    
                    # Kill enemy
                    enemy.kill() 
                    
                    # Update score
                    ui.score += 10
                    ui.update_score()
                    
                    # Track kills for stage progress
                    enemies_killed_this_stage += 1
                
                # Damage Bosses
                for boss in boss_group:
                    boss.health -= 50 # Massive damage to boss
                    # Explosion effect on boss
                    explosion = Explosion(boss.rect.centerx, boss.rect.centery, 150)
                    explosion_group.add(explosion)
                    if boss.health <= 0:
                        # Logic handled in main loop update, but we can kill it here too
                        # Let the main loop handle the "Death -> Stage Clear" transition 
                        # to avoid code duplication, OR duplicate it here if needed immediately.
                        # For safety, let's just reduce health. The main loop checks "if boss.health <= 0" later.
                        pass
                


                # Check for stage clear inside Ultimate loop
                if enemies_killed_this_stage >= enemies_needed_per_stage:
                    stage_clear = True
                    stage_clear_time = pygame.time.get_ticks()
                    current_stage += 1
                    enemies_killed_this_stage = 0
                    enemies_needed_per_stage = 15 + ((current_stage - 1) // 10) * 5
                    
                    print(f"Stage {current_stage-1} Clear! Next stage needs {enemies_needed_per_stage} kills")
                    
                    # Rewards
                    if player.health < 3:
                         player.health += 1
                    player.bombs += 1
                    ui.score += 50
                    
                    player.player_level += 1
                    player.damage += 1
                    
                    enemy_group.empty()
                     
                    enemies_to_spawn = enemies_needed_per_stage + 10
                    
                    pygame.mixer.Sound("sounds/point.wav").play()
                    print(f"Stage {current_stage - 1} Clear! (Ultimate)")

            # Reset request
            player.ultimate_request = False
            
        # Handle Melee Collision
        if player.is_attacking:
            hitbox = player.get_melee_hitbox()
            hit_enemies = [e for e in enemy_group if hitbox.colliderect(e.rect)]
            if hit_enemies:
                for enemy in hit_enemies:
                    try:
                        pygame.mixer.Sound("sounds/hit.wav").play()
                    except:
                        pass
                    enemy.health -= 5 # High damage for melee
                    if enemy.health <= 0:
                        enemy.kill()
                        explosion_group.add(Explosion(enemy.rect.centerx, enemy.rect.centery, 50))
                        ui.score += 2
                        enemies_killed_this_stage += 1
                        ui.update_score()
                        
                        # Check stage clear (Deduplicate logic later if possible)
                        if enemies_killed_this_stage >= enemies_needed_per_stage:
                             stage_clear = True
                             stage_clear_time = pygame.time.get_ticks()
                             current_stage += 1
                             enemies_killed_this_stage = 0
                             enemies_needed_per_stage = 15 + ((current_stage - 1) // 10) * 5
                             
                             print(f"Stage {current_stage-1} Clear! Next stage needs {enemies_needed_per_stage} kills")
                             
                             # Rewards
                             if player.health < 3:
                                 player.health += 1
                             player.bombs += 1
                             ui.score += 50
                             
                             player.player_level += 1
                             player.damage += 1
                             
                             enemy_group.empty()
                             
                             enemies_to_spawn = enemies_needed_per_stage + 10
                             for i in range(enemies_to_spawn):
                                 spawn_x = player.rect.x + random.randint(-500, 1500)
                                 enemy_type = random.choice([Enemy, SlimeEnemy, BatEnemy])
                                 if enemy_type == BatEnemy:
                                     spawn_y = random.randint(200, 500)
                                 else:
                                     spawn_y = random.randint(500, 650)
                                 new_enemy = enemy_type(spawn_x, spawn_y, level)
                                 health_bonus = ((current_stage - 1) // 3) * 5
                                 new_enemy.health += health_bonus
                                 enemy_group.add(new_enemy)
                             print(f"Stage {current_stage - 1} Clear! (Melee)")

        # Draw attacks
        player.draw_attack(screen)


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
        draw_with_offset(bomb_group)
        draw_with_offset(explosion_group)
        
        # Draw bullets
        for enemy in enemy_group:
            draw_with_offset(enemy.bullets)
        

        
        # Draw player bullets and beams
        draw_with_offset(player.bullets)
        draw_with_offset(player.sword_beams)

            
        # Draw UI
        current_time = pygame.time.get_ticks()
        ult_ready = (current_time - player.last_ultimate_time > player.ultimate_cooldown)
        # Draw Bosses (Custom draw to handle projectiles/health bars scroll)
        for boss in boss_group:
            # Draw Boss Sprite
            offset_pos = (boss.rect.x - scroll_x, boss.rect.y)
            screen.blit(boss.image, offset_pos)
            
            # Draw Bullets
            for b in boss.bullets:
                offset_pos = (b.rect.x - scroll_x, b.rect.y)
                screen.blit(b.image, offset_pos)
                
            # Draw Lasers
            for l in boss.lasers:
                # Lasers might be just a rect?
                l_rect = l.rect.copy()
                l_rect.x -= scroll_x
                screen.blit(l.image, l_rect)
                
            # Draw Boss Health Bar (Floating above head)
            bar_x = boss.rect.x - scroll_x
            bar_y = boss.rect.y - 20
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, boss.rect.width, 10))
            
            # Avoid division by zero
            max_hp = getattr(boss, 'max_health', 40 if boss.is_final else 20)
            
            current_health_width = int(boss.rect.width * (boss.health / max_hp))
            if current_health_width < 0: current_health_width = 0
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_health_width, 10))
            
            # Call UI draw (Global bar)
            ui.draw_boss_health(screen, boss.health, max_hp, boss.is_final)


        # Draw UI
        ui.draw(screen, player.health, player.player_level, current_stage, 
                enemies_killed_this_stage, enemies_needed_per_stage, player.bombs, ult_ready)
        
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
