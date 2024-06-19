import pygame
import random
import os

# Setup
w = 500
h = 554
pygame.init()
pygame.display.set_icon(pygame.image.load("9.png"))
pygame.display.set_caption('Minesweeper')
screen = pygame.display.set_mode((w, h))
time = pygame.time.Clock()
running = True
settings_mode = False  

# Variables
map_x = 10
map_y = 10
cell_size = 50
offset = 54
mines_amount = 15
difficulty = 1
size = 1

# Load imgs
blank = pygame.image.load("blank.png")
flag = pygame.image.load("flag.png")
xmark = pygame.image.load("xmark.png")
win = pygame.image.load("win.png")
lose = pygame.image.load("lose.png")
idle = pygame.image.load("idle.png")
settings_img = pygame.image.load("settings.png")  
exit_img = pygame.image.load("exit.png") 
logo = pygame.image.load("logo.png")
img_easy = pygame.image.load("easy.png")
img_normal = pygame.image.load("normal.png")
img_hard = pygame.image.load("hard.png")
img_small = pygame.image.load("small.png")
img_medium = pygame.image.load("medium.png")
img_big = pygame.image.load("big.png")

file_names = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "8.png", "9.png"]
nums = {}
files = ""
for i, file_name in enumerate(file_names, start=1):
    image_path = os.path.join(files, file_name)
    nums[i] = pygame.image.load(image_path)

# Map generation
game_map = [[0] * map_x for _ in range(map_y)]

def gen_map():
    global game_map
    game_map = [[0] * map_x for _ in range(map_y)]
    # Generation of mines
    mine = 0
    while mine < mines_amount:
        x = random.randint(0, map_x - 1)
        y = random.randint(0, map_y - 1)
        if game_map[x][y] == 9:
            continue
        game_map[x][y] = 9
        mine += 1
    
    # Mines bordering
    for x in range(map_x):
        for y in range(map_y):
            if game_map[x][y] == 9:
                for m in range(-1, 2):
                    for n in range(-1, 2):
                        if 0 <= x + m < map_x and 0 <= y + n < map_y and game_map[x + m][y + n] != 9:
                            game_map[x + m][y + n] += 1
    return game_map

game_map = gen_map()

# Dfs 1
def group_cells(game_map):
    visited = [[False] * map_x for _ in range(map_y)]
    group_id = 1
    grouped_cells = [[0] * map_x for _ in range(map_y)]
    
    def dfs(x, y, group_id):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not visited[cx][cy] and game_map[cx][cy] == 0:
                visited[cx][cy] = True
                grouped_cells[cx][cy] = group_id
                for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = cx + mx, cy + my
                    if 0 <= nx < map_x and 0 <= ny < map_y and not visited[nx][ny] and game_map[nx][ny] == 0:
                        stack.append((nx, ny))
    
    for x in range(map_x):
        for y in range(map_y):
            if game_map[x][y] == 0 and not visited[x][y]:
                dfs(x, y, group_id)
                group_id += 1
    
    return grouped_cells, group_id

grouped_cells, group_id = group_cells(game_map)

# Dfs 2
revealed_map = [[False] * map_x for _ in range(map_y)]
flags = [[False] * map_x for _ in range(map_y)]

def reveal_group(grouped_cells, group_id):
    to_reveal = set()
    for x in range(map_x):
        for y in range(map_y):
            if grouped_cells[x][y] == group_id:
                to_reveal.add((x, y))
                for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = x + mx, y + my
                    if 0 <= nx < map_x and 0 <= ny < map_y:
                        to_reveal.add((nx, ny))
    for (x, y) in to_reveal:
        revealed_map[x][y] = True

