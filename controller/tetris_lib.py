from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import random

import input_lib as panel

def run():

    WIDTH = 128
    HEIGHT = 160
    SPEED_HZ = 4000000
    # SPI configuration.
    DC = 24
    RST = 25
    SPI_PORT = 0
    SPI_DEVICE = 0

    # Create TFT LCD display class.
    disp = TFT.ST7735(
        DC,
        rst=RST,
        spi=SPI.SpiDev(
            SPI_PORT,
            SPI_DEVICE,
            max_speed_hz=SPEED_HZ))

    # Initialize display.

    # Get a PIL Draw object to start drawing on the display buffer.
    draw = disp.draw()

    disp.display()

    from PIL import Image, ImageDraw
    import time

    # LCD dimensions
    LCD_WIDTH = 128
    LCD_HEIGHT = 160

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Tetris block shapes
    BLOCKS = [
        [(1, 1, 1),    # I-shape
         (0, 0, 0),
         (0, 0, 0)],

        [(1, 1),       # O-shape
         (1, 1)],

        [(1, 1, 0),    # Z-shape
         (0, 1, 1),
         (0, 0, 0)],

        [(0, 1, 1),    # S-shape
         (1, 1, 0),
         (0, 0, 0)],

        [(1, 1, 1),    # L-shape
         (1, 0, 0),
         (0, 0, 0)],

        [(1, 1, 1),    # J-shape
         (0, 0, 1),
         (0, 0, 0)],

        [(1, 1, 1, 1)] # T-shape
    ]

    # Game variables
    board = [[0] * (LCD_WIDTH // 10) for _ in range(LCD_HEIGHT // 10)]  # Empty game board
    current_block = 0  # Current falling block
    block_x, block_y = 0, 0  # Current block position

    # Function to draw a block on the screen
    def draw_block(x, y, shape, color):
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    draw.rectangle((x + j * 10, y + i * 10, x + (j + 1) * 10, y + (i + 1) * 10), outline=BLACK, fill=color)

    # Function to check if a position is valid for the current block
    def is_valid_position(x, y, shape):
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    if x + j < 0 or x + j >= len(board[0]) or y + i >= len(board) or board[y + i][x + j]:
                        return False
        return True


    # Flag to indicate if the game has started
    game_started = False
    # Counter for cleared lines
    cleared_lines = 0
    while True:
        # Check if the game has started
        if not game_started:
            draw.text((LCD_WIDTH // 2 - 60, LCD_HEIGHT // 2 - 10), "PRESS BUTTON TO START", fill=WHITE)
            disp.display()
            time.sleep(.1)
            if any(panel.pins()):  # Check if any button is pressed to start the game
                game_started = True
                last_drop_time = time.time()  # Start the timer for block dropping
                board = [[0] * (LCD_WIDTH // 10) for _ in range(LCD_HEIGHT // 10)]  # Reset the game board
                current_block = 0  # Reset the current block
                cleared_lines = 0  # Reset the cleared lines counter
                continue  # Skip the rest of the loop until the game starts

        # Check for input
        if panel.pins()[3]:  # Up button
            pass  # Rotate block
        elif panel.pins()[5]:  # B button
            if is_valid_position(block_x - 1, block_y, BLOCKS[current_block]):
                block_x -= 1  # Move block left
        elif panel.pins()[10]:  # A button
            if is_valid_position(block_x + 1, block_y, BLOCKS[current_block]):
                block_x += 1  # Move block right
        elif panel.pins()[9]:  # Right button
            # Rotate block clockwise
            rotated_block = [[BLOCKS[current_block][col][row] for col in range(len(BLOCKS[current_block]))] for row in range(len(BLOCKS[current_block][0])-1, -1, -1)]
            if is_valid_position(block_x, block_y, rotated_block):
                BLOCKS[current_block] = rotated_block
        elif panel.pins()[8]:  # Left button
            # Rotate block counterclockwise
            rotated_block = [[BLOCKS[current_block][col][row] for col in range(len(BLOCKS[current_block])-1, -1, -1)] for row in range(len(BLOCKS[current_block][0]))]
            if is_valid_position(block_x, block_y, rotated_block):
                BLOCKS[current_block] = rotated_block
        elif panel.pins()[13]:  # Quit
            return

        # Automatic block dropping
        if game_started and time.time() - last_drop_time > 0.25:  # Drop every 1 second after the game has started
            if is_valid_position(block_x, block_y + 1, BLOCKS[current_block]):
                block_y += 1  # Move block down
                last_drop_time = time.time()

        # Update game logic
        # Check if the current block needs to be moved down or if it has reached the bottom or another block
        if game_started and (current_block is None or not is_valid_position(block_x, block_y + 1, BLOCKS[current_block])):
            # Add the current block to the board
            for i in range(len(BLOCKS[current_block])):
                for j in range(len(BLOCKS[current_block][0])):
                    if BLOCKS[current_block][i][j]:
                        board[block_y + i][block_x + j] = 1

            # Check for completed rows and clear them
            cleared = 0
            for i in range(len(board)):
                if all(board[i]):
                    cleared += 1
                    del board[i]
                    board.insert(0, [0] * (LCD_WIDTH // 10))
            cleared_lines += cleared

            # Check if the game is over (blocks reached the top)
            if any(board[0]):
                # Game over
                draw.text((LCD_WIDTH // 2 - 30, LCD_HEIGHT // 2 - 10), "GAME OVER", fill=WHITE)
                disp.display()
                time.sleep(5)
                return

            # Generate a new falling block
            current_block = random.randint(0, len(BLOCKS) - 1)  # Choose random block
            block_x, block_y = (LCD_WIDTH // 10 - len(BLOCKS[current_block][0])) // 2, 0
            last_drop_time = time.time()

        # Draw the game board
        draw.rectangle((0, 0, LCD_WIDTH, LCD_HEIGHT), outline=BLACK, fill=BLACK)
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j]:
                    draw.rectangle((j * 10, i * 10, (j + 1) * 10, (i + 1) * 10), outline=BLACK, fill=WHITE)

        # Draw the falling block
        if game_started:
            draw_block(block_x * 10, block_y * 10, BLOCKS[current_block], color=RED)

        # Draw the cleared lines indicator
        if game_started:
            draw.text((10, 10), f"Cleared Lines: {cleared_lines}", fill=WHITE)
            # Update the display
            disp.display()
            disp.clear()

