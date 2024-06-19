import pygame
import random

# Setup
w = 500
h = 554
caption = "Minesweeper"
pygame.init()
pygame.display.set_icon(pygame.image.load("9.png"))
screen = pygame.display.set_mode((w, h))
time = pygame.time.Clock()
running = True
settings_mode = True

# Variables
difficulty = 0
size = 0

map_size = [10, 20, 30]
cell_size = 50
offset = 54

caption_size = ["small", "medium", "big"]
caption_diff = ["easy", "normal", "hard"]

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
play = pygame.image.load("play.png")

file_names = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "8.png", "9.png"]
nums = {i: pygame.image.load(file_name) for i, file_name in enumerate(file_names, start=1)}

# Map generation
def gen_map():
    global game_map, mines_count
    game_map = [[0] * map_size[size] for _ in range(map_size[size])]
    mines_count = int((map_size[size] ** 2) * [0.1, 0.15, 0.3][difficulty])
    mines_placed = 0

    while mines_placed < mines_count:
        x = random.randint(0, map_size[size] - 1)
        y = random.randint(0, map_size[size] - 1)
        if game_map[x][y] == 9:
            continue
        game_map[x][y] = 9
        mines_placed += 1

    for x in range(map_size[size]):
        for y in range(map_size[size]):
            if game_map[x][y] == 9:
                for m in range(-1, 2):
                    for n in range(-1, 2):
                        if 0 <= x + m < map_size[size] and 0 <= y + n < map_size[size] and game_map[x + m][y + n] != 9:
                            game_map[x + m][y + n] += 1

    return game_map

def reset_game():
    global game_map, grouped_cells, group_id, revealed_map, flags
    game_map = gen_map()
    grouped_cells, group_id = group_cells(game_map)
    revealed_map = [[False] * map_size[size] for _ in range(map_size[size])]
    flags = [[False] * map_size[size] for _ in range(map_size[size])]

game_map = gen_map()

# Dfs 1
def group_cells(game_map):
    visited = [[False] * map_size[size] for _ in range(map_size[size])]
    group_id = 1
    grouped_cells = [[0] * map_size[size] for _ in range(map_size[size])]

    def dfs(x, y, group_id):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not visited[cx][cy] and game_map[cx][cy] == 0:
                visited[cx][cy] = True
                grouped_cells[cx][cy] = group_id
                for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = cx + mx, cy + my
                    if 0 <= nx < map_size[size] and 0 <= ny < map_size[size] and not visited[nx][ny] and game_map[nx][ny] == 0:
                        stack.append((nx, ny))

    for x in range(map_size[size]):
        for y in range(map_size[size]):
            if game_map[x][y] == 0 and not visited[x][y]:
                dfs(x, y, group_id)
                group_id += 1

    return grouped_cells, group_id

grouped_cells, group_id = group_cells(game_map)

# Dfs 2
revealed_map = [[False] * map_size[size] for _ in range(map_size[size])]
flags = [[False] * map_size[size] for _ in range(map_size[size])]

def reveal_group(grouped_cells, group_id):
    to_reveal = set()
    for x in range(map_size[size]):
        for y in range(map_size[size]):
            if grouped_cells[x][y] == group_id:
                to_reveal.add((x, y))
                for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = x + mx, y + my
                    if 0 <= nx < map_size[size] and 0 <= ny < map_size[size]:
                        to_reveal.add((nx, ny))
    for (x, y) in to_reveal:
        revealed_map[x][y] = True

