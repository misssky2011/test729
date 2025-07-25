import pygame
import randomTest

# 初始化pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("闪烁的满天星")

# 设置星星的数量
NUM_STARS = 500

# 设置星星的颜色和大小范围
STAR_SIZE_RANGE = (1, 3)  # 星星的大小范围
STAR_COLORS = [(255, 255, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]  # 白色、黄色、蓝色、紫色等

# 星星类
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(STAR_SIZE_RANGE[0], STAR_SIZE_RANGE[1])
        self.color = random.choice(STAR_COLORS)
        self.brightness = 255  # 初始亮度
        self.brightness_direction = random.choice([-1, 1])  # 控制亮度的增加或减少

    # 更新星星的亮度（模拟闪烁效果）
    def update(self):
        if self.brightness <= 50:
            self.brightness_direction = 1
        elif self.brightness >= 255:
            self.brightness_direction = -1

        self.brightness += self.brightness_direction * random.randint(1, 5)

    # 绘制星星
    def draw(self, win):
        # 根据亮度调整星星的颜色
        r, g, b = self.color
        brightness_factor = self.brightness / 255.0  # 亮度因子在0到1之间
        r = int(r * brightness_factor)
        g = int(g * brightness_factor)
        b = int(b * brightness_factor)

        # 限制 RGB 值在 0 到 255 之间
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        # 绘制星星
        pygame.draw.circle(win, (r, g, b), (self.x, self.y), self.size)

# 创建星星对象列表
stars = [Star() for _ in range(NUM_STARS)]

# 游戏主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 填充黑色背景
    win.fill((0, 0, 0))

    # 更新每颗星星并绘制
    for star in stars:
        star.update()  # 更新星星的亮度（闪烁效果）
        star.draw(win)  # 绘制星星

    # 更新显示
    pygame.display.update()

    # 设置帧率
    pygame.time.Clock().tick(60)

# 退出pygame
pygame.quit()
