import pygame
import random

# تهيئة pygame
pygame.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 900, 700  # تكبير حجم الشاشة
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Gayar")

# الألوان
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# تحميل الصورة بجودة أفضل
image = pygame.image.load("Gayar.jpg").convert_alpha()
image = pygame.transform.smoothscale(image, (80, 50))  # تصغيرها بدقة أفضل

# تحميل الصوت
pygame.mixer.init()
hit_sound = pygame.mixer.Sound("hit.wav")  # صوت عند ضرب الطوب

# إعدادات اللاعب (اللوح)
paddle_width = 120
paddle_height = 10
paddle_y = HEIGHT - 30

# إعدادات الكرة
ball_radius = 10

# إعداد الطوب
rows, cols = 7, 10  # زيادة عدد الصفوف من 5 إلى 7
brick_width = WIDTH // cols - 5
brick_height = 50  # زيادة ارتفاع الطوب ليكون أوضح

# قائمة الهدايا وتأثيراتها
bonuses = []
bonus_types = ["expand_paddle", "extra_ball"]
active_balls = []
bricks = []  # تعريف قائمة الطوب بشكل صحيح

# حالات اللعبة
game_over = False
game_won = False

# دالة لإعادة تشغيل اللعبة بالكامل
def reset_game():
    global paddle, bricks, bonuses, active_balls, paddle_width, game_over, game_won

    game_over = False  # إعادة تعيين حالة الخسارة
    game_won = False   # إعادة تعيين حالة الفوز

    # إعادة تعيين اللوح
    paddle_width = 120
    paddle = pygame.Rect(WIDTH // 2 - paddle_width // 2, paddle_y, paddle_width, paddle_height)

    # إعادة تعيين الكرات
    active_balls.clear()
    active_balls.append({
        "rect": pygame.Rect(WIDTH // 2, HEIGHT // 2, ball_radius * 2, ball_radius * 2),
        "speed_x": 4 * random.choice((1, -1)),
        "speed_y": -4
    })

    # إعادة بناء الطوب
    bricks.clear()
    for row in range(rows):
        for col in range(cols):
            brick = pygame.Rect(col * (brick_width + 5), row * (brick_height + 5), brick_width, brick_height)
            bricks.append(brick)

    # تفريغ قائمة الهدايا
    bonuses.clear()

# تشغيل اللعبة لأول مرة
reset_game()

# حلقة اللعبة
running = True
while running:
    screen.fill(BLACK)

    # أحداث المستخدم
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # عند الضغط على زر الماوس لإعادة اللعب بعد الفوز أو الخسارة
        if event.type == pygame.MOUSEBUTTONDOWN and (game_over or game_won):
            reset_game()

    # إذا انتهت اللعبة (فوز أو خسارة)، عرض رسالة فقط وانتظار إعادة التشغيل
    if game_over:
        font = pygame.font.Font(None, 50)
        text = font.render("U Lose! Press to Restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
        pygame.display.flip()
        continue  # إيقاف التحديثات حتى يعيد اللاعب اللعبة

    if game_won:
        font = pygame.font.Font(None, 50)
        text = font.render("U Won! Press to Restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
        pygame.display.flip()
        continue  # إيقاف التحديثات حتى يعيد اللاعب اللعبة

    # تحريك اللوح بالماوس
    mouse_x, _ = pygame.mouse.get_pos()
    paddle.x = mouse_x - paddle_width // 2
    paddle.clamp_ip(screen.get_rect())  # منع الخروج عن الحدود

    # تحديث حركة الكرات
    for ball in active_balls[:]:
        ball["rect"].x += ball["speed_x"]
        ball["rect"].y += ball["speed_y"]

        # ارتداد الكرة عن الجدران
        if ball["rect"].left <= 0 or ball["rect"].right >= WIDTH:
            ball["speed_x"] *= -1
        if ball["rect"].top <= 0:
            ball["speed_y"] *= -1

        # اصطدام الكرة باللوح
        if ball["rect"].colliderect(paddle):
            ball["speed_y"] *= -1

        # اصطدام الكرة بالطوب
        for brick in bricks[:]:
            if ball["rect"].colliderect(brick):
                bricks.remove(brick)
                ball["speed_y"] *= -1
                hit_sound.play()  # تشغيل الصوت

                # احتمال عشوائي لإنزال هدية (30%)
                if random.random() < 0.3:
                    bonus = {"rect": pygame.Rect(brick.x + 20, brick.y, 15, 15), "type": random.choice(bonus_types)}
                    bonuses.append(bonus)
                break  # لمنع حذف أكثر من طوبة عند التصادم

        # إذا سقطت الكرة أسفل الشاشة
        if ball["rect"].bottom >= HEIGHT:
            active_balls.remove(ball)

    # إذا لم يبقَ أي كرة، تعلن الخسارة بدون الخروج من اللعبة
    if not active_balls:
        game_over = True

    # إذا انتهى كل الطوب، يفوز اللاعب
    if not bricks:
        game_won = True

    # تحديث حركة الهدايا
    for bonus in bonuses[:]:
        bonus["rect"].y += 3  # تتحرك للأسفل

        # إذا التقطها اللاعب
        if paddle.colliderect(bonus["rect"]):
            if bonus["type"] == "expand_paddle":
                paddle_width = min(paddle_width + 30, WIDTH)
                paddle.width = paddle_width
            elif bonus["type"] == "extra_ball":
                new_ball = {
                    "rect": pygame.Rect(paddle.x + paddle.width // 2, paddle.top - 10, ball_radius * 2, ball_radius * 2),
                    "speed_x": 4 * random.choice((1, -1)),
                    "speed_y": -4
                }
                active_balls.append(new_ball)

            bonuses.remove(bonus)

    # رسم الطوب بجودة أفضل
    for brick in bricks:
        screen.blit(image, (brick.x, brick.y))

    # رسم الهدايا ككرات
    for bonus in bonuses:
        if bonus["type"] == "expand_paddle":
            pygame.draw.ellipse(screen, GREEN, bonus["rect"])  # لون أخضر للتكبير
        elif bonus["type"] == "extra_ball":
            pygame.draw.ellipse(screen, BLUE, bonus["rect"])  # لون أزرق للكرة الإضافية

    # رسم اللوح والكرات
    pygame.draw.rect(screen, WHITE, paddle)
    for ball in active_balls:
        pygame.draw.ellipse(screen, WHITE, ball["rect"])

    # تحديث الشاشة
    pygame.display.flip()
    pygame.time.delay(15)

pygame.quit()
