import input_lib as panel
import screens_lib as screens

# Real Imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
from time import sleep
import math
import os

# LCD Driver
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Theme color variables
bg_color = (60,60,60)
fg_color = (255,255,0)
hl_color = (0,0,0)
text_active = (0,0,0)
text_inactive = (255,255,255)

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

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

disp.display()

# Define menu options
menu_options = ["YES", "NO"]
num_options = len(menu_options)

# Define menu parameters
menu_font = ImageFont.truetype('EMDECO.ttf', 12)
menu_font2 = ImageFont.truetype('EMDECO.ttf', 17)
menu_item_height = 16
menu_item_spacing = 2
menu_start_y = 30  # Updated starting position
menu_end_y = height - 10
menu_top_index = 0

# Function to draw the menu
def draw_menu(selected_index):
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Draw title box
    draw.rectangle((0, 0, (width - 1), menu_start_y - 2), outline=hl_color, fill=hl_color)
    draw.text((5, 5), "SHUTDOWN!", fill=text_inactive, font=menu_font2)

    # Draw menu items
    for i in range(num_options):
        y = menu_start_y + (menu_item_height + menu_item_spacing) * i
        if i == selected_index:
            draw.rectangle((0, y, (width - 1), y + menu_item_height), outline=hl_color, fill=fg_color)
            draw.text((5, y), menu_options[i], fill=text_active, font=menu_font2)
        else:
            draw.text((5, y), menu_options[i], fill=text_inactive, font=menu_font)

    disp.display(image)

def run():
    menu_top_index = 0
    # Initial draw
    draw_menu(menu_top_index)
    # Main loop
    sleep(1)
    selected_option_index = 0
    oldpins = []
    while True:
        # Check for button presses
        pins = panel.pins()
        if pins != oldpins:
            if pins[4]:  # Scroll up
                if selected_option_index > 0:
                    selected_option_index -= 1
                    if selected_option_index < menu_top_index:
                        menu_top_index -= 1
                        draw_menu(selected_option_index)
            elif pins[5]:  # Scroll down
                if selected_option_index < num_options - 1:
                    selected_option_index += 1
                    if selected_option_index >= menu_top_index:
                        menu_top_index += 1
                        draw_menu(selected_option_index)
            elif pins[9]:  # Back
                # Handle back button press if needed
                break
            elif pins[10]:  # Enter
                if menu_options[selected_option_index] == "YES":
                    disp.display(screens.genShutdownScreen())
                    sleep(5)
                    os.system('sudo poweroff')
                    return True
                if menu_options[selected_option_index] == "NO":
                    return False
        oldpins = pins
        time.sleep(0.01)  # Adjust as needed for responsiveness
