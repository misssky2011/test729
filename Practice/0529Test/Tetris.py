import pygame
import randomTest
import sys

# 游戏窗口相关设置
WIDTH = 300
HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = WIDTH // BLOCK_SIZE
GRID_HEIGHT = HEIGHT // BLOCK_SIZE

# 颜色定义
# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)  # 添加蓝色定义

# 初始化pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 方块形状及对应的坐标偏移（以初始形状为基础）
SHAPES = {
    "I": [[(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)]],
    "J": [[(0, 0), (0, 1), (0, 2), (1, 2)],
          [(1, 0), (1, 1), (0, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (0, 1), (1, 1), (2, 1)]],
    "L": [[(0, 0), (0, 1), (0, 2), (1, 0)],
          [(0, 0), (0, 1), (1, 1), (2, 1)],
          [(0, 2), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (1, 0), (2, 0), (2, 1)]],
    "O": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "S": [[(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
    "T": [[(0, 0), (0, 1), (0, 2), (1, 1)],
          [(0, 1), (1, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 1)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
    "Z": [[(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (1, 0), (2, 0)]]
}

# 初始化游戏网格，0表示空白
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def draw_grid():
    """绘制游戏网格背景"""
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(win, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(win, WHITE, (0, y), (WIDTH, y))


def draw_block(x, y, color):
    """绘制一个方块"""
    pygame.draw.rect(win, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))


def draw_shape(shape, x, y, color):
    """绘制整个方块形状"""
    for block in shape:
        draw_block(x + block[0], y + block[1], color)


def create_new_shape():
    """随机生成新的方块形状及初始位置"""
    shape_type = random.choice(list(SHAPES.keys()))
    shape = SHAPES[shape_type][0]
    x = GRID_WIDTH // 2 - len(shape[0]) // 2
    y = 0
    return shape_type, shape, x, y


def check_collision(shape, x, y):
    """检查方块是否与已有方块或边界碰撞"""
    for block in shape:
        new_x = x + block[0]
        new_y = y + block[1]
        if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or grid[new_y][new_x]:
            return True
    return False


def lock_shape(shape, x, y, current_shape_type):
    """将方块锁定在网格中（当方块下落到底部或碰到其他方块时）"""
    for block in shape:
        grid[y + block[1]][x + block[0]] = current_shape_type


def clear_lines():
    """检查并清除满行的方块"""
    lines_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if all(grid[y]):
            del grid[y]
            grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            lines_cleared += 1
    return lines_cleared


def main():
    """游戏主函数"""
    global grid
    clock = pygame.time.Clock()
    game_over = False
    current_shape_type, current_shape, current_x, current_y = create_new_shape()
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not check_collision(current_shape, current_x - 1, current_y):
                    current_x -= 1
                elif event.key == pygame.K_RIGHT and not check_collision(current_shape, current_x + 1, current_y):
                    current_x += 1
                elif event.key == pygame.K_UP:
                    rotated_shape = rotate_shape(current_shape)
                    if not check_collision(rotated_shape, current_x, current_y):
                        current_shape = rotated_shape
                elif event.key == pygame.K_DOWN:
                    if not check_collision(current_shape, current_x, current_y + 1):
                        current_y += 1

        if check_collision(current_shape, current_x, current_y + 1):
            lock_shape(current_shape, current_x, current_y, current_shape_type)
            lines_cleared = clear_lines()
            current_shape_type, current_shape, current_x, current_y = create_new_shape()
            if check_collision(current_shape, current_x, current_y):
                game_over = True

        win.fill(BLACK)
        draw_grid()

        # 绘制已有的固定方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    draw_block(x, y, get_color_by_type(grid[y][x]))

        draw_shape(current_shape, current_x, current_y, get_color_by_type(current_shape_type))

        pygame.display.update()
        clock.tick(10)

    pygame.quit()
    sys.exit()


def rotate_shape(shape):
    """旋转方块形状"""
    return list(zip(*reversed(shape)))


def get_color_by_type(shape_type):
    """根据方块类型获取对应的颜色"""
    colors = {
        "I": CYAN,
        "J": BLUE,
        "L": ORANGE,
        "O": YELLOW,
        "S": GREEN,
        "T": PURPLE,
        "Z": RED
    }
    return colors.get(shape_type, BLACK)  # 如果类型不在 colors 中，返回 BLACK


if __name__ == "__main__":
    main()