#!/usr/bin/python

# Common variables
install_dir = '/home/pi/lococtrl/controller'

# Import "libraries"
import sys
sys.path.append(install_dir)
import input_lib as panel

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

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

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

# Load default font.
font = ImageFont.load_default()

# Load Images
eegg = Image.open('/home/pi/lococtrl/controller/eegg.png').resize((WIDTH, HEIGHT))

def inStatesToColor(pins):
    colorList = []
    for i in pins:
        if i:
            colorList.append((0,255,0))
        else:
            colorList.append((255,0,0))
    return colorList

def drawTestScreen(pins, pots):
    colorlist = inStatesToColor(pins)
    # Draw indicators.
    # Row 1
    draw.ellipse((5, 5, 25, 25), outline=(255,255,255), fill=(colorlist[0]))
    draw.ellipse((30, 5, 50, 25), outline=(255,255,255), fill=(colorlist[3]))
    draw.ellipse((78, 5, 98, 25), outline=(255,255,255), fill=(colorlist[8]))
    draw.ellipse((103, 5, 123, 25), outline=(255,255,255), fill=(colorlist[13]))
    # Row 2
    draw.ellipse((5, 30, 25, 50), outline=(255,255,255), fill=(colorlist[1]))
    draw.ellipse((30, 30, 50, 50), outline=(255,255,255), fill=(colorlist[4]))
    draw.ellipse((78, 30, 98, 50), outline=(255,255,255), fill=(colorlist[9]))
    draw.ellipse((103, 30, 123, 50), outline=(255,255,255), fill=(colorlist[14]))
    # Row 3
    draw.ellipse((5, 55, 25, 75), outline=(255,255,255), fill=(colorlist[2]))
    draw.ellipse((30, 55, 50, 75), outline=(255,255,255), fill=(colorlist[5]))
    draw.ellipse((78, 55, 98, 75), outline=(255,255,255), fill=(colorlist[10]))
    draw.ellipse((103, 55, 123, 75), outline=(255,255,255), fill=(colorlist[15]))
    # Row 4
    draw.ellipse((17, 80, 37, 100), outline=(255,255,255), fill=(colorlist[6]))
    draw.ellipse((91, 80, 111, 100), outline=(255,255,255), fill=(colorlist[11]))
    # Row 5
    draw.ellipse((17, 105, 37, 125), outline=(255,255,255), fill=(colorlist[7]))
    draw.ellipse((91, 105, 111, 125), outline=(255,255,255), fill=(colorlist[12]))
    # Row 6
    draw.text((23,140), str(pots[0]), font=font, fill=(255,255,255))
    draw.text((97,140), str(pots[1]), font=font, fill=(255,255,255))

def run():
    while True:
        pots = panel.pots()
        pins = panel.pins()
        disp.clear()
        drawTestScreen(pins, pots)
        if pins[0] and pins[1] and pins[2] and pins[13] and pins[14]:
            while panel.pins()[15]:
                disp.display(eegg)
        if pins[9] and pins[13]:
            return
        disp.display()
