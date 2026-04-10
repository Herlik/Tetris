import pygame
import random
import copy

pygame.init()
pygame.key.start_text_input()
pygame.key.set_text_input_rect(pygame.Rect(0, 0, 0, 0))

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PREVIEW_COUNT = 3
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE
PREVIEW_AREA_LEFT = BLOCK_SIZE * (GRID_WIDTH + 2)

SHAPES_WITH_COLORS = [
    ([[1, 1, 1, 1]], CYAN),
    ([[1, 1], [1, 1]], YELLOW),
    ([[1, 1, 1], [0, 1, 0]], PURPLE),
    ([[1, 1, 1], [1, 0, 0]], ORANGE),
    ([[1, 1, 1], [0, 0, 1]], BLUE),
    ([[0, 1, 1], [1, 1, 0]], GREEN),
    ([[1, 1, 0], [0, 1, 1]], RED)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块 - 按R重启（请确保英文输入法）")
clock = pygame.time.Clock()

class Tetris:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500

        self.next_pieces = []
        for _ in range(PREVIEW_COUNT + 1):
            idx = random.randint(0, len(SHAPES_WITH_COLORS) - 1)
            shape, color = SHAPES_WITH_COLORS[idx]
            self.next_pieces.append({"shape": copy.deepcopy(shape), "color": color})

        self.current_piece = self.next_pieces.pop(0)
        self.current_piece["x"] = GRID_WIDTH // 2 - len(self.current_piece["shape"][0]) // 2
        self.current_piece["y"] = 0

        idx = random.randint(0, len(SHAPES_WITH_COLORS) - 1)
        shape, color = SHAPES_WITH_COLORS[idx]
        self.next_pieces.append({"shape": copy.deepcopy(shape), "color": color})

    def valid_move(self, piece, dx=0, dy=0):
        if piece is None:
            return False
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + dx
                    new_y = piece["y"] + y + dy
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def rotate_piece(self):
        if self.game_over:
            return
        old_shape = self.current_piece["shape"]
        rotated = [list(row) for row in zip(*old_shape[::-1])]
        self.current_piece["shape"] = rotated
        if not self.valid_move(self.current_piece):
            self.current_piece["shape"] = old_shape

    def lock_piece(self):
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    gy = self.current_piece["y"] + y
                    gx = self.current_piece["x"] + x
                    if 0 <= gy < GRID_HEIGHT and 0 <= gx < GRID_WIDTH:
                        self.grid[gy][gx] = self.current_piece["color"]

        lines = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1][:]
                self.grid[0] = [0] * GRID_WIDTH
            else:
                y -= 1

        if lines > 0:
            self.lines_cleared += lines
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(lines, 0) * self.level
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(100, 500 - (self.level - 1) * 30)

        self.current_piece = self.next_pieces.pop(0)
        self.current_piece["x"] = GRID_WIDTH // 2 - len(self.current_piece["shape"][0]) // 2
        self.current_piece["y"] = 0

        idx = random.randint(0, len(SHAPES_WITH_COLORS) - 1)
        shape, color = SHAPES_WITH_COLORS[idx]
        self.next_pieces.append({"shape": copy.deepcopy(shape), "color": color})

        if not self.valid_move(self.current_piece):
            self.game_over = True

    def update(self, dt):
        if not self.game_over:
            self.fall_time += dt
            if self.fall_time >= self.fall_speed:
                if self.valid_move(self.current_piece, 0, 1):
                    self.current_piece["y"] += 1
                else:
                    self.lock_piece()
                self.fall_time = 0

    def draw(self):
        screen.fill(BLACK)

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, GRAY, rect, 1)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    rect = (GAME_AREA_LEFT + x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                    pygame.draw.rect(screen, self.grid[y][x], rect)

        if self.current_piece and not self.game_over:
            for y, row in enumerate(self.current_piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        rect = (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE + 1,
                                (self.current_piece["y"] + y) * BLOCK_SIZE + 1,
                                BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                        pygame.draw.rect(screen, self.current_piece["color"], rect)

        font = pygame.font.SysFont("simsun", 24)
        screen.blit(font.render("下一个:", True, WHITE), (PREVIEW_AREA_LEFT, 50))
        for i in range(min(3, len(self.next_pieces))):
            piece = self.next_pieces[i]
            preview_y = 100 + i * 100
            pygame.draw.rect(screen, GRAY, (PREVIEW_AREA_LEFT - 5, preview_y - 5, 100, 80), 2)
            shape = piece["shape"]
            shape_w = len(shape[0])
            shape_h = len(shape)
            ox = (100 - shape_w * BLOCK_SIZE) // 2
            oy = (80 - shape_h * BLOCK_SIZE) // 2
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = (PREVIEW_AREA_LEFT + ox + x * BLOCK_SIZE,
                                preview_y + oy + y * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        pygame.draw.rect(screen, piece["color"], rect)
                        pygame.draw.rect(screen, WHITE, rect, 1)

        font = pygame.font.SysFont("simsun", 28)
        screen.blit(font.render(f"分数: {self.score}", True, WHITE), (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 200))
        screen.blit(font.render(f"等级: {self.level}", True, WHITE), (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 160))
        screen.blit(font.render(f"消除: {self.lines_cleared}", True, WHITE), (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 120))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            font_big = pygame.font.SysFont("simsun", 48)
            text = font_big.render("游戏结束!", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(text, text_rect)
            font_small = pygame.font.SysFont("simsun", 24)
            text2 = font_small.render("按 R 键重新开始", True, WHITE)
            text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(text2, text_rect2)

game = Tetris()
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.reset_game()
                continue
            if not game.game_over:
                if event.key == pygame.K_LEFT:
                    if game.valid_move(game.current_piece, -1, 0):
                        game.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT:
                    if game.valid_move(game.current_piece, 1, 0):
                        game.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN:
                    if game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                        game.fall_time = 0
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    while game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    game.lock_piece()
                    game.fall_time = 0

    game.update(dt)
    game.draw()
    pygame.display.flip()

pygame.quit()