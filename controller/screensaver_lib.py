from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import random
import math

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import input_lib as panel

# Screen configuration
WIDTH = 128
HEIGHT = 160
width = WIDTH
height = HEIGHT
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

disp.clear()
disp.display()

def rotate_point(point, angle, origin):
    """
    Rotate a point around an origin by a given angle.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy

def run():
    # Create an empty image
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    # Define the number of lines and animation steps
    num_lines = 30
    animation_steps = 200

    # Initialize lists to store line coordinates, colors, and rotation angles
    lines = []
    for _ in range(num_lines):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        angle = random.uniform(0, 2 * math.pi)
        lines.append(((x1, y1), (x2, y2), color, angle))

    # Loop for animation
    #for step in range(animation_steps):
    oldpins = panel.pins()
    while True:
        pins = panel.pins()
        if pins != oldpins:
            break
        # Clear the screen
        draw.rectangle((0, 0, width, height), fill="black")

        # Move lines and draw them
        for i, (p1, p2, color, angle) in enumerate(lines):
            # Rotate the line slightly
            rotated_p1 = rotate_point(p1, 0.05, (width / 2, height / 2))
            rotated_p2 = rotate_point(p2, 0.05, (width / 2, height / 2))

            # Move the lines
            lines[i] = ((rotated_p1[0] + random.randint(-3, 3), rotated_p1[1] + random.randint(-3, 3)),
                        (rotated_p2[0] + random.randint(-3, 3), rotated_p2[1] + random.randint(-3, 3)),
                        color, angle)

            # Draw the lines
            draw.line((lines[i][0], lines[i][1]), fill=lines[i][2])

        # Display the image
        disp.display(image)

        # Uncomment the following line if you want to save the frames as images
        # image.save(f"frame_{step}.png")

        # Pause briefly before the next frame
        time.sleep(0.01)

    # Close the image
    disp.clear()
    disp.display()
    image.close()

