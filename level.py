import pygame  # Imports the Pygame library
from player import AmmoBox

# from main import ammo_box_group


class Level:  # Creates a Level class
    def __init__(self, level_data):  # Defines the constructor for the Level class
        self.level_data = level_data  # Sets the level data to the provided level data
        self.tile_size = 32
        self.bricks_img = pygame.transform.scale(
            pygame.image.load("assets/bricks.png"),
            (self.tile_size, self.tile_size),
        )
        self.ammo_group = pygame.sprite.Group()
        # Create ammo boxes
        self.create_ammo_boxes()

    def check_collision(self, sprite, x_vel, y_vel):
        """
        Check for collisions with level tiles and resolve them.
        Updates sprite.rect directly.
        """
        sprite.rect.x += x_vel
        
        # Horizontal Collision
        hits = self.get_tile_hits(sprite)
        for tile_rect in hits:
            if x_vel > 0:  # Moving right; Hit left side of tile
                sprite.rect.right = tile_rect.left
            elif x_vel < 0:  # Moving left; Hit right side of tile
                sprite.rect.left = tile_rect.right

        sprite.rect.y += y_vel
        
        # Vertical Collision
        hits = self.get_tile_hits(sprite)
        for tile_rect in hits:
            if y_vel > 0:  # Falling; Hit top of tile
                sprite.rect.bottom = tile_rect.top
                # Stop falling
                if hasattr(sprite, 'velocity_y'):
                    sprite.velocity_y = 0
                    sprite.is_jumping = False
            elif y_vel < 0:  # Jumping; Hit bottom of tile
                sprite.rect.top = tile_rect.bottom
                if hasattr(sprite, 'velocity_y'):
                    sprite.velocity_y = 0

    def get_tile_hits(self, sprite):
        """Return a list of rects for tiles colliding with the sprite"""
        hits = []
        # Calculate grid range to check (optimization)
        start_col = max(0, sprite.rect.left // self.tile_size)
        end_col = min(len(self.level_data[0]), (sprite.rect.right // self.tile_size) + 1)
        start_row = max(0, sprite.rect.top // self.tile_size)
        end_row = min(len(self.level_data), (sprite.rect.bottom // self.tile_size) + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.level_data[row][col]
                if tile_type in (1, 2):  # Solid blocks
                    tile_rect = pygame.Rect(
                        col * self.tile_size, 
                        row * self.tile_size, 
                        self.tile_size, 
                        self.tile_size
                    )
                    if sprite.rect.colliderect(tile_rect):
                        hits.append(tile_rect)
        return hits

    def create_ammo_boxes(self):
        for row_index, row in enumerate(self.level_data):
            for col_index, tile in enumerate(row):
                if tile == 3:
                    ammo_box = AmmoBox(
                        col_index * self.tile_size, row_index * self.tile_size
                    )
                    self.ammo_group.add(ammo_box)
                    # clear the tile so we don't draw it or spawn it again
                    self.level_data[row_index][col_index] = 0

    def draw(self, screen):  # Defines a method to draw the level on the screen
        for row_index, row in enumerate(
            self.level_data
        ):  # Loops through each row in the level data
            for col_index, tile in enumerate(row):  # Loops through each tile in the row
                if tile == 1:  # Checks if the tile is a ground tile (represented by 1)
                    position = (
                        col_index * self.tile_size,
                        row_index * self.tile_size,
                    )
                    screen.blit(self.bricks_img, position)
                elif tile == 2:  # Sky block
                    pygame.draw.rect(
                        screen,
                        (0, 0, 255),
                        (
                            col_index * self.tile_size,
                            row_index * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        ),
                    )
        self.ammo_group.draw(screen)


# create empty level matrix
row = 29
col = 45
level_data = []
for i in range(row):
    col_data = []
    for j in range(col):
        col_data.append(0)
    level_data.append(col_data)


def change_level_data(level_data, row, col, value, count):
    """
    Changes a row of level_data, starting at column y, to the given value,
    for a specified count of columns.

    Args:
        level_data (list of lists): The 2D list representing the level data.
        x (int): The row index to modify.
        y (int): The starting column index to modify.
        value: The value to assign to the specified cells.
        count (int): The number of columns to modify.
    """
    if 0 <= row < len(level_data):
        for i in range(count):
            if 0 <= col + i < len(level_data[row]):
                level_data[row][col + i] = value
    return level_data


level_data = change_level_data(level_data, 18, 5, 1, 5)
level_data = change_level_data(level_data, 16, 12, 1, 5)
level_data = change_level_data(level_data, 14, 18, 1, 10)

level_data = change_level_data(level_data, 13, 28, 1, 1)
level_data = change_level_data(level_data, 12, 28, 1, 1)
level_data = change_level_data(level_data, 11, 28, 1, 1)
level_data = change_level_data(level_data, 10, 28, 1, 1)
level_data = change_level_data(level_data, 9, 28, 1, 1)

level_data = change_level_data(level_data, 9, 18, 1, 10)
level_data = change_level_data(level_data, 8, 22, 3, 1)

# Add a floor at the bottom
level_data = change_level_data(level_data, 25, 0, 1, 45)
