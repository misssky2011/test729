import pygame
import math
import randomTest

# 游戏窗口大小
WIDTH = 800
HEIGHT = 600
# 泡泡大小
BUBBLE_RADIUS = 20
# 泡泡颜色列表
BUBBLE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
# 炮台相关设置
CANNON_WIDTH = 80
CANNON_HEIGHT = 40
CANNON_COLOR = (128, 128, 128)
# 炮台初始位置
cannon_x = WIDTH // 2 - CANNON_WIDTH // 2
cannon_y = HEIGHT - CANNON_HEIGHT
# 炮台角度（初始为水平方向，角度以弧度制表示）
cannon_angle = 0
# 泡泡发射速度
BUBBLE_SPEED = 10
# 存储当前存在的泡泡对象列表
bubbles = []
# 游戏主循环的时钟，用于控制帧率
clock = pygame.time.Clock()

# 初始化pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("泡泡龙游戏")

# 发射泡泡的函数
def fire_bubble():
    global cannon_angle
    color = random.choice(BUBBLE_COLORS)
    start_x = cannon_x + CANNON_WIDTH // 2
    start_y = cannon_y
    velocity_x = BUBBLE_SPEED * math.cos(cannon_angle)
    velocity_y = -BUBBLE_SPEED * math.sin(cannon_angle)
    new_bubble = [start_x, start_y, velocity_x, velocity_y, color]
    bubbles.append(new_bubble)

# 移动泡泡的函数
def move_bubbles():
    # 遍历所有泡泡并更新其位置
    for bubble in bubbles[:]:  # 使用切片以避免在遍历时修改列表
        bubble[0] += bubble[2]  # 更新泡泡的 x 坐标
        bubble[1] += bubble[3]  # 更新泡泡的 y 坐标

        # 如果泡泡超出屏幕，则移除该泡泡
        if bubble[1] < 0 or bubble[1] > HEIGHT or bubble[0] < 0 or bubble[0] > WIDTH:
            bubbles.remove(bubble)

# 绘制泡泡的函数
def draw_bubbles():
    for bubble in bubbles:
        pygame.draw.circle(win, bubble[4], (int(bubble[0]), int(bubble[1])), BUBBLE_RADIUS)

# 绘制炮台的函数
def draw_cannon():
    points = [(cannon_x, cannon_y),
              (cannon_x + CANNON_WIDTH * math.cos(cannon_angle), cannon_y - CANNON_WIDTH * math.sin(cannon_angle)),
              (cannon_x + CANNON_WIDTH * math.cos(cannon_angle) + CANNON_HEIGHT * math.sin(cannon_angle),
               cannon_y - CANNON_WIDTH * math.sin(cannon_angle) - CANNON_HEIGHT * math.cos(cannon_angle)),
              (cannon_x + CANNON_HEIGHT * math.sin(cannon_angle), cannon_y - CANNON_HEIGHT * math.cos(cannon_angle))]
    pygame.draw.polygon(win, CANNON_COLOR, points)

# 游戏主循环
def game_loop():
    global cannon_angle
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                fire_bubble()
            elif event.type == pygame.MOUSEMOTION:
                dx = pygame.mouse.get_pos()[0] - (cannon_x + CANNON_WIDTH // 2)
                cannon_angle = math.atan2(dx, CANNON_HEIGHT)

        # 移动并更新泡泡状态
        move_bubbles()

        # 清屏并绘制
        win.fill((0, 0, 0))  # 清空屏幕
        draw_bubbles()       # 绘制所有泡泡
        draw_cannon()        # 绘制炮台
        pygame.display.update()  # 更新显示

        # 控制帧率
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    game_loop()
