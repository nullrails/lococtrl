#!/usr/bin/python

# Common variables
install_dir = '/home/pi/lococtrl/controller'
bg_color = (60,60,60)
fg_color = (255,255,0)
hl_color = (0,0,0)
text_active = (0,0,0)
text_inactive = (255,255,255)

# Import "libraries"
import sys
sys.path.append(install_dir)
import input_lib as panel
import test_lib as test
import tetris_lib as tetris
import screens_lib as screens
import screensaver_lib as screensaver
import brickbreaker_lib as brickbreaker

# Real Imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
from time import time
from time import sleep
import math
import os
from subprocess import Popen

# LCD Driver
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Screen settings
WIDTH = 128
HEIGHT = 160
width = WIDTH
height = HEIGHT
SPEED_HZ = 4000000
# SPI Configuration.
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
menu_options = ["TETRIS", "BRICKBREAKER", "TEST","SCREENSAVER"]
num_options = len(menu_options)

# Define menu parameters
#menu_font = ImageFont.load_default()  # Use a suitable font
menu_font = ImageFont.truetype('EMDECO.ttf', 12)
menu_font2 = ImageFont.truetype('EMDECO.ttf', 17)
menu_item_height = 16
menu_item_spacing = 2
menu_start_y = 10
menu_end_y = height - 10
menu_top_index = 0

# Function to draw the menu
def draw_menu(selected_index):
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    # Draw menu items
    for i in range(num_options):
        y = menu_start_y + (menu_item_height + menu_item_spacing) * i
        if i == selected_index:
            draw.rectangle((0, y, (width-1), y + menu_item_height), outline=hl_color, fill=fg_color)
            draw.text((5, y), menu_options[i], fill=text_active, font=menu_font2)
        else:
            draw.text((5, y), menu_options[i], fill=text_inactive, font=menu_font)
    disp.display(image)

def run():
    # Main loop
    selected_option_index = 0
    menu_top_index = 0
    draw_menu(selected_option_index)
    try:
        oldpins = []
        then = round(time())
        while True:
            now = round(time())
            if now - then > 60:
                screensaver.run()
                oldpins = []
                draw_menu(selected_option_index)
            pins = panel.pins()
            if pins != oldpins or pins[4] or pins[5]:
                # Check for button presses
                if pins[4]:  # Scroll up
                    if selected_option_index > 0:
                        selected_option_index -= 1
                        if selected_option_index < menu_top_index:
                            menu_top_index -= 1
                            draw_menu(selected_option_index)
                    else:
                        selected_option_index = num_options - 1
                        menu_top_index = num_options - 1
                        draw_menu(selected_option_index)
                elif pins[5]:  # Scroll down
                    if selected_option_index < num_options - 1:
                        selected_option_index += 1
                        if selected_option_index >= menu_top_index:
                            menu_top_index += 1
                            draw_menu(selected_option_index)
                    else:
                        selected_option_index = 0
                        menu_top_index = 0
                        draw_menu(selected_option_index)
                elif pins[9]:  # Back
                    return
                elif pins[10]:  # Enter
                    if menu_options[selected_option_index] == "TEST":
                        test.run()
                        draw_menu(selected_option_index)
                    if menu_options[selected_option_index] == "TETRIS":
                        tetris.run()
                        draw_menu(selected_option_index)
                    if menu_options[selected_option_index] == "BRICKBREAKER":
                        brickbreaker.run()
                        draw_menu(selected_option_index)
                    if menu_options[selected_option_index] == "SCREENSAVER":
                        sleep(.5)
                        screensaver.run()
                        draw_menu(selected_option_index)
                then = round(time())

            oldpins = pins
            sleep(0.01)  # Adjust as needed for responsiveness
    except KeyboardInterrupt:
        return
