import pygame
import random
import copy

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
GRAY = (128, 128, 128)

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PREVIEW_COUNT = 3  # 显示接下来3个方块
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE
PREVIEW_AREA_LEFT = BLOCK_SIZE * (GRID_WIDTH + 2)

# 方块形状和颜色（固定配对）
SHAPES_WITH_COLORS = [
    ([[1, 1, 1, 1]], CYAN),           # I
    ([[1, 1], [1, 1]], YELLOW),       # O
    ([[1, 1, 1], [0, 1, 0]], PURPLE), # T
    ([[1, 1, 1], [1, 0, 0]], ORANGE), # L
    ([[1, 1, 1], [0, 0, 1]], BLUE),   # J
    ([[0, 1, 1], [1, 1, 0]], GREEN),  # S
    ([[1, 1, 0], [0, 1, 1]], RED)     # Z
]

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块 - 显示下一个方块")

clock = pygame.time.Clock()

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_pieces = []  # 存储接下来的方块
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        
        # 初始化下一个方块队列
        self.init_next_pieces()
    
    def init_next_pieces(self):
        """初始化下一个方块队列"""
        self.next_pieces = []
        for _ in range(PREVIEW_COUNT + 1):
            self.next_pieces.append(self.create_piece())
        self.spawn_new_piece()
    
    def create_piece(self):
        """创建一个新的方块（包含形状和颜色）"""
        shape_idx = random.randint(0, len(SHAPES_WITH_COLORS) - 1)
        shape, color = SHAPES_WITH_COLORS[shape_idx]
        return {"shape": copy.deepcopy(shape), "color": color}
    
    def spawn_new_piece(self):
        """生成新方块"""
        if self.current_piece is None:
            # 第一个方块
            self.current_piece = self.next_pieces.pop(0)
            self.next_pieces.append(self.create_piece())
        else:
            # 使用队列中的下一个方块
            self.current_piece = self.next_pieces.pop(0)
            self.next_pieces.append(self.create_piece())
        
        # 设置初始位置
        self.current_piece["x"] = GRID_WIDTH // 2 - len(self.current_piece["shape"][0]) // 2
        self.current_piece["y"] = 0
        
        # 检查游戏是否结束
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
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
        """旋转方块"""
        rotated_shape = [list(row) for row in zip(*self.current_piece["shape"][::-1])]
        original_shape = self.current_piece["shape"]
        self.current_piece["shape"] = rotated_shape
        
        if not self.valid_move(self.current_piece):
            # 尝试向左移动
            self.current_piece["x"] -= 1
            if not self.valid_move(self.current_piece):
                # 尝试向右移动
                self.current_piece["x"] += 2
                if not self.valid_move(self.current_piece):
                    # 恢复原状
                    self.current_piece["x"] -= 1
                    self.current_piece["shape"] = original_shape
    
    def lock_piece(self):
        """固定当前方块"""
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = self.current_piece["color"]
        
        lines_cleared = self.clear_lines()
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += scores.get(lines_cleared, 0) * self.level
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(100, 500 - (self.level - 1) * 30)
        
        self.spawn_new_piece()
    
    def clear_lines(self):
        """消除完整的行并返回消除的行数"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1].copy()
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
            else:
                y -= 1
        return lines_cleared
    
    def update(self, delta_time):
        """更新游戏状态"""
        if not self.game_over:
            self.fall_time += delta_time
            if self.fall_time >= self.fall_speed:
                if self.valid_move(self.current_piece, 0, 1):
                    self.current_piece["y"] += 1
                else:
                    self.lock_piece()
                self.fall_time = 0
    
    def draw_preview(self):
        """绘制接下来的方块"""
        font = pygame.font.SysFont("simsun", 24)
        title_text = font.render("下一个:", True, WHITE)
        screen.blit(title_text, (PREVIEW_AREA_LEFT, 50))
        
        # 绘制接下来的3个方块
        for i in range(PREVIEW_COUNT):
            if i < len(self.next_pieces):
                piece = self.next_pieces[i]
                
                # 计算预览区域的Y坐标
                preview_y = 100 + i * 100
                
                # 绘制方块预览背景
                pygame.draw.rect(screen, GRAY, 
                               (PREVIEW_AREA_LEFT - 5, preview_y - 5, 
                                100, 80), 2)
                
                # 获取方块的形状和颜色
                shape = piece["shape"]
                color = piece["color"]  # 直接使用存储的颜色
                
                # 计算方块在预览区域中的偏移，使其居中
                shape_width = len(shape[0])
                shape_height = len(shape)
                offset_x = (100 - shape_width * BLOCK_SIZE) // 2
                offset_y = (80 - shape_height * BLOCK_SIZE) // 2
                
                # 绘制方块
                for y, row in enumerate(shape):
                    for x, cell in enumerate(row):
                        if cell:
                            # 使用方块自身的颜色
                            pygame.draw.rect(screen, color, 
                                           (PREVIEW_AREA_LEFT + offset_x + x * BLOCK_SIZE,
                                            preview_y + offset_y + y * BLOCK_SIZE,
                                            BLOCK_SIZE - 1, BLOCK_SIZE - 1), 0)
                            # 添加边框效果
                            pygame.draw.rect(screen, WHITE, 
                                           (PREVIEW_AREA_LEFT + offset_x + x * BLOCK_SIZE,
                                            preview_y + offset_y + y * BLOCK_SIZE,
                                            BLOCK_SIZE - 1, BLOCK_SIZE - 1), 1)
    
    def draw(self):
        """绘制游戏界面"""
        # 清空屏幕
        screen.fill(BLACK)
        
        # 绘制游戏区域背景
        pygame.draw.rect(screen, BLACK, (GAME_AREA_LEFT, 0, BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT))
        
        # 绘制网格线
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(screen, GRAY, 
                                (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                 BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制已落下的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE + 1, 
                                     y * BLOCK_SIZE + 1, 
                                     BLOCK_SIZE - 2, BLOCK_SIZE - 2), 0)
        
        # 绘制当前方块
        if not self.game_over and self.current_piece:
            for y, row in enumerate(self.current_piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece["color"], 
                                        (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE + 1, 
                                         (self.current_piece["y"] + y) * BLOCK_SIZE + 1, 
                                         BLOCK_SIZE - 2, BLOCK_SIZE - 2), 0)
        
        # 绘制游戏信息
        font = pygame.font.SysFont("simsun", 28)
        
        # 分数
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 200))
        
        # 等级
        level_text = font.render(f"等级: {self.level}", True, WHITE)
        screen.blit(level_text, (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 160))
        
        # 消除行数
        lines_text = font.render(f"消除: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (PREVIEW_AREA_LEFT, SCREEN_HEIGHT - 120))
        
        # 绘制预览区域
        self.draw_preview()
        
        # 游戏结束提示
        if self.game_over:
            # 半透明遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            font_big = pygame.font.SysFont("simsun", 48)
            game_over_text = font_big.render("游戏结束!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, text_rect)
            
            font_small = pygame.font.SysFont("simsun", 24)
            restart_text = font_small.render("按 R 键重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(restart_text, restart_rect)
    
    def restart(self):
        """重新开始游戏"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.next_pieces = []
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.init_next_pieces()

# 创建游戏实例
game = Tetris()

# 游戏主循环
running = True
while running:
    # 计算时间差
    delta_time = clock.tick(60)  # 60帧
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game.game_over:  # 按R重新开始
                game.restart()
            
            if not game.game_over:
                if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, -1, 0):
                    game.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, 1, 0):
                    game.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN:
                    if game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                        game.fall_time = 0  # 重置下落计时器
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:  # 硬降落
                    while game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    game.lock_piece()
                    game.fall_time = 0
    
    # 游戏更新
    game.update(delta_time)
    
    # 游戏绘制
    game.draw()
    
    pygame.display.flip()

pygame.quit()