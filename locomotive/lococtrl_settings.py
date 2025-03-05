import board

# Change this file to set up for your locomotive

# Speed ramp up/down time in seconds ( more for a "heavier" train )
ramptime = 0

# Locomotive Name (displayed on controller, doesn't like # char)
loconame = "RS3 v1"

# Headlights
hl4 = board.A3 # Extra
hl3 = board.A2 # Extra
hl2 = board.D13 # This one fades when BLE is waiting to pair
hl1 = board.D12 # This one fades when BLE is waiting to pair, and flashes when the battery is low

# Motors
enable = board.D9 # Motor controller enable
forward = board.D10 # Forward PWM signal
reverse = board.D11 # Reverse PWM signal
motor_frequency = 200 # YMMV

# Battery Voltage
batt = board.A0 # Analog in pin, use a voltage divider
batt_magic = 47321 # Adjust this to calibrate voltage, batt_magic = 4096 * (R1 + R2) / R2
batt_limit = -1 # Drive disabled below this voltage, set to -1 to disable
