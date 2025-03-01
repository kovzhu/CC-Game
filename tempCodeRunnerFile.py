
    player_group.update()  # Updates the player sprite group
    enemy_group.update()  # Updates the enemy sprite group

    # Clear the screen with background
    screen.blit(background, (0, 0))

    # Draw the level
    # level.draw(screen)  # Draws the level on the screen

    # Draw the player
    player_group.draw(screen)  # Draws the player sprite group on the screen

    # Draw the enemy
    enemy_group.draw(screen)  # Draws the enemy sprite group on the screen

    # Draw the UI
    ui.draw(screen, 0, 3)  # Draws the UI on the screen with score 0 and 3 lives

    # Update the display
    pygame.display.flip()  # Updates the entire screen to the display

# Quit Pygame
pygame.quit()  # Uninitializes all Pygame modules
