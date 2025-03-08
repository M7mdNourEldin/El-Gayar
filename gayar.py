import pygame
import random
import requests
import os



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

# تحميل الصورة (أوفلاين أو أونلاين)
image_path = "Gayar.jpg"
image_url = "https://i.ibb.co/nsqnpn28/Gayar.jpg"

if not os.path.exists(image_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response.content)
        print("✅ The image has been successfully uploaded.!")
    else:
        print("❌  Failed to upload the image!")
        image_path = None

if image_path:
    image = pygame.image.load(image_path).convert_alpha()
    image = pygame.transform.smoothscale(image, (80, 50))
else:
    image = pygame.Surface((80, 50))
    image.fill(WHITE)

# تحميل الصوت (أوفلاين أو أونلاين)
sound_path = "hit.wav"
sound_url = "https://www.dropbox.com/s/ujte0dolxv1ge3l/hit.wav?st=pr2htt9g&dl=1"

pygame.mixer.init()

def download_sound():
    global sound_path
    if not os.path.exists(sound_path):
        response = requests.get(sound_url)
        if response.status_code == 200:
            with open(sound_path, "wb") as f:
                f.write(response.content)
            print("✅The sound has been downloaded successfully.!")
            pygame.mixer.quit()  # إعادة تهيئة pygame.mixer بعد تنزيل الملف
            pygame.mixer.init()
        else:
            print("❌ Failed to load audio.!")
            sound_path = None

download_sound()  # تحميل الصوت فقط إذا لم يكن موجودًا

if sound_path and os.path.exists(sound_path):
    try:
        hit_sound = pygame.mixer.Sound(sound_path)
        hit_sound.play()
    except pygame.error as e:
        print(f'❌ Failed to load audio.: {e}')
        hit_sound = None
else:
    hit_sound = None


# إعدادات اللاعب (اللوح)
paddle_width = 120
paddle_height = 10
paddle_y = HEIGHT - 30

# إعدادات الكرة
ball_radius = 10

# إعداد الطوب
rows, cols = 7, 10
brick_width = WIDTH // cols - 5
brick_height = 50

# قائمة الهدايا وتأثيراتها
bonuses = []
bonus_types = ["expand_paddle", "extra_ball"]
active_balls = []
bricks = []

# حالات اللعبة
game_over = False
game_won = False

# دالة لإعادة تشغيل اللعبة بالكامل
def reset_game():
    global paddle, bricks, bonuses, active_balls, paddle_width, game_over, game_won

    game_over = False
    game_won = False

    paddle_width = 120
    paddle = pygame.Rect(WIDTH // 2 - paddle_width // 2, paddle_y, paddle_width, paddle_height)

    active_balls.clear()
    active_balls.append({
        "rect": pygame.Rect(WIDTH // 2, HEIGHT // 2, ball_radius * 2, ball_radius * 2),
        "speed_x": 4 * random.choice((1, -1)),
        "speed_y": -4
    })

    bricks.clear()
    for row in range(rows):
        for col in range(cols):
            brick = pygame.Rect(col * (brick_width + 5), row * (brick_height + 5), brick_width, brick_height)
            bricks.append(brick)

    bonuses.clear()

# تشغيل اللعبة لأول مرة
reset_game()

# حلقة اللعبة
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and (game_over or game_won):
            reset_game()

    if game_over:
        font = pygame.font.Font(None, 50)
        text = font.render("U Lose! Press to Restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
        pygame.display.flip()
        continue

    if game_won:
        font = pygame.font.Font(None, 50)
        text = font.render("U Won! Press to Restart", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
        pygame.display.flip()
        continue

    mouse_x, _ = pygame.mouse.get_pos()
    paddle.x = mouse_x - paddle_width // 2
    paddle.clamp_ip(screen.get_rect())

    for ball in active_balls[:]:
        ball["rect"].x += ball["speed_x"]
        ball["rect"].y += ball["speed_y"]

        if ball["rect"].left <= 0 or ball["rect"].right >= WIDTH:
            ball["speed_x"] *= -1
        if ball["rect"].top <= 0:
            ball["speed_y"] *= -1

        if ball["rect"].colliderect(paddle):
            ball["speed_y"] *= -1

        for brick in bricks[:]:
            if ball["rect"].colliderect(brick):
                bricks.remove(brick)
                ball["speed_y"] *= -1
                if hit_sound:
                    hit_sound.play()

                if random.random() < 0.3:
                    bonus = {"rect": pygame.Rect(brick.x + 20, brick.y, 15, 15), "type": random.choice(bonus_types)}
                    bonuses.append(bonus)
                break

        if ball["rect"].bottom >= HEIGHT:
            active_balls.remove(ball)

    if not active_balls:
        game_over = True

    if not bricks:
        game_won = True

    for brick in bricks:
        screen.blit(image, (brick.x, brick.y))

    pygame.draw.rect(screen, WHITE, paddle)
    for ball in active_balls:
        pygame.draw.ellipse(screen, WHITE, ball["rect"])

    pygame.display.flip()
    pygame.time.delay(15)

pygame.quit()
