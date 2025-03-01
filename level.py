import pygame  # Imports the Pygame library


class Level:  # Creates a Level class
    def __init__(self, level_data):  # Defines the constructor for the Level class
        self.level_data = level_data  # Sets the level data to the provided level data

    def draw(self, screen):  # Defines a method to draw the level on the screen
        for row_index, row in enumerate(
            self.level_data
        ):  # Loops through each row in the level data
            for col_index, tile in enumerate(row):  # Loops through each tile in the row
                if tile == 1:  # Checks if the tile is a ground tile (represented by 1)
                    # Draw a ground tile
                    pygame.draw.rect(  # Draws a rectangle on the screen
                        screen,
                        (0, 255, 0),
                        (
                            col_index * 32,
                            row_index * 32,
                            32,
                            32,
                        ),  # Specifies the screen, color, position, and size of the rectangle
                    )
