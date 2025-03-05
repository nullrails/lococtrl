import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

GPIO.setmode(GPIO.BCM)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 1
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

pinlist = [26,20,21,19,13,6,22,5,2,3,4,27,17,18,15,14]

for i in pinlist:
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def pins():
    global pinlist
    now = []
    for i in pinlist:
        state = GPIO.input(i)
        if state == 1:
            now.append(False)
        elif state == 0:
            now.append(True)
    return now

def pots():
    round1 = round(mcp.read_adc(1)/1023 * 100)
    round2 = round(mcp.read_adc(0)/1023 * 100)
    invert1 = 100 - round1
    invert2 = 100 - round2
    return invert1,invert2

def battery():
    level = round(mcp.read_adc(2)*0.01144,2)
    return level
