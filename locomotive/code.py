# Locomotive Controller
# (c) 2024 nullrails - tom@joyce.ooo

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import digitalio
import pwmio
import analogio
import board
import supervisor
from time import sleep, time
import lococtrl_settings as settings

# Import settings

# Speed ramp up/down time in seconds ( more for a "heavier" train )
ramptime = settings.ramptime

# Locomotive Name (displayed on controller)
loconame = settings.loconame

# Headlights
hl4 = pwmio.PWMOut(settings.hl4)
hl3 = pwmio.PWMOut(settings.hl3)
hl2 = pwmio.PWMOut(settings.hl2)
hl1 = pwmio.PWMOut(settings.hl1)

# Light to turn on if bluetooth disconnected
bt_status = hl2

# Motors
enable = digitalio.DigitalInOut(settings.enable)
enable.direction = digitalio.Direction.OUTPUT
forward = pwmio.PWMOut(settings.forward, frequency=settings.motor_frequency)
reverse = pwmio.PWMOut(settings.reverse, frequency=settings.motor_frequency)

# Battery Voltage
batt = analogio.AnalogIn(settings.batt)
batt_limit = settings.batt_limit
batt_magic = settings.batt_magic

# Startup Values
enable.value = False
direction = 0
lastdirection = 0
throttle = 0
voltage = 0
fade_direction = 1 
fade_time = 0

def low_batt_led():
    interval = 2
    global voltage
    if supervisor.runtime.serial_connected:
        print("Low battery, motors disabled!")
    while voltage <= batt_limit:
        voltage = round(batt.value / batt_magic * 10,2)

        # Get the current time
        current_time = time()

        # Calculate the time since the last toggle
        time_since_last_toggle = current_time % interval

        # Toggle the LED if the time since the last toggle exceeds half of the period
        if time_since_last_toggle >= interval / 2:
            hl1.duty_cycle = 4000
        else:
            hl1.duty_cycle = 0

def status_led():
    global fade_direction, fade_time
    
    # Get the current time
    current_time = time()
    
    # Calculate the time since the last toggle
    time_since_last_toggle = current_time - fade_time
    
    # Get the current brightness level
    current_brightness = bt_status.duty_cycle
    
    # Calculate the new brightness level
    new_brightness = current_brightness + ( fade_direction * 100 )
    
    # Ensure new brightness stays within valid range
    new_brightness = max(0, min(8000, new_brightness))
    
    # Set the LED brightness
    if new_brightness < 0:
        actual_brightness = 0
    else:
        actual_brightness = new_brightness
    #print(f"Actual: {actual_brightness} New: {new_brightness}")
    actual_brightness_2 = 8000 - actual_brightness
    bt_status.duty_cycle = int(actual_brightness)
    hl1.duty_cycle = int(actual_brightness_2)
    
    # If brightness reaches 0 or 65534, reverse fade direction
    if new_brightness <= 0 or new_brightness >= 8000:
        fade_direction *= -1

def allLights(level = 2 ** 15):
    hl1.duty_cycle = level
    hl2.duty_cycle = level
    hl3.duty_cycle = level
    hl4.duty_cycle = level

def readBatt():
    global direction
    global throttle
    global voltage
    voltage = round(batt.value / batt_magic * 10,2)
    # Stop locomotive and disable drive if battery is below limit
    if voltage <= batt_limit:
        direction = 0
        throttle = 0
        throttleSet()
        allLights(0)
        low_batt_led()
    return voltage

def fadePWM(device,target,seconds=1):
    global throttle
    #print("fadePWM")
    now = device.duty_cycle
    now100 = round((now/65535)*100)
    target100 = round((target/65535)*100)
    if target > now:
        #print("ramp up")
        delay = seconds / (target100 - now100)
        for level in range(now100,target100):
            level100 = int((level/100)*65535)
            device.duty_cycle = level100
            sleep(delay)
    if now > target:
        #print("ramp down")
        delay = seconds / (now100 - target100)
        for level in range(now100,target100,-1):
            level100 = int((level/100)*65535)
            if level100 < 1000:
                device.duty_cycle = 0
                break
            else:
                device.duty_cycle = level100
            sleep(delay)

    throttle = target
    #print("Target reached")