# Cells logic
def cells_logic():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    
    flags_placed = sum(sum(1 for cell in row if cell) for row in flags)

    # If revealed
    for x in range(map_x):
        for y in range(map_y):
            if not revealed_map[x][y]:
                pygame.draw.rect(screen, "gray", (x * cell_size, y * cell_size + offset, cell_size, cell_size))
            else:
                screen.blit(blank, (x * cell_size, y * cell_size + offset))

    # Board
    for x in range(map_x):
        for y in range(map_y):
            pygame.draw.rect(screen, "black", (x * cell_size, y * cell_size + offset, cell_size, cell_size), 1)

    # LMB logic
    if mouse_click[0]:
        for x in range(map_x):
            for y in range(map_y):
                if not revealed_map[x][y] and cell_size * x < mouse_x < cell_size * x + cell_size and cell_size * y + offset < mouse_y < cell_size * y + offset + cell_size and not flags[x][y]:
                    if game_map[x][y] == 9:
                        for ax in range(map_x):
                            for ay in range(map_y):
                                revealed_map[ax][ay] = True
                    elif grouped_cells[x][y] != 0:
                        reveal_group(grouped_cells, grouped_cells[x][y])
                    else:
                        revealed_map[x][y] = True
    
    # RMB logic
    elif mouse_click[2]:
        for x in range(map_x):
            for y in range(map_y):
                if cell_size * x < mouse_x < cell_size * x + cell_size and cell_size * y + offset < mouse_y < cell_size * y + offset + cell_size and not revealed_map[x][y]:
                    if flags_placed == mines_amount:
                        if flags[x][y]:
                            flags[x][y] = False
                            flags_placed -= 1
                            pygame.time.wait(150)
                    else:
                        flags[x][y] = not flags[x][y]
                        if flags[x][y]:
                            flags_placed += 1
                        else:
                            flags_placed -= 1
                        pygame.time.wait(150)

# Main code loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_click = pygame.mouse.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    win_lose_idle = idle

    if not settings_mode:
        pygame.display.set_caption('Minesweeper')

        # Game drawing
        screen.fill("gray")  
        for x in range(map_x):
            for y in range(map_y):
                if not revealed_map[x][y]:
                    pygame.draw.rect(screen, "gray", (x * cell_size, y * cell_size + offset, cell_size, cell_size))
                else:
                    screen.blit(blank, (x * cell_size, y * cell_size + offset))

                pygame.draw.rect(screen, "black", (x * cell_size, y * cell_size + offset, cell_size, cell_size), 1)

        cells_logic() 

        # Nums display
        for x in range(map_x):
            for y in range(map_y):
                if revealed_map[x][y]:
                    if game_map[x][y] in nums:
                        screen.blit(nums[game_map[x][y]], (x * cell_size, y * cell_size + offset))

        # Flags
        for x in range(map_x):
            for y in range(map_y):
                if flags[x][y]:
                    screen.blit(flag, (x * cell_size, y * cell_size + offset))

        # if game lost
        if all(revealed_map[x][y] for x in range(map_x) for y in range(map_y)):
            win_lose_idle = lose
            for x in range(map_x): 
                for y in range(map_y):
                    if game_map[x][y] != 9 and flags[x][y]:
                        screen.blit(xmark, (x * cell_size, y * cell_size + offset))

        # if win
        if sum(sum(1 for cell in row if cell) for row in flags) == mines_amount:
            win_lose_idle = win

        # New Game
        screen.blit(win_lose_idle, (w/2 - 25, 2)) 
        if mouse_click[0] and mouse_x > w/2 - 25 and mouse_x < w/2 + 25 and mouse_y > 2 and mouse_y < 52:
            revealed_map = [[False] * map_x for _ in range(map_y)]
            flags = [[False] * map_x for _ in range(map_y)]
            game_map = gen_map()
            grouped_cells, group_id = group_cells(game_map)  

        # Settings
        screen.blit(settings_img, (w - 52, 2))
        if mouse_click[0] and mouse_x > w - 52 and mouse_x < w and mouse_y > 2 and mouse_y < 52:
            settings_mode = True

        # Exit
        screen.blit(exit_img, (2, 2))
        if mouse_click[0] and mouse_x > 2 and mouse_x < 52 and mouse_y > 2 and mouse_y < 52:
            running = False

    elif settings_mode:
        pygame.display.set_caption('Minesweeper - settings')
        pygame.display.set_mode((500, 554))
        screen.fill("gray")
        screen.blit(logo, (3, 3))

        screen.blit(img_small, (30, 103 + 50))
        screen.blit(img_medium, (30, 203 + 50))
        screen.blit(img_big, (30, 303 + 50))

        screen.blit(img_easy, (w - 200 - 30, 103 + 50))
        screen.blit(img_normal, (w - 200 - 30, 203 + 50))
        screen.blit(img_hard, (w - 200 - 30, 303 + 50))

        if mouse_click[0]:
            if 30 < mouse_x < 230:
                if 153 < mouse_y < 193:
                    size = 0
                elif 253 < mouse_y < 293:
                    size = 1
                elif 353 < mouse_y < 393:
                    size = 2
            elif w - 230 < mouse_x < w - 30:
                if 153 < mouse_y < 193:
                    difficulty = 0
                elif 253 < mouse_y < 293:
                    difficulty = 1
                elif 353 < mouse_y < 393:
                    difficulty = 2

        #if size == 0:
        #    pygame.draw.rect()


    pygame.display.flip()
    time.tick(60)

pygame.quit()
