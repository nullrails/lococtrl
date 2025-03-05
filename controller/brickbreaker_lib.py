import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import random
import input_lib as panel
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Constants for screen dimensions
WIDTH = 127
HEIGHT = 160

# SPI configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0
SPEED_HZ = 4000000

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display.
draw = disp.draw()
disp.display()

# Font for text
font = ImageFont.load_default()

# Function to draw the paddle
def draw_paddle(x, y, width):
    draw.rectangle((x, y, x + width, y + 10), outline=WHITE, fill=WHITE)

# Function to draw the ball
def draw_ball(x, y):
    draw.ellipse((x, y, x + 10, y + 10), outline=RED, fill=RED)

# Function to draw bricks
def draw_bricks(bricks):
    for brick, color in bricks:
        draw.rectangle((brick[0], brick[1], brick[0] + 19, brick[1] + 10), outline=WHITE, fill=color)

def run():
    # Pre-game scrolling text
    message = "Press any button to begin"
    message_width, _ = draw.textsize(message, font=font)
    scroll_x = WIDTH
    while True:
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=BLACK, fill=BLACK)
        draw.text((scroll_x, HEIGHT // 2 - 10), message, font=font, fill=WHITE)
        disp.display()
        time.sleep(0.01)
        scroll_x -= 5
        if scroll_x < -message_width:
            scroll_x = WIDTH

        if any(panel.pins()):
            break

    # Initialize paddle position and width
    paddle_height = 10
    paddle_x = (WIDTH - 40) // 2
    paddle_y = HEIGHT - paddle_height - 5
    paddle_width = 40

    # Initialize ball position and velocity
    ball_size = 10
    ball_x = random.randint(0, WIDTH - ball_size)
    ball_y = 80
    ball_dx = 4
    ball_dy = 4

    # Initialize bricks with random colors
    bricks = []
    for i in range(4):
        for j in range(6):
            brick_x = (j * 21) + 1
            brick_y = i * 12 + 20  # Move bricks down to clear space for text
            brick_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            bricks.append(((brick_x, brick_y), brick_color))

    # Score and level variables
    score = 0
    level = 1

    # Game loop
    while True:
        # Clear screen
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=BLACK, fill=BLACK)

        # Draw top bar with score and level
        draw.text((5, 2), f"Score: {score}", font=font, fill=WHITE)  # Adjusted position for score
        draw.text((WIDTH - 60, 2), f"Level: {level}", font=font, fill=WHITE)  # Adjusted position for level

        # Draw paddle, ball, and bricks
        draw_paddle(paddle_x, paddle_y, paddle_width)
        draw_ball(ball_x, ball_y)
        draw_bricks(bricks)

        # Check for input
        if panel.pins()[5] and paddle_x > 0:
            paddle_x -= 7
        if panel.pins()[10] and paddle_x < WIDTH - paddle_width:
            paddle_x += 7
        if panel.pins()[9]:
            break

        # Move ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Check for collisions with walls
        if ball_x <= 0 or ball_x >= WIDTH - ball_size:
            ball_dx *= -1
        if ball_y <= 0:
            ball_dy *= -1

        # Check for collision with paddle
        if ball_y + ball_size >= paddle_y and ball_y <= paddle_y + paddle_height and ball_x + ball_size >= paddle_x and ball_x <= paddle_x + paddle_width:
            ball_dy *= -1
            score += 1

        # Check for collision with bricks
        for brick, _ in bricks:
            brick_x, brick_y = brick
            if ball_x + ball_size >= brick_x and ball_x <= brick_x + 20 and ball_y + ball_size >= brick_y and ball_y <= brick_y + 10:
                bricks.remove((brick, _))
                ball_dy *= -1
                score += 1

        # Check for game over
        if ball_y >= HEIGHT:
            draw.text((WIDTH // 2 - 28, HEIGHT // 2 - 10), "GAME OVER", font=font, fill=WHITE)
            disp.display()
            time.sleep(2)
            break

        # Check if all bricks are cleared
        if not bricks:
            # Increment level
            level += 1
            # Increase ball speed
            ball_dx = 4 + level   
            ball_dy = 4 + level   
            # Reset ball position and direction
            ball_x = random.randint(0, WIDTH - ball_size)
            ball_y = 80
            # Decrease paddle width by 10%
            paddle_width = int(paddle_width * 0.90)
            # Redraw bricks for the next level
            bricks = []
            for i in range(4):
                for j in range(6):
                    brick_x = j * 22
                    brick_y = i * 12 + 20  # Move bricks down to clear space for text
                    brick_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    bricks.append(((brick_x, brick_y), brick_color))

        # Update display
        disp.display()
        time.sleep(0.005)  # Adjust the sleep time to control game speed

#run()

