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
import drive_lib as drive
import screens_lib as screens
import shutdown_lib as shutdown
import screensaver_lib as screensaver
import pairing_lib as pairing
import brickbreaker_lib as brickbreaker
import other_menu_lib as others

# Real Imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
from time import time,sleep,localtime,strftime
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

bt_thread = None
bt_thread1 = None
bt_thread2 = None
shutdown_now = False

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display.
disp.begin()
disp.clear()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

disp.display()

# Define menu options
menu_options = ["DRIVE", "PAIR", "SETTINGS", "OTHER","SHUTDOWN"]
num_options = len(menu_options)

# Define menu parameters
small_font = ImageFont.load_default()  # Use a suitable font
menu_font = ImageFont.truetype('EMDECO.ttf', 12)
menu_font2 = ImageFont.truetype('EMDECO.ttf', 17)
menu_item_height = 16
menu_item_spacing = 2
menu_start_y = 10
menu_end_y = height - 10
menu_top_index = 0

def draw_menu(selected_index):
    battery_voltage = panel.battery()
    current_time = strftime("%I:%M %p", localtime())  # Get current local time in 12-hour format
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

    # Draw bottom bar
    bottom_bar_height = 14
    draw.rectangle((0, height - bottom_bar_height, width, height), fill=(0,0,0))
    battery_text = f"B: {battery_voltage:.2f}V"
    time_text = current_time
    battery_text_width = draw.textsize(battery_text, font=small_font)[0]
    time_text_width = draw.textsize(time_text, font=small_font)[0]
    draw.text((5, height - bottom_bar_height + 2), battery_text, fill=text_inactive, font=small_font)
    draw.text((width - time_text_width - 5, height - bottom_bar_height + 2), time_text, fill=text_inactive, font=small_font)

    disp.display(image)

# Splash then menu
splash = screens.genMsgScreen('Starting LocoCTRL v0.3')
disp.display(splash)
sleep(1)
draw_menu(menu_top_index)

# Main loop
selected_option_index = 0
try:
    name = "N/C"
    oldpins = []
    then = round(time())
    count = 0
    while True:
        now = round(time())
        if now - then > 60:
            screensaver.run()
            oldpins = []
            then = round(time())
            draw_menu(selected_option_index)
        pins = panel.pins()
        if pins != oldpins or pins[4] or pins[5] or count >= 600:
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
                # Not used
                pass
            elif pins[10]:  # Enter
                if menu_options[selected_option_index] == "DRIVE":
                    try:
                        drive.run()
                    except FileNotFoundError:
                        disp.display(screens.genMsgScreen("No locomotive paired!"))
                        sleep(1.5)
                    draw_menu(selected_option_index)
                if menu_options[selected_option_index] == "SHUTDOWN":
                    shutdown_now = shutdown.run()
                    draw_menu(selected_option_index)
                if menu_options[selected_option_index] == "OTHER":
                    sleep(.5)
                    others.run()
                    draw_menu(selected_option_index)
                if menu_options[selected_option_index] == "SETTINGS":
                    sleep(.5)
                    screensaver.run()
                    draw_menu(selected_option_index)
                if menu_options[selected_option_index] == "PAIR":
                    bt_thread1, bt_thread2 = pairing.run(bt_thread1, bt_thread2)
                    draw_menu(selected_option_index)
            if count >= 60:
                count = 0
                draw_menu(selected_option_index)
            else:
                then = round(time())

        oldpins = pins
        count += 1
        sleep(0.01)  # Adjust as needed for responsiveness
except KeyboardInterrupt:
    print("Shutting down")
    if not shutdown_now:
        disp.clear()
        disp.display()
    exit
