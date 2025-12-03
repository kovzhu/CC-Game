import pygame  # Imports the Pygame library
from player import AmmoBox

# from main import ammo_box_group


import random

class Level:  # Creates a Level class
    def __init__(self, level_data=None):  # Defines the constructor for the Level class
        self.tile_size = 32
        if level_data:
            self.level_data = level_data
        else:
            self.level_data = self.generate_random_level()
            
        self.bricks_img = pygame.transform.scale(
            pygame.image.load("assets/bricks.png"),
            (self.tile_size, self.tile_size),
        )
        self.ammo_group = pygame.sprite.Group()
        # Create ammo boxes
        self.create_ammo_boxes()

    def generate_random_level(self):
        rows = 29
        cols = 300  # Long level
        data = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # Helper to set a block
        def set_block(r, c, val):
            if 0 <= r < rows and 0 <= c < cols:
                data[r][c] = val

        # 1. Floor (with gaps)
        current_col = 0
        while current_col < cols:
            # Safe zone at start
            if current_col < 20:
                segment_len = 20
                for i in range(segment_len):
                    set_block(24, current_col + i, 1)
                    set_block(25, current_col + i, 1)
                current_col += segment_len
                continue

            # Random segment type
            segment_type = random.choice(['flat', 'gap', 'platform', 'stairs'])
            segment_len = random.randint(5, 15)
            
            if segment_type == 'flat':
                for i in range(segment_len):
                    set_block(24, current_col + i, 1)
                    set_block(25, current_col + i, 1)
                    # Random obstacle
                    if random.random() < 0.2:
                        set_block(23, current_col + i, 1)
                        if random.random() < 0.5:
                            set_block(22, current_col + i, 1)
            
            elif segment_type == 'gap':
                # Gap length 2 (safe for jumping)
                gap_len = 2
                current_col += gap_len  # Skip blocks (create hole)
                segment_len = 0 # Already advanced
                
            elif segment_type == 'platform':
                # Ground underneath
                for i in range(segment_len):
                    set_block(24, current_col + i, 1)
                    set_block(25, current_col + i, 1)
                
                # Floating platform - lower to be reachable (2-4 blocks up)
                height = random.randint(20, 22)
                for i in range(2, segment_len - 2):
                    set_block(height, current_col + i, 1)
                    if i == segment_len // 2: # Ammo on top
                        set_block(height - 1, current_col + i, 3)

            elif segment_type == 'stairs':
                # Ground underneath
                for i in range(segment_len):
                    set_block(24, current_col + i, 1)
                    set_block(25, current_col + i, 1)
                
                # Stairs up
                stair_height = 23
                for i in range(segment_len):
                    if i % 2 == 0:
                        stair_height -= 1
                    set_block(stair_height, current_col + i, 1)
            
            current_col += segment_len
            
        return data

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

    def draw(self, screen, scroll_x=0):  # Added scroll_x
        # Calculate visible range
        start_col = max(0, int(scroll_x // self.tile_size))
        end_col = start_col + int(pygame.display.get_surface().get_width() // self.tile_size) + 2
        end_col = min(end_col, len(self.level_data[0]))

        for row_index, row in enumerate(self.level_data):
            # Only draw visible columns
            for col_index in range(start_col, end_col):
                tile = row[col_index]
                if tile == 1:
                    position = (
                        col_index * self.tile_size - scroll_x,
                        row_index * self.tile_size,
                    )
                    screen.blit(self.bricks_img, position)
                elif tile == 2:
                    pygame.draw.rect(
                        screen,
                        (0, 0, 255),
                        (
                            col_index * self.tile_size - scroll_x,
                            row_index * self.tile_size,
                            self.tile_size,
                            self.tile_size,
                        ),
                    )
        
        # Draw ammo boxes with scroll offset
        for ammo in self.ammo_group:
            screen.blit(ammo.image, (ammo.rect.x - scroll_x, ammo.rect.y))
    
    def destroy_tiles_in_radius(self, center_x, center_y, radius):
        """Destroy all tiles within a given radius from center point"""
        # Convert pixel coordinates to tile coordinates
        start_col = max(0, int((center_x - radius) // self.tile_size))
        end_col = min(len(self.level_data[0]), int((center_x + radius) // self.tile_size) + 1)
        start_row = max(0, int((center_y - radius) // self.tile_size))
        end_row = min(len(self.level_data), int((center_y + radius) // self.tile_size) + 1)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                # Calculate distance from center
                tile_center_x = col * self.tile_size + self.tile_size / 2
                tile_center_y = row * self.tile_size + self.tile_size / 2
                distance = ((tile_center_x - center_x) ** 2 + (tile_center_y - center_y) ** 2) ** 0.5
                
                if distance <= radius:
                    # Destroy tile (set to 0)
                    if self.level_data[row][col] == 1:  # Only destroy bricks
                        self.level_data[row][col] = 0

