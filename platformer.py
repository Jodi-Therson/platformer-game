import pygame
import json
import os # Import the os module to check for file existence

# --- Initialization ---
pygame.init()

# --- Constants ---
# Adjust screen width back to not include the UI panel
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_SIZE = 40
FPS = 60
START_LEVEL = 1 # Change this to start on a different level

# --- Colors (Copied from editor) ---
WHITE = (255, 255, 255)
PLAYER_COLOR = (255, 132, 124) # Fallback color for the player if sprite is missing
PALETTE_1 = (218, 210, 216)
PALETTE_2 = (189, 200, 230)
PALETTE_3 = (154, 152, 193)
PALETTE_4 = (106, 103, 159) # Background
PALETTE_5 = (46, 47, 82)
COLOR_1 = (255, 132, 124)
COLOR_2 = (255, 220, 123)
COLOR_3 = (147, 223, 118)
COLOR_4 = (118, 185, 223)
COLOR_5 = (180, 147, 223)

# Tile Color Mapping
TILE_COLORS = {
    1: PALETTE_2,
    2: PALETTE_3,
    3: COLOR_1,
    4: COLOR_2,
    5: COLOR_3,
    6: COLOR_4,
    7: COLOR_5
}

# --- Game Window ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer Game')
clock = pygame.time.Clock()


# --- Player Class ---
class Player:
    def __init__(self, x, y):
        """Initializes the player."""
        self.start_x = x # Store start position for reset
        self.start_y = y
        
        # --- Load Player Sprite ---
        try:
            self.image = pygame.image.load('character_sprite.png').convert_alpha()
        except FileNotFoundError:
            print("Warning: 'character_sprite.png' not found. Using a fallback color rect.")
            # Create a fallback surface if the image doesn't exist
            self.image = pygame.Surface((40, 40))
            self.image.fill(PLAYER_COLOR)
            
        self.rect = self.image.get_rect(topleft=(self.start_x, self.start_y))
        
        # --- Physics and Movement Attributes ---
        self.vel_y = 0
        self.speed = 7
        self.jump_power = -18
        self.gravity = 0.8
        self.on_ground = False

    def reset(self):
        """Resets the player to their starting position."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_y = 0
        self.on_ground = False
        print("Player died and has been reset.")

    def update(self, world):
        """Handles player logic including movement, gravity, and collisions."""
        dx = 0
        dy = 0

        # --- Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # --- Gravity ---
        self.vel_y += self.gravity
        if self.vel_y > 15: # Terminal velocity
            self.vel_y = 15
        dy += self.vel_y

        # --- Collision Detection ---
        self.on_ground = False # Assume not on ground until a collision proves otherwise
        for tile in world.tile_rects:
            # Check for collision in x-direction
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Check for collision in y-direction
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # Check if below the ground (jumping up)
                if self.vel_y < 0:
                    dy = tile.bottom - self.rect.top
                    self.vel_y = 0
                # Check if above the ground (falling down)
                elif self.vel_y >= 0:
                    dy = tile.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True # Player is on the ground

        # Update player position
        self.rect.x += dx
        self.rect.y += dy
        
        # --- World Boundary Collisions ---
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > world.world_pixel_width:
            self.rect.right = world.world_pixel_width
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0 # Stop upward velocity if hitting the top
        
        # --- Death Condition ---
        # Check if player has fallen off the bottom of the world
        if self.rect.bottom > world.world_pixel_height:
            self.reset()
    
    def draw(self, surface, camera_offset):
        """Draws the player relative to the camera."""
        # The player's draw position is offset by the camera's position
        draw_pos_x = self.rect.x - camera_offset.x
        draw_pos_y = self.rect.y - camera_offset.y
        # Use blit to draw the image instead of a rect
        surface.blit(self.image, (draw_pos_x, draw_pos_y))


# --- World Class ---
class World:
    def __init__(self, level_num):
        """Loads and prepares the level."""
        self.tile_rects = []
        self.world_data = []
        self.world_pixel_width = 0
        self.world_pixel_height = 0
        
        level_file = f'level_{level_num}.json'
        try:
            with open(level_file, 'r') as file:
                self.world_data = json.load(file)
            
            # Calculate world dimensions
            if self.world_data:
                self.world_pixel_height = len(self.world_data) * GRID_SIZE
                self.world_pixel_width = len(self.world_data[0]) * GRID_SIZE
            
            # Create collision rectangles from the loaded data
            for y, row in enumerate(self.world_data):
                for x, tile_value in enumerate(row):
                    if tile_value > 0:
                        self.tile_rects.append(pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        except FileNotFoundError:
            print(f"Error: Could not load {level_file}. Make sure you have saved it in the editor.")
            # Create a floor so the player doesn't fall forever
            for i in range(50):
                self.tile_rects.append(pygame.Rect(i * GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE, GRID_SIZE))
            self.world_pixel_width = 50 * GRID_SIZE
            self.world_pixel_height = SCREEN_HEIGHT


    def draw(self, surface, camera_offset):
        """Draws the world tiles relative to the camera."""
        for y, row in enumerate(self.world_data):
            for x, tile_value in enumerate(row):
                if tile_value > 0:
                    tile_color = TILE_COLORS.get(tile_value, PALETTE_2)
                    tile_rect = pygame.Rect(x * GRID_SIZE - camera_offset.x, y * GRID_SIZE - camera_offset.y, GRID_SIZE, GRID_SIZE)
                    # Simple culling: only draw tiles that are on screen
                    if -GRID_SIZE < tile_rect.x < SCREEN_WIDTH and -GRID_SIZE < tile_rect.y < SCREEN_HEIGHT:
                        pygame.draw.rect(surface, tile_color, tile_rect)


def main():
    """Main game function."""
    # --- Setup ---
    world = World(START_LEVEL)
    player = Player(100, SCREEN_HEIGHT - 200)
    camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    # --- Game Loop ---
    run = True
    while run:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # --- Update ---
        player.update(world)

        # --- Camera Follow with Dead Zone ---
        # The camera only moves when the player gets near the edge of the screen.
        dead_zone_left = SCREEN_WIDTH * 0.3
        dead_zone_right = SCREEN_WIDTH * 0.7
        dead_zone_top = SCREEN_HEIGHT * 0.3
        dead_zone_bottom = SCREEN_HEIGHT * 0.7

        player_screen_pos_x = player.rect.x - camera.x
        player_screen_pos_y = player.rect.y - camera.y

        if player_screen_pos_x < dead_zone_left:
            camera.x = player.rect.x - dead_zone_left
        if player_screen_pos_x + player.rect.width > dead_zone_right:
            camera.x = player.rect.x + player.rect.width - dead_zone_right
        
        if player_screen_pos_y < dead_zone_top:
            camera.y = player.rect.y - dead_zone_top
        if player_screen_pos_y + player.rect.height > dead_zone_bottom:
            camera.y = player.rect.y + player.rect.height - dead_zone_bottom
        
        # Clamp camera to world bounds
        if camera.left < 0:
            camera.left = 0
        if camera.top < 0:
            camera.top = 0
        if camera.right > world.world_pixel_width:
            camera.right = world.world_pixel_width
        if camera.bottom > world.world_pixel_height:
            camera.bottom = world.world_pixel_height
        
        # --- Drawing ---
        screen.fill(PALETTE_4)
        
        camera_offset = pygame.Vector2(camera.x, camera.y)
        world.draw(screen, camera_offset)
        player.draw(screen, camera_offset)

        # --- Display Update ---
        pygame.display.update()
        clock.tick(FPS)

    # --- Quit ---
    pygame.quit()


if __name__ == '__main__':
    main()
