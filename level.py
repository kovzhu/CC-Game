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
        # rect = self.bricks_img.get_rect()
        # print(rect.height, rect.width)

    def check_collision(self, player_rect):
        """Check if player is colliding with any blocks"""
        # Convert player rect to grid coordinates
        left = player_rect.left // self.tile_size
        right = player_rect.right // self.tile_size
        bottom = player_rect.bottom // self.tile_size
        top = player_rect.top // self.tile_size

        # Check if any blocks below player are solid
        if bottom < len(self.level_data):
            for x in range(left, right + 1):
                if x < len(self.level_data[bottom]):
                    if self.level_data[bottom][x] in (1, 2):  # Ground or sky block
                        print(f"Collision detected at x={x}, bottom={bottom}")
                        # Adjust player position to stand on the block
                        player_rect.bottom = bottom * self.tile_size
                        return True

        # Check if any blocks above player are solid
        if top >= 0:
            for x in range(left, right + 1):
                if x < len(self.level_data[top]):
                    if self.level_data[top][x] in (1, 2):  # Ground or sky block
                        print(f"Collision detected at x={x}, top={top}")
                        return True
        return False

    def draw(self, screen):  # Defines a method to draw the level on the screen
        for row_index, row in enumerate(
            self.level_data
        ):  # Loops through each row in the level data
            for col_index, tile in enumerate(row):  # Loops through each tile in the row
                if tile == 1:  # Checks if the tile is a ground tile (represented by 1)
                    # Draw a ground tile
                    # pygame.draw.rect(  # Draws a rectangle on the screen
                    #     screen,
                    #     (0, 255, 0),
                    #     (
                    #         col_index * 32,
                    #         row_index * 32,
                    #         32,
                    #         32,
                    #     ),  # Specifies the screen, color, position, and size of the rectangle
                    # )
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
                elif tile == 3:  # ammo box
                    ammo_box = AmmoBox(
                        col_index * self.tile_size, row_index * self.tile_size
                    )
                    self.ammo_group.add(ammo_box)
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
            if 0 <= col + i < len(level_data[col]):
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
