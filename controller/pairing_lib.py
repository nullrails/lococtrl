import input_lib as panel
import screens_lib as screens

# Real Imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
from time import sleep
import math
import os
from subprocess import Popen

# LCD Driver
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Common variables
install_dir = '/home/pi/lococtrl/controller'

# Theme color variables
bg_color = (60,60,60)
fg_color = (255, 255, 0)
hl_color = (0, 0, 0)
text_active = (0, 0, 0)
text_inactive = (255, 255, 255)

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

name = 'N/C'
name1 = "Unpaired"
name2 = "Unpaired"

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
menu_options = ["PAIR", "UNPAIR", "PAIR", "UNPAIR"]
num_options = len(menu_options)

# Define menu parameters
small_font = font = ImageFont.load_default()
menu_font = ImageFont.truetype('EMDECO.ttf', 12)
menu_font2 = ImageFont.truetype('EMDECO.ttf', 14)  # Reduced font size for menu options
menu_item_height = 16
menu_item_spacing = 2
menu_start_y = 30  # Updated starting position
menu_end_y = height - 10
menu_top_index = 0

# Function to draw the menu
def draw_menu(selected_index):
    global name1
    global name2
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Draw title box
    draw.rectangle((0, 0, (width - 1), menu_start_y - 2), outline=hl_color, fill=hl_color)
    draw.text((5, 5), "PAIRING", fill=text_inactive, font=menu_font2)

    # Draw subtitle boxes and informative text
    subtitle_height = 20
    subtitle_box_color = (255, 255, 0)
    draw.rectangle((width // 2, 30, width - 2, 30 + subtitle_height), fill=subtitle_box_color)
    draw.rectangle((2, 30, width // 2 - 2, 30 + subtitle_height), fill=subtitle_box_color)
    draw.text((width // 2 + 5, 35), "Loco 1", fill=(0,0,0), font=menu_font)
    draw.text((5, 35), "Loco 2", fill=(0,0,0), font=menu_font)
    draw.text((width // 2 + 5, 55), name2, fill=text_inactive, font=small_font)
    draw.text((5, 55), name1, fill=text_inactive, font=small_font)

    # Draw menu items for Loco 1
    for i in range(num_options // 2):
        y = 80 + (menu_item_height + menu_item_spacing) * i
        if i + num_options // 2 == selected_index:
            draw.rectangle((width // 2, y, width - 2, y + menu_item_height), outline=hl_color, fill=fg_color)
            draw.text((width // 2 + 5, y), menu_options[i + num_options // 2], fill=text_active, font=menu_font2)
        else:
            draw.text((width // 2 + 5, y), menu_options[i + num_options // 2], fill=text_inactive, font=menu_font)

    # Draw menu items for Loco 2
    for i in range(num_options // 2):
        y = 80 + (menu_item_height + menu_item_spacing) * i
        if i == selected_index:
            draw.rectangle((2, y, width // 2 - 2, y + menu_item_height), outline=hl_color, fill=fg_color)
            draw.text((5, y), menu_options[i], fill=text_active, font=menu_font2)
        else:
            draw.text((5, y), menu_options[i], fill=text_inactive, font=menu_font)

    disp.display(image)

def run(bt_thread1,bt_thread2):
    global name
    global name1
    global name2
    selected_option_index = 0  # Start with "PAIR2" selected
    # Initial draw
    draw_menu(selected_option_index)
    # Main loop
    sleep(1)
    oldpins = []
    count = 0
    while True:
        if count >= 30:
            try:
                f1 = open('/tmp/lococtrl_connected_name_2','r')
                name1 = f1.read()
                f1.close()
            except FileNotFoundError:
                name1 = 'Unpaired'
            try:
                f2 = open('/tmp/lococtrl_connected_name_1','r')
                name2 = f2.read()
                f2.close()
            except FileNotFoundError:
                name2 = 'Unpaired'
            draw_menu(selected_option_index)
            count = 0
        # Check for button presses
        pins = panel.pins()
        if pins != oldpins:
            if pins[4]:  # Scroll up
                if selected_option_index > 0:
                    selected_option_index -= 1
                    draw_menu(selected_option_index)
            elif pins[5]:  # Scroll down
                if selected_option_index < num_options - 1:
                    selected_option_index += 1
                    draw_menu(selected_option_index)
            elif pins[9]:  # Back
                # Handle back button press if needed
                break
            elif pins[10]:  # Enter
                if selected_option_index == 0:
                    try:
                        if bt_thread1.poll() == None:
                            pass
                        else:
                            bt_thread1 = Popen(['python', install_dir + '/host_lococtrl.py', '2'])
                    except:
                        bt_thread1 = Popen(['python', install_dir + '/host_lococtrl.py', '2'])
                    disp.display(screens.genMsgScreen('Pairing Loco 2, press back to cancel'))
                    while True:
                        try:
                            if panel.pins()[9]:
                                bt_thread1.send_signal(2)
                                break
                            f = open('/tmp/lococtrl_connected_name_2','r')
                            name = f.read()
                            f.close()
                            conn_string = 'Connected to ' + name
                            disp.display(screens.genMsgScreen(conn_string))
                            sleep(1.5)
                            break
                        except FileNotFoundError:
                            pass
                    name1 = name
                    draw_menu(selected_option_index)
                if selected_option_index == 1:
                    try:
                        bt_thread1.send_signal(2)
                    except:
                        pass
                    disp.display(screens.genMsgScreen("Unpairing"))
                    sleep(1)
                    draw_menu(selected_option_index)
                if selected_option_index == 2:
                    try:
                        if bt_thread2.poll() == None:
                            pass
                        else:
                            bt_thread2 = Popen(['python', install_dir + '/host_lococtrl.py', '1'])
                    except:
                        bt_thread2 = Popen(['python', install_dir + '/host_lococtrl.py', '1'])
                    disp.display(screens.genMsgScreen('Pairing locomotive 1, press back to cancel'))
                    while True:
                        try:
                            if panel.pins()[9]:
                                bt_thread2.send_signal(2)
                                break
                            f = open('/tmp/lococtrl_connected_name_1','r')
                            name = f.read()
                            f.close()
                            conn_string = 'Connected to ' + name
                            disp.display(screens.genMsgScreen(conn_string))
                            sleep(1.5)
                            break
                        except FileNotFoundError:
                            pass
                    name2 = name
                    draw_menu(selected_option_index)
                if selected_option_index == 3:
                    try:
                        bt_thread2.send_signal(2)
                    except:
                        pass
                    disp.display(screens.genMsgScreen("Unpairing"))
                    sleep(1)
                    draw_menu(selected_option_index)
        count += 1
        oldpins = pins
        time.sleep(0.01)  # Adjust as needed for responsiveness
    return bt_thread1,bt_thread2
