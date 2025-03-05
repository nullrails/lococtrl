import input_lib as panel
import screens_lib as screens

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import math
from time import sleep,localtime,strftime

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

loco_info_1 = ['N/C','0.00','0','0']
loco_info_2 = ['N/C','0.00','0','0']
loco_1_scroll = 5
loco_2_scroll = 5

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

def draw_gauge(value1, value2):
    bottom_bar_height = 14
    battery_voltage = panel.battery()
    current_time = strftime("%I:%M %p", localtime())  # Get current local time in 12-hour format
    global loco_info_2, loco_info_1, loco_1_scroll, loco_2_scroll
    # Create a blank image
    image = Image.new('RGB', (width, height), color=(60, 60, 60))
    draw = ImageDraw.Draw(image)

    # Define gauge parameters
    center_x = width // 2
    center_y = 70
    radius = min(width, height) // 3
    gauge_width = 10
    scale_length = 10
    scale_count = 10

    # Draw semi-circle gauge
    draw.arc((center_x - radius, center_y - radius, center_x + radius, center_y + radius), start=180, end=0,
             fill=(255, 255, 255), width=2)
    draw.line((center_x - radius, center_y, center_x + radius, center_y), fill=(255, 255, 255), width=2)  # Line across the bottom

    # Draw gauge scale with labels
    scale_start_angle = math.radians(180)
    scale_end_angle = math.radians(0)
    for i in range(scale_count + 1):
        angle = scale_start_angle + (scale_end_angle - scale_start_angle) / scale_count * i
        x1 = center_x + (radius - gauge_width) * math.cos(angle)
        y1 = center_y - (radius - gauge_width) * math.sin(angle)
        x2 = center_x + (radius - gauge_width - scale_length) * math.cos(angle)
        y2 = center_y - (radius - gauge_width - scale_length) * math.sin(angle)
        draw.line((x1, y1, x2, y2), fill=(255, 255, 255), width=2)

        # Label scale
        label = str(int(i * (100 / scale_count)))
        label_width, label_height = draw.textsize(label)
        label_x = center_x + (radius + gauge_width + scale_length * 0.5) * math.cos(angle) - label_width / 2
        label_y = center_y - (radius + gauge_width + scale_length * 0.5) * math.sin(angle) - label_height / 2
        if label == "100":
            label_x = label_x - 2
        draw.text((label_x, label_y), label, fill=(255, 255, 255))

    # Draw gauge needles
    needle_length = radius - gauge_width - scale_length

    # Draw red needle (sweeping up and clockwise)
    needle_angle1 = math.radians(180 - (value1 / 100 * 180))
    needle_x1 = center_x + needle_length * math.cos(needle_angle1)
    needle_y1 = center_y - needle_length * math.sin(needle_angle1)
    draw.line((center_x, center_y, needle_x1, needle_y1), fill=(255, 0, 0), width=3)

    # Draw yellow needle (sweeping up and clockwise)
    needle_angle2 = math.radians(180 - (value2 / 100 * 180))
    needle_x2 = center_x + needle_length * math.cos(needle_angle2)
    needle_y2 = center_y - needle_length * math.sin(needle_angle2)
    draw.line((center_x, center_y, needle_x2, needle_y2), fill=(255, 255, 0), width=3)

    # Draw loco info 2 square
    draw.rectangle((2, (center_y + 10), (center_x - 2), (height - bottom_bar_height - 3)), outline=(255, 255, 0), fill=(60, 60, 60))
    draw.text((7, center_y + 14), "L: ", fill=(255, 255, 255))  # Stationary "L: " label
    loco_name_1 = loco_info_1[0]
    loco_name_1_print = loco_name_1
    if len(loco_name_1) > 6:
        loco_name_1 = loco_name_1[loco_1_scroll:]
        loco_name_1_print = loco_name_1
    if len(loco_name_1) > 6:
        loco_name_1_trunc = loco_name_1[:6]
        loco_name_1_print = loco_name_1_trunc
    draw.text((5 + 20, center_y + 14), loco_name_1_print, fill=(255, 255, 255))  # Scrolling locomotive name

    if len(loco_name_1_print) > 2:
        loco_1_scroll += 1
    else:
        loco_1_scroll = 0

    draw.text((7, center_y + 18 + label_height), ("B: " + str(loco_info_1[1]) + "v"), fill=(255, 255, 255))
    draw.text((7, center_y + 22 + (2 * label_height)), ("H1: " + str(loco_info_1[2])), fill=(255, 255, 255))
    draw.text((7, center_y + 26 + (3 * label_height)), ("H2: " + str(loco_info_1[3])), fill=(255, 255, 255))

    # Draw loco info 1 square
    draw.rectangle(((center_x + 1), (center_y + 10), (width - 3), (height - bottom_bar_height - 3)), outline=(255, 0, 0), fill=(60, 60, 60))
    draw.text((((center_x + 5)), center_y + 14), "L: ", fill=(255, 255, 255))  # Stationary "L: " label
    loco_name_2 = loco_info_2[0]
    loco_name_2_print = loco_name_2
    if len(loco_name_2) > 6:
        loco_name_2 = loco_name_2[loco_2_scroll:]
        loco_name_2_print = loco_name_2
    if len(loco_name_2) > 6:
        loco_name_2_trunc = loco_name_2[:6]
        loco_name_2_print = loco_name_2_trunc
    draw.text((((center_x + 3) + 20), center_y + 14), loco_name_2_print, fill=(255, 255, 255))  # Scrolling locomotive name

    if len(loco_name_2_print) > 2:
        loco_2_scroll += 1
    else:
        loco_2_scroll = 0

    draw.text((((center_x + 5)), center_y + 18 + label_height), ("B: " + str(loco_info_2[1]) + "v"), fill=(255, 255, 255))
    draw.text((((center_x + 5)), center_y + 22 + (2 * label_height)), ("H1: " + str(loco_info_2[2])), fill=(255, 255, 255))
    draw.text((((center_x + 5)), center_y + 26 + (3 * label_height)), ("H2: " + str(loco_info_2[3])), fill=(255, 255, 255))
    # Draw bottom bar
    draw.rectangle((0, height - bottom_bar_height, width, height), fill=(0,0,0))
    battery_text = f"B: {battery_voltage:.2f}V"
    time_text = current_time
    battery_text_width = draw.textsize(battery_text)[0]
    time_text_width = draw.textsize(time_text)[0]
    draw.text((5, height - bottom_bar_height + 2 ), battery_text, fill=(255,255,255))
    draw.text((width - time_text_width - 5, height - bottom_bar_height + 2), time_text, fill=(255,255,255))

    disp.display(image)
    
