import pygame
import random

# 初始化
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# 方块颜色
COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        
    def new_piece(self):
        # 随机选择一个形状和颜色
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        
        # 初始位置 (顶部中间)
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {"shape": shape, "color": color, "x": x, "y": y}
    
    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + x_offset
                    new_y = piece["y"] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self):
        # 转置矩阵然后反转每一行得到旋转后的形状
        piece = self.current_piece.copy()
        piece["shape"] = [list(row) for row in zip(*piece["shape"][::-1])]
        
        if self.valid_move(piece):
            self.current_piece = piece
    
    def lock_piece(self):
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = self.current_piece["color"]
        
        # 检查是否有完整的行
        self.clear_lines()
        
        # 生成新方块
        self.current_piece = self.new_piece()
        
        # 检查游戏是否结束
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                # 移动上面的行下来
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1].copy()
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
        
        # 更新分数
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800
    
    def update(self):
        if not self.game_over:
            if self.valid_move(self.current_piece, 0, 1):
                self.current_piece["y"] += 1
            else:
                self.lock_piece()
    
    def draw(self):
        # 绘制游戏区域背景
        pygame.draw.rect(screen, WHITE, (GAME_AREA_LEFT, 0, BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT), 0)
        
        # 绘制网格
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(screen, BLACK, 
                                (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                 BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制已落下的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, 
                                     BLOCK_SIZE - 2, BLOCK_SIZE - 2), 0)
        
        # 绘制当前方块
        if not self.game_over:
            for y, row in enumerate(self.current_piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece["color"], 
                                        (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE + 1, 
                                         (self.current_piece["y"] + y) * BLOCK_SIZE + 1, 
                                         BLOCK_SIZE - 2, BLOCK_SIZE - 2), 0)
        
        # 绘制分数
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20, 30))
        
        # 游戏结束提示
        if self.game_over:
            font = pygame.font.SysFont(None, 48)
            game_over_text = font.render("Game Over!", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))

# 创建游戏实例
game = Tetris()

# 游戏主循环
running = True
while running:
    # 控制方块下落速度
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not game.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, -1, 0):
                    game.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, 1, 0):
                    game.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN and game.valid_move(game.current_piece, 0, 1):
                    game.current_piece["y"] += 1
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:  # 硬降落
                    while game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    game.lock_piece()
    
    # 游戏更新
    game.update()
    
    # 游戏绘制
    game.draw()
    
    pygame.display.flip()
    clock.tick(2)  # 控制游戏速度

pygame.quit()