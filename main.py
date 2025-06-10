import pygame
import json
import os

# --- Initialization ---
pygame.init()

# --- Directory Setup ---
# Define directory paths and create them if they don't exist
LEVELS_DIR = 'levels'
CHARACTERS_DIR = 'characters'

if not os.path.exists(LEVELS_DIR):
    os.makedirs(LEVELS_DIR)
if not os.path.exists(CHARACTERS_DIR):
    os.makedirs(CHARACTERS_DIR)


# --- Constants ---
UI_WIDTH = 320 # Increased UI width for more colors
SCREEN_WIDTH = 1280 + UI_WIDTH
SCREEN_HEIGHT = 720
GRID_SIZE = 40 # Size of tiles in the level editor
FPS = 60

# Character Editor Grid Dimensions
CHAR_GRID_DIM = 40 # 40x40 grid for the character sprite
CHAR_GRID_CELL_SIZE = 18 # The display size of each cell in the character grid to fit on screen

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
# Level Editor Palette
LEVEL_PALETTE_1 = (218, 210, 216)
LEVEL_PALETTE_2 = (189, 200, 230)
LEVEL_PALETTE_3 = (154, 152, 193)
LEVEL_PALETTE_4 = (106, 103, 159)
LEVEL_PALETTE_5 = (46, 47, 82)
LEVEL_COLOR_1 = (255, 132, 124)
LEVEL_COLOR_2 = (255, 220, 123)
LEVEL_COLOR_3 = (147, 223, 118)
LEVEL_COLOR_4 = (118, 185, 223)
LEVEL_COLOR_5 = (180, 147, 223)

# Expanded Character Editor Palette
CHAR_COLORS = {
    1: (255, 0, 0), 2: (0, 255, 0), 3: (0, 0, 255), 4: (255, 255, 0), 5: (0, 255, 255),
    6: (255, 0, 255), 7: (255, 128, 0), 8: (128, 0, 255), 9: (0, 128, 0), 10: (255, 255, 255),
    11: (128, 128, 128), 12: (0, 0, 0), 13: (139, 69, 19), 14: (244, 164, 96), 15: (255, 215, 0)
}

LEVEL_TILE_COLORS = { 1: LEVEL_PALETTE_2, 2: LEVEL_PALETTE_3, 3: LEVEL_COLOR_1, 4: LEVEL_COLOR_2, 5: LEVEL_COLOR_3, 6: LEVEL_COLOR_4, 7: LEVEL_COLOR_5 }

# --- Fonts ---
title_font = pygame.font.SysFont('Arial', 60, bold=True)
button_font = pygame.font.SysFont('Arial', 24, bold=True)
ui_font = pygame.font.SysFont('Arial', 30, bold=True)
small_font = pygame.font.SysFont('Arial', 20)

# --- Game Window ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# --- Game State ---
game_mode = 'main_menu' # 'main_menu', 'level_editor', 'char_editor'
current_level = 1

# --- Level Editor State ---
level_world_data = []
level_num_rows = (SCREEN_HEIGHT * 2) // GRID_SIZE
level_num_cols = (1280 * 2) // GRID_SIZE
camera = pygame.Rect(0, 0, 1280, SCREEN_HEIGHT)
camera_speed = 15
level_selected_tile = 1

# --- Character Editor State ---
char_grid_data = [[0] * CHAR_GRID_DIM for _ in range(CHAR_GRID_DIM)]
char_selected_color = 1
char_input_active = False
char_filename = ""
char_feedback_msg = ""
char_feedback_timer = 0


# --- UI Elements ---
# Main Menu Buttons
level_editor_button = pygame.Rect((SCREEN_WIDTH / 2) - 200, 300, 400, 80)
char_editor_button = pygame.Rect((SCREEN_WIDTH / 2) - 200, 400, 400, 80)

