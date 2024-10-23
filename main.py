import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Initialize the mixer for sound
pygame.mixer.init()

# Load sound effects
paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")
bullet_shot_sound = pygame.mixer.Sound("bullet_shot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# Set up the game window
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pong with Guns')

# Set frame rate to control overall game speed
FPS = 60
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WEAKENED_COLOR = (200, 0, 0)
BLUE = (0, 0, 255)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 5
AI_PADDLE_SPEED = 4

# Ball settings
BALL_RADIUS = 10
BALL_SPEED_X = 4
BALL_SPEED_Y = 4
ball_velocity_x = BALL_SPEED_X
ball_velocity_y = BALL_SPEED_Y

# Bullet settings
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
BULLET_SPEED = 7
MAX_BULLETS = 5
bullet_list = []

# Score settings
player_score = 0
ai_score = 0
winning_score = 10

# Fonts for text
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Create paddles and ball
player_paddle = pygame.Rect(30, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai_paddle = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)

# Track bullet supply
player_bullet_count = MAX_BULLETS
ai_bullet_count = MAX_BULLETS

# Explosion particles
explosion_particles = []

# Power-up settings
power_up_active = False
power_up_timer = 0
power_up = pygame.Rect(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - 10, 20, 20)
power_up_visible = True
power_up_direction = None
power_up_speed = 2

# Function to reset ball and paddles without recreating them or clearing the screen
def reset_ball_and_paddles(direction_x):
    global ball_velocity_x, ball_velocity_y, player_bullet_count, ai_bullet_count

    # Reposition paddles and ball
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    player_paddle.centery = SCREEN_HEIGHT // 2
    ai_paddle.centery = SCREEN_HEIGHT // 2

    # Reset ball velocity to original speed
    ball_velocity_x = BALL_SPEED_X * direction_x
    ball_velocity_y = BALL_SPEED_Y * random.choice([-1, 1])

    # Reset bullet counts after hitting the ball
    player_bullet_count = MAX_BULLETS
    ai_bullet_count = MAX_BULLETS

# Function to fully reset game state and scores
def reset_game():
    global player_score, ai_score, ball_velocity_x, ball_velocity_y, player_bullet_count, ai_bullet_count, power_up_visible, power_up_direction

    # Reset all game state
    player_score = 0
    ai_score = 0
    player_bullet_count = MAX_BULLETS
    ai_bullet_count = MAX_BULLETS
    power_up_visible = True
    power_up_direction = None
    power_up.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    reset_ball_and_paddles(random.choice([-1, 1]))

# Function to shoot a bullet
def shoot_bullet(paddle, direction):
    global player_bullet_count, ai_bullet_count, MAX_BULLETS, power_up_active
    if direction == "player" and (power_up_active or player_bullet_count > 0):
        bullet = pygame.Rect(paddle.right, paddle.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
        bullet_list.append((bullet, BULLET_SPEED))
        bullet_shot_sound.play()
        if not power_up_active:
            player_bullet_count -= 1
    elif direction == "ai" and ai_bullet_count > 0:
        bullet = pygame.Rect(paddle.left - BULLET_WIDTH, paddle.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
        bullet_list.append((bullet, -BULLET_SPEED))
        bullet_shot_sound.play()
        ai_bullet_count -= 1

# Function to handle bullet collisions
def handle_bullet_collisions():
    global player_bullet_count, ai_bullet_count, ball_velocity_x, ball_velocity_y, player_paddle_color, ai_paddle_color, power_up_direction
    for bullet, speed in bullet_list[:]:
        bullet.x += speed

        # Remove bullet if it goes off-screen
        if bullet.right < 0 or bullet.left > SCREEN_WIDTH:
            bullet_list.remove((bullet, speed))
            continue

        # Bullet hitting AI paddle
        if bullet.colliderect(ai_paddle):
            bullet_list.remove((bullet, speed))
            ai_paddle.height = max(PADDLE_HEIGHT // 2, ai_paddle.height - 10)  # Shrink AI paddle
            explosion_sound.play()
            ai_paddle_color = WEAKENED_COLOR  # Change color to indicate weakening
            explosion_particles.append((bullet.centerx, bullet.centery))

        # Bullet hitting Player paddle
        elif bullet.colliderect(player_paddle):
            bullet_list.remove((bullet, speed))
            player_paddle.height = max(PADDLE_HEIGHT // 2, player_paddle.height - 10)  # Shrink Player paddle
            explosion_sound.play()
            player_paddle_color = WEAKENED_COLOR  # Change color to indicate weakening
            explosion_particles.append((bullet.centerx, bullet.centery))

        # Bullet hitting the ball
        elif bullet.colliderect(ball):
            bullet_list.remove((bullet, speed))
            if speed > 0:  # Player bullet
                ball_velocity_x *= 1.1
                ball_velocity_y *= 1.1
            else:  # AI bullet
                ball_velocity_x *= 0.9
                ball_velocity_y *= 0.9
            explosion_sound.play()
            explosion_particles.append((bullet.centerx, bullet.centery))

        # Bullet hitting the power-up
        elif bullet.colliderect(power_up) and power_up_visible:
            bullet_list.remove((bullet, speed))
            power_up_direction = "player" if speed > 0 else "ai"

# Function to handle explosion visuals
def draw_explosions():
    for (x, y) in explosion_particles[:]:
        pygame.draw.circle(screen, RED, (x, y), 15)
        explosion_particles.remove((x, y))

# Start screen function
def show_start_screen():
    screen.fill(BLACK)
    start_text = font.render("Press SPACE to Start", True, GREEN)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Game loop
running = True
game_started = False
player_paddle_color = WHITE
ai_paddle_color = WHITE
ai_shoot_timer = 0
show_start_screen()  # Show start screen before game starts
while running:
    screen.fill(BLACK)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if power_up_active or player_bullet_count > 0:
                    shoot_bullet(player_paddle, "player")

    # Get keys for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN]:
        player_paddle.y += PADDLE_SPEED

    # Keep player paddle within the screen boundaries
    if player_paddle.top < 0:
        player_paddle.top = 0
    if player_paddle.bottom > SCREEN_HEIGHT:
        player_paddle.bottom = SCREEN_HEIGHT

    # AI paddle movement (basic tracking of the ball)
    if ai_paddle.centery < ball.centery:
        ai_paddle.y += AI_PADDLE_SPEED
    if ai_paddle.centery > ball.centery:
        ai_paddle.y -= AI_PADDLE_SPEED

    # Keep AI paddle within the screen boundaries
    if ai_paddle.top < 0:
        ai_paddle.top = 0
    if ai_paddle.bottom > SCREEN_HEIGHT:
        ai_paddle.bottom = SCREEN_HEIGHT

    # Ball movement
    ball.x += ball_velocity_x
    ball.y += ball_velocity_y

    # Ball collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_velocity_y *= -1  # Reverse the direction when it hits top or bottom

    # Ball collision with player paddle
    if player_paddle.colliderect(ball):
        ball_velocity_x = -ball_velocity_x
        paddle_hit_sound.play()
        player_paddle_color = WHITE  # Reset color on successful hit
        player_paddle.height = min(PADDLE_HEIGHT, player_paddle.height + 10)  # Regain paddle height
        if not power_up_active:
            player_bullet_count = MAX_BULLETS  # Refill bullets after hitting the ball

    # Ball collision with AI paddle
    if ball.colliderect(ai_paddle):
        ball_velocity_x = -ball_velocity_x
        paddle_hit_sound.play()
        ai_paddle_color = WHITE  # Reset color on successful hit
        ai_paddle.height = min(PADDLE_HEIGHT, ai_paddle.height + 10)  # Regain paddle height
        ai_bullet_count = MAX_BULLETS  # Refill bullets after hitting the ball

    # Scoring (when the ball goes beyond the left or right boundaries)
    if ball.left <= 0:  # AI scores
        ai_score += 1
        if ai_score >= winning_score:
            show_start_screen()
            reset_game()
        else:
            reset_ball_and_paddles(1)
    if ball.right >= SCREEN_WIDTH:  # Player scores
        player_score += 1
        if player_score >= winning_score:
            show_start_screen()
            reset_game()
        else:
            reset_ball_and_paddles(-1)

    # Handle bullet collisions
    handle_bullet_collisions()

    # Power-up handling
    if power_up_visible:
        pygame.draw.rect(screen, BLUE, power_up)
        if power_up_direction == "player":
            power_up.x -= power_up_speed
            if power_up.right < 0:
                power_up.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                power_up_direction = None
        elif power_up_direction == "ai":
            power_up.x += power_up_speed
            if power_up.left > SCREEN_WIDTH:
                power_up.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                power_up_direction = None

        if power_up.colliderect(player_paddle):
            power_up_active = True
            power_up_visible = False
            power_up_timer = pygame.time.get_ticks()
        elif power_up.colliderect(ai_paddle):
            power_up_visible = False

    # Auto-shooting when power-up is active
    if power_up_active:
        if pygame.time.get_ticks() - power_up_timer < 3000:  # 3 seconds of power-up
            if pygame.time.get_ticks() % 200 < 20:  # Shoot every 200 ms (5 bullets per second)
                shoot_bullet(player_paddle, "player")
        else:
            power_up_active = False
            power_up = pygame.Rect(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - 10, 20, 20)
            power_up_visible = True
            power_up_direction = None

    # Draw paddles, ball, bullets, and score
    # Draw player paddle
    pygame.draw.rect(screen, player_paddle_color, player_paddle)

    # Draw AI paddle
    pygame.draw.rect(screen, ai_paddle_color, ai_paddle)

    # Draw ball
    pygame.draw.ellipse(screen, WHITE, ball)
    for bullet, _ in bullet_list:
        pygame.draw.rect(screen, YELLOW, bullet)

    # Draw explosions
    draw_explosions()

    # Display the score during gameplay
    player_text = font.render(str(player_score), True, WHITE)
    ai_text = font.render(str(ai_score), True, WHITE)
    screen.blit(player_text, (SCREEN_WIDTH // 4, 20))
    screen.blit(ai_text, (SCREEN_WIDTH * 3 // 4, 20))

    # Display bullet count (clip) for player if power-up is not active
    if not power_up_active:
        bullet_count_text = small_font.render(f'Bullets: {player_bullet_count}', True, WHITE)
        screen.blit(bullet_count_text, (20, SCREEN_HEIGHT - 40))

    # AI shooting every once in a while
    ai_shoot_timer += 1
    if ai_shoot_timer > 120:  # AI shoots every 2 seconds
        shoot_bullet(ai_paddle, "ai")
        ai_shoot_timer = 0

    # Update display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()