# Cells logic
def cells_logic():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    flags_placed = sum(sum(1 for cell in row if cell) for row in flags)

    for x in range(map_size[size]):
        for y in range(map_size[size]):
            if not revealed_map[x][y]:
                pygame.draw.rect(screen, "gray", (x * cell_size, y * cell_size + offset, cell_size, cell_size))
            else:
                screen.blit(blank, (x * cell_size, y * cell_size + offset))

    for x in range(map_size[size]):
        for y in range(map_size[size]):
            pygame.draw.rect(screen, "black", (x * cell_size, y * cell_size + offset, cell_size, cell_size), 1)

    if mouse_click[0]:
        for x in range(map_size[size]):
            for y in range(map_size[size]):
                if not revealed_map[x][y] and cell_size * x < mouse_x < cell_size * x + cell_size and cell_size * y + offset < mouse_y < cell_size * y + offset + cell_size and not flags[x][y]:
                    if game_map[x][y] == 9:
                        for ax in range(map_size[size]):
                            for ay in range(map_size[size]):
                                revealed_map[ax][ay] = True
                    elif grouped_cells[x][y] != 0:
                        reveal_group(grouped_cells, grouped_cells[x][y])
                    else:
                        revealed_map[x][y] = True

    elif mouse_click[2]:
        for x in range(map_size[size]):
            for y in range(map_size[size]):
                if cell_size * x < mouse_x < cell_size * x + cell_size and cell_size * y + offset < mouse_y < cell_size * y + offset + cell_size and not revealed_map[x][y]:
                    if flags[x][y]:
                        flags[x][y] = False
                    else:
                        if flags_placed < mines_count:
                            flags[x][y] = True
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
        pygame.display.set_caption(caption + " - " + caption_size[size] + ", " + caption_diff[difficulty])

        screen.fill("gray")
        for x in range(map_size[size]):
            for y in range(map_size[size]):
                if not revealed_map[x][y]:
                    pygame.draw.rect(screen, "gray", (x * cell_size, y * cell_size + offset, cell_size, cell_size))
                else:
                    screen.blit(blank, (x * cell_size, y * cell_size + offset))

                pygame.draw.rect(screen, "black", (x * cell_size, y * cell_size + offset, cell_size, cell_size), 1)

        cells_logic()

        for x in range(map_size[size]):
            for y in range(map_size[size]):
                if revealed_map[x][y]:
                    if game_map[x][y] in nums:
                        screen.blit(nums[game_map[x][y]], (x * cell_size, y * cell_size + offset))

        for x in range(map_size[size]):
            for y in range(map_size[size]):
                if flags[x][y]:
                    screen.blit(flag, (x * cell_size, y * cell_size + offset))

        if all(game_map[x][y] == 9 or revealed_map[x][y] for x in range(map_size[size]) for y in range(map_size[size])) and all(
            (game_map[x][y] != 9 or flags[x][y]) for x in range(map_size[size]) for y in range(map_size[size])
        ):
            win_lose_idle = win

        if any(game_map[x][y] == 9 and revealed_map[x][y] for x in range(map_size[size]) for y in range(map_size[size])):
            win_lose_idle = lose

        screen.blit(win_lose_idle, (w / 2 - 25, 2))
        if mouse_click[0] and w / 2 - 25 < mouse_x < w / 2 + 25 and 2 < mouse_y < 52:
            reset_game()

        screen.blit(settings_img, (w - 52, 2))
        if mouse_click[0] and w - 52 < mouse_x < w and 2 < mouse_y < 52:
            settings_mode = True

        screen.blit(exit_img, (2, 2))
        if mouse_click[0] and 2 < mouse_x < 52 and 2 < mouse_y < 52:
            running = False

    elif settings_mode:
        pygame.display.set_caption('Minesweeper - settings')
        pygame.display.set_mode((500, 554))
        screen.fill("gray")
        screen.blit(logo, (3, 3))

        screen.blit(img_small, (30, 153))
        screen.blit(img_medium, (30, 253))
        screen.blit(img_big, (30, 353))

        screen.blit(img_easy, (w - 230, 153))
        screen.blit(img_normal, (w - 230, 253))
        screen.blit(img_hard, (w - 230, 353))

        screen.blit(play, (w / 2 - 100, 453))

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
            if w / 2 - 100 < mouse_x < w / 2 + 100 and 453 < mouse_y < 493:
                reset_game()
                settings_mode = False
                pygame.time.wait(150)

        if size == 0:
            pygame.draw.rect(screen, "black", (25, 148, 210, 50), 4)
        elif size == 1:
            pygame.draw.rect(screen, "black", (25, 248, 210, 50), 4)
        elif size == 2:
            pygame.draw.rect(screen, "black", (25, 348, 210, 50), 4)

        if difficulty == 0:
            pygame.draw.rect(screen, "black", (w - 235, 148, 210, 50), 4)
        elif difficulty == 1:
            pygame.draw.rect(screen, "black", (w - 235, 248, 210, 50), 4)
        elif difficulty == 2:
            pygame.draw.rect(screen, "black", (w - 235, 348, 210, 50), 4)

    pygame.display.flip()
    time.tick(60)

pygame.quit()