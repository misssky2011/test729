import pygame
import randomTest
import time

# 游戏窗口大小
WIDTH = 800
HEIGHT = 600
# 地洞数量（行列数）
HOLE_ROWS = 3
HOLE_COLS = 3
# 地洞大小以及间距等相关设置
HOLE_SIZE = 100
HOLE_SPACING = 50
# 地鼠出现时间间隔范围（秒）
MOLE_APPEAR_TIME_MIN = 1
MOLE_APPEAR_TIME_MAX = 3
# 游戏总时长（秒）
GAME_TIME = 30
# 颜色定义
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)

# 初始化pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打地鼠游戏")

# 初始化字体，用于显示得分等信息
font = pygame.font.SysFont(None, 30)

# 地洞的坐标列表（左上角坐标）
holes = []
for row in range(HOLE_ROWS):
    for col in range(HOLE_COLS):
        x = col * (HOLE_SIZE + HOLE_SPACING) + (WIDTH - (HOLE_COLS * (HOLE_SIZE + HOLE_SPACING))) // 2
        y = row * (HOLE_SIZE + HOLE_SPACING) + (HEIGHT - (HOLE_ROWS * (HOLE_SIZE + HOLE_SPACING))) // 2
        holes.append((x, y))

# 地鼠是否出现的状态列表，初始都为False
moles_appear = [False] * len(holes)
# 得分
score = 0
# 游戏开始时间
start_time = time.time()


def draw_holes():
    """绘制地洞"""
    for hole in holes:
        pygame.draw.rect(win, BROWN, (hole[0], hole[1], HOLE_SIZE, HOLE_SIZE))


def draw_moles():
    """绘制出现的地鼠"""
    for index, appear in enumerate(moles_appear):
        if appear:
            x, y = holes[index]
            pygame.draw.circle(win, GREY, (x + HOLE_SIZE // 2, y + HOLE_SIZE // 2), HOLE_SIZE // 3)


def draw_score():
    """在屏幕上显示得分"""
    score_text = font.render(f"得分: {score}", True, WHITE)
    win.blit(score_text, (10, 10))


def draw_timer():
    """在屏幕上显示剩余时间"""
    remaining_time = GAME_TIME - (time.time() - start_time)
    time_text = font.render(f"剩余时间: {int(remaining_time)}s", True, WHITE)
    win.blit(time_text, (WIDTH - 120, 10))


def check_hit(pos):
    """检查是否点击到了地鼠"""
    global score
    for index, hole in enumerate(holes):
        x, y = hole
        if x <= pos[0] <= x + HOLE_SIZE and y <= pos[1] <= y + HOLE_SIZE and moles_appear[index]:
            score += 1
            moles_appear[index] = False
            return True
    return False


def random_mole_appear():
    """随机让一个地鼠出现"""
    available_holes = [i for i in range(len(holes)) if not moles_appear[i]]
    if available_holes:
        random_hole = random.choice(available_holes)
        moles_appear[random_hole] = True
        return True
    return False


def game_loop():
    """游戏主循环"""
    global score
    clock = pygame.time.Clock()
    mole_appear_timer = None
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_hit(event.pos):
                    print("打中啦！")
        win.fill(BLACK)

        # 绘制地洞、地鼠、得分和剩余时间
        draw_holes()
        draw_moles()
        draw_score()
        draw_timer()

        # 根据时间随机让地鼠出现
        if mole_appear_timer is None or time.time() - mole_appear_timer > random.uniform(MOLE_APPEAR_TIME_MIN,
                                                                                       MOLE_APPEAR_TIME_MAX):
            if random_mole_appear():
                mole_appear_timer = time.time()

        # 检查游戏时间是否结束
        if time.time() - start_time > GAME_TIME:
            game_over = True

        pygame.display.update()
        clock.tick(60)

    # 游戏结束，显示最终得分
    final_score_text = font.render(f"游戏结束，最终得分: {score}", True, WHITE)
    win.blit(final_score_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.update()
    time.sleep(3)
    pygame.quit()


if __name__ == "__main__":
    game_loop()