def run():
    global loco_info_2
    oldpins = []
    oldpots = []
    no1 = False
    no2 = False
    count = 60
    while True:
        pins = panel.pins()
        pots = panel.pots()
        if count >= 8:
            try:
                f = open('/tmp/lococtrl_connected_name_1','r')
                name = f.read()
                if name == "Disconnected":
                    loco_info_2[0] = "N/C"
                else:
                    if len(name) > 6:
                        loco_info_2[0] = "      " + name
                    else:
                        loco_info_2[0] = name
                f.close()
                f = open('/tmp/lococtrl_batt_1','r')
                loco_info_2[1] = f.read()
                f.close()
                no2 = False
            except FileNotFoundError:
                loco_info_2[0] = "N/C"
                loco_info_2[1] = "0.00"
                no2 = True
            try:
                f = open('/tmp/lococtrl_connected_name_2','r')
                name = f.read()
                if name == "Disconnected":
                    loco_info_1[0] = "N/C"
                else:
                    if len(name) > 6:
                        loco_info_1[0] = "      " + name
                    else:
                        loco_info_1[0] = name
                f.close()
                f = open('/tmp/lococtrl_batt_2','r')
                loco_info_1[1] = f.read()
                f.close()
                no1 = False
            except FileNotFoundError:
                loco_info_1[0] = "N/C"
                loco_info_1[1] = "0.00"
                no1 = True
            if no1 and no2:
                disp.display(screens.genMsgScreen("No locomotive paired!"))
                sleep(1.5)
                return
            try:
                f = open('/tmp/lococtrl_hl_1','r')
                hls = f.read().split(' ')
                f.close()
                l1_hl1_set = hls[0]
                l1_hl2_set = hls[1]
            except FileNotFoundError:
                l1_hl1_set = 75
                l1_hl2_set = 75
            try:
                f = open('/tmp/lococtrl_hl_2','r')
                hls = f.read().split(' ')
                f.close()
                l2_hl1_set = hls[0]
                l2_hl2_set = hls[1]
            except FileNotFoundError:
                l2_hl1_set = 75
                l2_hl2_set = 75
            draw_gauge(pots[1],pots[0])
            count = 0
        count += 1
        if pins[0]:
            loco_info_1[2] = l2_hl1_set
        if not pins[0]:
            loco_info_1[2] = 0
        if pins[1]:
            loco_info_1[3] = l2_hl2_set
        if not pins[1]:
            loco_info_1[3] = 0
        if pins[13]:
            loco_info_2[2] = l1_hl1_set
        if not pins[13]:
            loco_info_2[2] = 0
        if pins[14]:
            loco_info_2[3] = l1_hl2_set
        if not pins[14]:
            loco_info_2[3] = 0
        if pins != oldpins or pots != oldpots:
            if pins[9]:
                return
            else:
                yellow_brightness = [0, 40, 60, 100]
                draw_gauge(pots[1],pots[0])
        oldpins = pins
        oldpots = pots
        sleep(.01)