# Level Editor Buttons
lvl_reset_button = pygame.Rect(1280 + 20, SCREEN_HEIGHT - 70, UI_WIDTH - 40, 50)
lvl_save_button = pygame.Rect(lvl_reset_button.left, lvl_reset_button.top - 60, lvl_reset_button.width, 50)
lvl_menu_button = pygame.Rect(lvl_save_button.left, lvl_save_button.top - 60, lvl_save_button.width, 50)
lvl_color_buttons = [pygame.Rect(1280 + 20 + ((i % 4) * (50 + 15)), 80 + 20 + ((i // 4) * (50 + 15)), 50, 50) for i in range(len(LEVEL_TILE_COLORS))]

# Character Editor Buttons
char_menu_button = pygame.Rect(1280 + 20, SCREEN_HEIGHT - 70, UI_WIDTH - 40, 50)
char_export_button = pygame.Rect(char_menu_button.left, char_menu_button.top - 60, char_menu_button.width, 50)
char_clear_button = pygame.Rect(char_export_button.left, char_export_button.top - 60, char_export_button.width, 50)
char_color_buttons = [pygame.Rect(1280 + 20 + ((i % 4) * (50 + 15)), 80 + 20 + ((i // 4) * (50 + 15)), 50, 50) for i in range(len(CHAR_COLORS))]
char_filename_input_rect = pygame.Rect(char_clear_button.left, char_clear_button.top - 60, char_clear_button.width, 50)


def load_level_data(level_num):
    global level_world_data, current_level
    current_level = level_num
    level_file_path = os.path.join(LEVELS_DIR, f'level_{current_level}.json')
    try:
        with open(level_file_path, 'r') as file:
            level_world_data = json.load(file)
    except FileNotFoundError:
        level_world_data = [[0] * level_num_cols for _ in range(level_num_rows)]
    pygame.display.set_caption(f'Level Editor - Level {current_level}')
    camera.topleft = (0, 0)

# --- Drawing Functions ---
def draw_main_menu():
    screen.fill(LEVEL_PALETTE_4)
    title_text = title_font.render('GAME EDITOR SUITE', True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, 150)))
    # Level Editor Button
    pygame.draw.rect(screen, LEVEL_PALETTE_5, level_editor_button)
    pygame.draw.rect(screen, LEVEL_PALETTE_1, level_editor_button, 4)
    lvl_btn_text = ui_font.render('LEVEL EDITOR', True, WHITE)
    screen.blit(lvl_btn_text, lvl_btn_text.get_rect(center=level_editor_button.center))
    # Character Editor Button
    pygame.draw.rect(screen, LEVEL_PALETTE_5, char_editor_button)
    pygame.draw.rect(screen, LEVEL_PALETTE_1, char_editor_button, 4)
    char_btn_text = ui_font.render('CHARACTER EDITOR', True, WHITE)
    screen.blit(char_btn_text, char_btn_text.get_rect(center=char_editor_button.center))

def draw_level_editor():
    # Draw World
    screen.fill(LEVEL_PALETTE_4)
    for y, row in enumerate(level_world_data):
        for x, tile in enumerate(row):
            if tile > 0:
                pygame.draw.rect(screen, LEVEL_TILE_COLORS.get(tile), pygame.Rect(x * GRID_SIZE - camera.x, y * GRID_SIZE - camera.y, GRID_SIZE, GRID_SIZE))
    # Draw Grid
    start_x, start_y = (camera.x // GRID_SIZE) * GRID_SIZE, (camera.y // GRID_SIZE) * GRID_SIZE
    for x in range(int(start_x), int(camera.x) + 1280 + GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, LEVEL_PALETTE_1, (x - camera.x, 0), (x - camera.x, SCREEN_HEIGHT))
    for y in range(int(start_y), int(camera.y) + SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
        pygame.draw.line(screen, LEVEL_PALETTE_1, (0, y - camera.y), (1280, y - camera.y))
    
    # Draw UI
    pygame.draw.rect(screen, LEVEL_PALETTE_5, (1280, 0, UI_WIDTH, SCREEN_HEIGHT))
    level_text = ui_font.render(f'LEVEL: {current_level}', True, WHITE)
    screen.blit(level_text, level_text.get_rect(center=(1280 + UI_WIDTH / 2, 40)))
    # UI Buttons
    for i, btn in enumerate(lvl_color_buttons):
        pygame.draw.rect(screen, LEVEL_TILE_COLORS[i + 1], btn)
        if level_selected_tile == i + 1: pygame.draw.rect(screen, WHITE, btn, 3)
    
    pygame.draw.rect(screen, LEVEL_PALETTE_1, lvl_menu_button); screen.blit(button_font.render('MENU', True, BLACK), button_font.render('MENU', True, BLACK).get_rect(center=lvl_menu_button.center))
    pygame.draw.rect(screen, LEVEL_PALETTE_1, lvl_save_button); screen.blit(button_font.render('SAVE', True, BLACK), button_font.render('SAVE', True, BLACK).get_rect(center=lvl_save_button.center))
    pygame.draw.rect(screen, LEVEL_PALETTE_1, lvl_reset_button); screen.blit(button_font.render('RESET', True, BLACK), button_font.render('RESET', True, BLACK).get_rect(center=lvl_reset_button.center))


def draw_character_editor():
    global char_feedback_msg, char_feedback_timer
    screen.fill(LEVEL_PALETTE_4)
    # Drawing Canvas
    canvas_size = CHAR_GRID_DIM * CHAR_GRID_CELL_SIZE
    canvas_x = (1280 - canvas_size) / 2
    canvas_y = (SCREEN_HEIGHT - canvas_size) / 2
    pygame.draw.rect(screen, GREY, (canvas_x - 5, canvas_y - 5, canvas_size + 10, canvas_size + 10))
    for r_idx, row in enumerate(char_grid_data):
        for c_idx, val in enumerate(row):
            tile_rect = pygame.Rect(canvas_x + c_idx * CHAR_GRID_CELL_SIZE, canvas_y + r_idx * CHAR_GRID_CELL_SIZE, CHAR_GRID_CELL_SIZE, CHAR_GRID_CELL_SIZE)
            if val > 0: pygame.draw.rect(screen, CHAR_COLORS.get(val), tile_rect)
            else: pygame.draw.rect(screen, WHITE, tile_rect) # Empty tiles are white
            pygame.draw.rect(screen, LEVEL_PALETTE_1, tile_rect, 1) # Grid lines
    
    # UI Panel
    pygame.draw.rect(screen, LEVEL_PALETTE_5, (1280, 0, UI_WIDTH, SCREEN_HEIGHT))
    ui_title = ui_font.render('SPRITE EDITOR', True, WHITE)
    screen.blit(ui_title, ui_title.get_rect(center=(1280 + UI_WIDTH/2, 40)))
    # Color Buttons
    for i, btn in enumerate(char_color_buttons):
        pygame.draw.rect(screen, CHAR_COLORS[i + 1], btn)
        if char_selected_color == i + 1: pygame.draw.rect(screen, WHITE, btn, 3)
    
    # Filename Input Box
    pygame.draw.rect(screen, WHITE, char_filename_input_rect)
    if char_input_active:
        pygame.draw.rect(screen, LEVEL_COLOR_1, char_filename_input_rect, 3)
    filename_text = small_font.render(char_filename, True, BLACK)
    screen.blit(filename_text, (char_filename_input_rect.x + 10, char_filename_input_rect.y + 15))
        
    # Action Buttons
    pygame.draw.rect(screen, LEVEL_PALETTE_1, char_menu_button); screen.blit(button_font.render('MENU', True, BLACK), button_font.render('MENU', True, BLACK).get_rect(center=char_menu_button.center))
    pygame.draw.rect(screen, LEVEL_PALETTE_1, char_export_button); screen.blit(button_font.render('EXPORT (.png)', True, BLACK), button_font.render('EXPORT (.png)', True, BLACK).get_rect(center=char_export_button.center))
    pygame.draw.rect(screen, LEVEL_PALETTE_1, char_clear_button); screen.blit(button_font.render('CLEAR', True, BLACK), button_font.render('CLEAR', True, BLACK).get_rect(center=char_clear_button.center))
    
    # Feedback Message
    if char_feedback_timer > 0:
        feedback_text = small_font.render(char_feedback_msg, True, WHITE)
        screen.blit(feedback_text, feedback_text.get_rect(center=(char_filename_input_rect.centerx, char_filename_input_rect.top - 20)))
        char_feedback_timer -= 1


# --- Main Loop ---
run = True
is_drawing, is_erasing = False, False
load_level_data(1) # Initial load

while run:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        
        # --- SHARED KEYDOWN ---
        if event.type == pygame.KEYDOWN:
            if game_mode == 'level_editor':
                if event.key == pygame.K_RSHIFT: load_level_data(current_level + 1)
                elif event.key == pygame.K_LSHIFT and current_level > 1: load_level_data(current_level - 1)
            elif game_mode == 'char_editor' and char_input_active:
                if event.key == pygame.K_BACKSPACE:
                    char_filename = char_filename[:-1]
                else:
                    char_filename += event.unicode
        
        # --- MOUSEUP ---
        if event.type == pygame.MOUSEBUTTONUP:
            is_drawing, is_erasing = False, False
            
        # --- MOUSEDOWN ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # --- Main Menu Logic ---
            if game_mode == 'main_menu':
                if level_editor_button.collidepoint(pos): game_mode = 'level_editor'
                elif char_editor_button.collidepoint(pos): game_mode = 'char_editor'
            
            # --- Level Editor Logic ---
            elif game_mode == 'level_editor':
                if pos[0] >= 1280: # UI click
                    if lvl_menu_button.collidepoint(pos): game_mode = 'main_menu'
                    elif lvl_save_button.collidepoint(pos):
                        level_file_path = os.path.join(LEVELS_DIR, f'level_{current_level}.json')
                        with open(level_file_path, 'w') as f: json.dump(level_world_data, f)
                    elif lvl_reset_button.collidepoint(pos): level_world_data = [[0] * level_num_cols for _ in range(level_num_rows)]
                    else:
                        for i, btn in enumerate(lvl_color_buttons):
                            if btn.collidepoint(pos): level_selected_tile = i + 1
                else: # World click
                    if event.button == 1: is_drawing = True
                    elif event.button == 3: is_erasing = True

            # --- Character Editor Logic ---
            elif game_mode == 'char_editor':
                char_input_active = False # Deactivate by default on any click
                if pos[0] >= 1280: # UI click
                    if char_filename_input_rect.collidepoint(pos):
                        char_input_active = True
                    elif char_menu_button.collidepoint(pos): game_mode = 'main_menu'
                    elif char_clear_button.collidepoint(pos): char_grid_data = [[0] * CHAR_GRID_DIM for _ in range(CHAR_GRID_DIM)]
                    elif char_export_button.collidepoint(pos):
                        if char_filename != "":
                            sprite_surface = pygame.Surface((CHAR_GRID_DIM, CHAR_GRID_DIM), pygame.SRCALPHA)
                            for r, row in enumerate(char_grid_data):
                                for c, val in enumerate(row):
                                    if val > 0:
                                        sprite_surface.set_at((c, r), CHAR_COLORS.get(val))
                            
                            file_path = os.path.join(CHARACTERS_DIR, f'{char_filename}.png')
                            pygame.image.save(sprite_surface, file_path)
                            char_feedback_msg = f"Saved as {file_path}"
                            char_feedback_timer = FPS * 3 # Show message for 3 seconds
                            char_filename = ""
                        else:
                            char_feedback_msg = "Enter filename!"
                            char_feedback_timer = FPS * 3
                    else:
                        for i, btn in enumerate(char_color_buttons):
                            if btn.collidepoint(pos): char_selected_color = i + 1
                else: # Canvas click
                    canvas_size = CHAR_GRID_DIM * CHAR_GRID_CELL_SIZE
                    canvas_x, canvas_y = (1280 - canvas_size) / 2, (SCREEN_HEIGHT - canvas_size) / 2
                    if canvas_x <= pos[0] < canvas_x + canvas_size and canvas_y <= pos[1] < canvas_y + canvas_size:
                        col = int((pos[0] - canvas_x) // CHAR_GRID_CELL_SIZE)
                        row = int((pos[1] - canvas_y) // CHAR_GRID_CELL_SIZE)
                        if event.button == 1:
                            is_drawing = True
                            char_grid_data[row][col] = char_selected_color
                        elif event.button == 3:
                            is_erasing = True
                            char_grid_data[row][col] = 0
    
    # --- Continuous Drawing/Erasing Logic on Drag ---
    if game_mode == 'level_editor' and (is_drawing or is_erasing):
        pos = pygame.mouse.get_pos()
        if pos[0] < 1280:
            world_x, world_y = pos[0] + camera.x, pos[1] + camera.y
            col, row = world_x // GRID_SIZE, world_y // GRID_SIZE
            if 0 <= row < level_num_rows and 0 <= col < level_num_cols:
                level_world_data[row][col] = level_selected_tile if is_drawing else 0
    
    elif game_mode == 'char_editor' and (is_drawing or is_erasing):
        pos = pygame.mouse.get_pos()
        canvas_size = CHAR_GRID_DIM * CHAR_GRID_CELL_SIZE
        canvas_x, canvas_y = (1280 - canvas_size) / 2, (SCREEN_HEIGHT - canvas_size) / 2
        if canvas_x <= pos[0] < canvas_x + canvas_size and canvas_y <= pos[1] < canvas_y + canvas_size:
            col = int((pos[0] - canvas_x) // CHAR_GRID_CELL_SIZE)
            row = int((pos[1] - canvas_y) // CHAR_GRID_CELL_SIZE)
            if 0 <= row < CHAR_GRID_DIM and 0 <= col < CHAR_GRID_DIM:
                char_grid_data[row][col] = char_selected_color if is_drawing else 0

    # --- Camera Movement (Level Editor) ---
    if game_mode == 'level_editor':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if keys[pygame.K_LEFT]: camera.x -= camera_speed
            elif keys[pygame.K_RIGHT]: camera.x += camera_speed
            elif keys[pygame.K_UP]: camera.y -= camera_speed
            elif keys[pygame.K_DOWN]: camera.y += camera_speed
        # Clamp Camera
        camera.left = max(0, camera.left)
        camera.right = min(1280 * 2, camera.right)
        camera.top = max(0, camera.top)
        camera.bottom = min(SCREEN_HEIGHT * 2, camera.bottom)

    # --- Drawing ---
    if game_mode == 'main_menu':
        draw_main_menu()
    elif game_mode == 'level_editor':
        draw_level_editor()
    elif game_mode == 'char_editor':
        draw_character_editor()
    
    pygame.display.update()
    clock.tick(FPS)

# --- Quit ---
pygame.quit()
