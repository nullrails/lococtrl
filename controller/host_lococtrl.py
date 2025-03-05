#!/usr/bin/python

# Common variables
install_dir = '/home/pi/lococtrl/controller'
default_unit_num = '1'

# Import "libraries"
import sys
sys.path.append(install_dir)
import input_lib as panel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from time import sleep
from time import ctime
import os

ble = BLERadio()

uart_connection = None
name = "Disconnected"

try:
    unit_num = sys.argv[1]
except IndexError:
    print("No unit number selected, selecting unit 1")
    unit_num = default_unit_num 

print("BLE Loco Controller v0.1")
print("Unit: " + str(unit_num))

def cmdLoop():
    global uart_connection
    oldpins = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    oldpots = [0,0]
    count = 101
    h1 = 75
    h2 = 75
    if uart_connection and uart_connection.connected:
        uart_service = uart_connection[UARTService]
        while uart_connection.connected:
            pins = panel.pins()
            pots = panel.pots()
            changed = False
            battcheck = False
            icount = 0
            try:
                for i in pots:
                    if i != oldpots[icount]:
                        if unit_num == '1':
                            pot = 1
                        if unit_num == '2':
                            pot = 0
                        if icount == pot:
                            uart_service.write(("t," + str(i) + ",0\n").encode("utf-8"))
                    icount += 1
                icount = 0
                for i in pins:
                    if i != oldpins[icount]:
                        if unit_num == '1':
                            dir1 = 11
                            dir2 = 12
                            hlss = 8
                            hls1 = 13
                            hls2 = 14
                            pot = 1
                        if unit_num == '2':
                            dir1 = 6
                            dir2 = 7
                            hlss = 3
                            hls1 = 0
                            hls2 = 1
                            pot = 0
                        changed = True
                        set1 = h1
                        set2 = h2
                        if icount == dir1:
                            if pins[dir1]:
                                uart_service.write(("d,1\n").encode("utf-8"))
                            elif not pins[dir2]:
                                uart_service.write(("d,0\n").encode("utf-8"))
                        elif icount == dir2:
                            if pins[dir2]:
                                uart_service.write(("d,2\n").encode("utf-8"))
                            elif not pins[dir1]:
                                uart_service.write(("d,0\n").encode("utf-8"))
                        elif icount == hls1:
                            if pins[hls1]:
                                uart_service.write(("1," + str(h1) + "\n").encode("utf-8"))
                            else:
                                uart_service.write(("1,0\n").encode("utf-8"))
                        elif icount == hls2:
                            if pins[hls2]:
                                uart_service.write(("2," + str(h2) + "\n").encode("utf-8"))
                            else:
                                uart_service.write(("2,0\n").encode("utf-8"))
                        elif icount == hlss:
                            while panel.pins()[hlss]:
                                if pins[hls1]:
                                    set1 = panel.pots()[pot]
                                    uart_service.write(("1," + str(set1) + "\n").encode("utf-8"))
                                if pins[hls2]:
                                    set2 = panel.pots()[pot]
                                    uart_service.write(("2," + str(set2) + "\n").encode("utf-8"))
                                writeLights(set1,set2)
                                sleep(.01)

                    icount += 1
                if not changed:
                    uart_service.write(("v\n").encode("utf-8"))
                    battcheck = True

                resp = (uart_service.readline().decode("utf-8")).rstrip()

                if battcheck and count >= 100:
                    try:
                        # Check if the string starts with a digit
                        if resp[0].isdigit():
                            # Split the string at 'v' and convert the voltage part to float
                            voltage = float(resp.split('v')[0])
                            # Check if the voltage is within the valid range
                            if 0.00 <= voltage <= 14.00:
                                volts = f"{voltage:.2f}v"
                                f = open('/tmp/lococtrl_batt_' + unit_num,'w')
                                f.write(resp)
                                f.close()
                                count = -1
                    except (IndexError, ValueError):
                        pass  # If any error occurs, return False

                if count >= 50:
                    try:
                        f = open('/tmp/lococtrl_hl_' + unit_num, 'r')
                        strlist = f.read().split()
                        f.close()
                        intlist = []
                        for i in strlist:
                            intlist.append(int(i))
                        h1,h2 = intlist
                    except FileNotFoundError:
                        h1,h2 = 75,75
                count += 1
                sleep(.03)


            except Exception as e:
                print("Exception in cmdLoop: " + e)
                os.remove('/tmp/lococtrl_connected_name_' + unit_num, 'w')
                uart_connection = None
                clean_exit("Connection lost or BLE error")

            oldpins = pins
            oldpots = pots

def writeName(msg):
    f = open('/tmp/lococtrl_connected_name_' + unit_num,'w')
    f.write(msg)
    f.close

def writeLights(l1=75,l2=75):
    f = open('/tmp/lococtrl_hl_' + unit_num,'w')
    f.write(str(l1) + " " + str(l2))
    f.close()

def main():
    global uart_connection
    global name
    name = "Disconnected"
    try:
        os.remove('/tmp/lococtrl_connected_name_' + unit_num)
    except:
        pass
    while True:
        if not uart_connection:
            print("Trying to connect...")
            for adv in ble.start_scan(ProvideServicesAdvertisement):
                if UARTService in adv.services:
                    uart_connection = ble.connect(adv)
                    name = adv.complete_name
                    writeName(name)
                    f = open('/tmp/lococtrl_batt_' + unit_num,'w')
                    f.write('0.00')
                    f.close()
                    print("Connected to: " + name)
                    break
            ble.stop_scan()

        cmdLoop()

def clean_exit(source="Idk"):
    print("Disconnecting and exiting")
    print(f"Shutdown reason: {source}")
    ble.stop_scan()
    if uart_connection and uart_connection.connected:
        uart_connection.disconnect()
    writeName("Disconnected")
    try:
        os.remove('/tmp/lococtrl_connected_name_' + unit_num)
        os.remove('/tmp/lococtrl_hl_' + unit_num)
    except FileNotFoundError:
        pass
    f = open('/tmp/lococtrl_batt_' + unit_num,'w')
    f.write('0.00')
    f.close()
    exit

try:
    main()
except KeyboardInterrupt:
    clean_exit("User shutdown")
