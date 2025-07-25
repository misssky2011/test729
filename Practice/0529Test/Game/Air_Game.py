import pygame
import randomTest

# 游戏窗口相关设置
WIDTH = 480
HEIGHT = 700
# 游戏窗口创建
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机大战")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 玩家飞机相关设置
PLAYER_SPEED = 5
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
player_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
player_img.fill(GREEN)
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.centery = HEIGHT - 50

# 子弹相关设置
BULLET_SPEED = 10
BULLET_WIDTH = 10
BULLET_HEIGHT = 20
bullet_img = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
bullet_img.fill(WHITE)
bullets = []

# 敌机相关设置
ENEMY_SPEED = 3
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
enemy_img = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
enemy_img.fill(RED)
enemies = []
SPAWN_ENEMY_TIME = 1000  # 每隔多久生成一个敌机（单位：毫秒）
last_enemy_spawn_time = pygame.time.get_ticks()

# 游戏主循环的时钟，用于控制帧率
clock = pygame.time.Clock()


def draw_player():
    """绘制玩家飞机"""
    win.blit(player_img, player_rect)


def draw_bullets():
    """绘制子弹"""
    for bullet in bullets:
        win.blit(bullet_img, bullet)


def draw_enemies():
    """绘制敌机"""
    for enemy in enemies:
        win.blit(enemy_img, enemy)


def move_player():
    """移动玩家飞机（根据按键控制）"""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += PLAYER_SPEED
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect.y += PLAYER_SPEED


def fire_bullet():
    """玩家飞机发射子弹"""
    bullet = bullet_img.get_rect()
    bullet.centerx = player_rect.centerx
    bullet.top = player_rect.top
    bullets.append(bullet)


def spawn_enemy():
    """生成敌机"""
    global last_enemy_spawn_time
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_spawn_time > SPAWN_ENEMY_TIME:
        enemy = enemy_img.get_rect()
        enemy.x = random.randint(0, WIDTH - ENEMY_WIDTH)
        enemy.y = 0
        enemies.append(enemy)
        last_enemy_spawn_time = current_time


def move_bullets():
    """移动子弹（向上移动）"""
    for bullet in bullets:
        bullet.y -= BULLET_SPEED
        if bullet.y < 0:
            bullets.remove(bullet)


def move_enemies():
    """移动敌机（向下移动）"""
    for enemy in enemies:
        enemy.y += ENEMY_SPEED
        if enemy.y > HEIGHT:
            enemies.remove(enemy)


def check_collisions():
    """检查碰撞（子弹与敌机、玩家飞机与敌机）"""
    global enemies, bullets
    # 检查子弹与敌机的碰撞
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
    # 检查玩家飞机与敌机的碰撞
    for enemy in enemies:
        if player_rect.colliderect(enemy):
            return True
    return False


def game_loop():
    """游戏主循环"""
    global running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                fire_bullet()

        move_player()
        spawn_enemy()
        move_bullets()
        move_enemies()

        if check_collisions():
            running = False

        win.fill(BLACK)
        draw_player()
        draw_bullets()
        draw_enemies()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    game_loop()