def throttleSet():
    global direction
    global throttle
    global lastdirection
    desired_throttle = throttle
    if direction != lastdirection:
        if lastdirection == 0:
            pass
        if lastdirection == 1:
            fadePWM(forward,0,ramptime)
        if lastdirection == 2:
            fadePWM(reverse,0,ramptime)
    if direction == 0:
        enable.value = False
        forward.duty_cycle = 0
        reverse.duty_cycle = 0
        throttle = 0
    if direction == 1:
        enable.value = True
        reverse.duty_cycle = 0
        fadePWM(forward, desired_throttle, ramptime)
    if direction == 2:
        enable.value = True
        forward.duty_cycle = 0
        fadePWM(reverse, desired_throttle, ramptime)
    lastdirection = direction

def interpret(cmd):
    global direction
    global throttle
    cmdlen = len(cmd)
    # Sorry about this:
    if cmdlen == 1:
        o = cmd[0]
        if o == "1":
            ret = hl1.duty_cycle
        elif o == "2":
            ret = hl2.duty_cycle
        elif o == "3":
            ret = hl3.duty_cycle
        elif o == "4":
            ret = hl4.duty_cycle
        elif o == "d":
            ret = direction
        elif o == "t":
            ret = round((int(throttle)/65535)*100)
        elif o == "v":
            ret = readBatt()
        elif o == "vl":
            ret = batt_limit
        else:
            print("1: " + repr(cmd))
            ret = "Unknown command"
        return str(ret)
    elif cmdlen == 2:
        o = cmd[0]
        l = cmd[1]
        ll = int(eval ("(" + str(l) + "/100)*65535"))
        if o == "1":
            hl1.duty_cycle=ll
        elif o == "2":
            hl2.duty_cycle=ll
        elif o == "3":
            hl3.duty_cycle=ll
        elif o == "4":
            hl4.duty_cycle=ll
        elif o == "d":
            direction = int(l)
            throttleSet()
        elif o == "t":
            throttle = ll
            throttleSet()
        else:
            print("2: " + repr(cmd))
            return "Unknown command"
        return "Ok"
    elif cmdlen == 3:
        o = cmd[0]
        l = cmd[1]
        ll = int(eval ("(" + str(l) + "/100)*65535"))
        s = int(cmd[2])
        if o == "1":
            fadePWM(hl1,ll,s)
        elif o == "2":
            fadePWM(hl2,ll,s)
        elif o == "3":
            fadePWM(hl3,ll,s)
        elif o == "4":
            fadePWM(hl4,ll,s)
        elif o == "t":
            if direction == 1:
                fadePWM(forward,ll,s)
            if direction == 2:
                fadePWM(reverse,ll,s)
        else:
            print("3: " + repr(cmd))
            return "Unknown command"
        return "Ok"
    else:
        print("4: " + repr(cmd))
        return "Unknown command"

# Begin the program

if supervisor.runtime.serial_connected:
    print("Locomotive Controller v0.2")
    print("Serial console connected, Auto-Reload disabled.")
    supervisor.runtime.autoreload = False

ble = BLERadio()
ble.name = loconame
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

while True:
    ble.start_advertising(advertisement)
    allLights(0)
    print("BLE waiting to connect")
    while not ble.connected:
        readBatt()
        status_led()
        sleep(.01)
        pass
    ble.stop_advertising()
    allLights(0)
    print("BLE connected")
    while ble.connected:
        readBatt()
        s = uart.readline()
        if s:
            try:
                result = interpret((str(s.decode("utf-8")).rstrip()).split(","))
            except Exception as e:
                error = repr(e)
                print(error)
            try:
                uart.write(result.encode("utf-8") + "\n".encode("utf-8"))
                #uart.write("Error".encode("utf-8"))
            except Exception as e:
                error = repr(e)
                resor = repr(result)
                print("Result: " + resor)
                print("Error: " + error)
    direction = 0
    throttleSet()
    print("BLE disconnected")
