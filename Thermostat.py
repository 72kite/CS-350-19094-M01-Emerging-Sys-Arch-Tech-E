#
# Thermostat.py - Integrated code for the smart thermostat prototype.
#
# Functionality:
# 1. Three states: Off, Heat, Cool.
# 2. Red LED: Pulse if heating/below setpoint; Solid if at/above setpoint.
# 3. Blue LED: Pulse if cooling/above setpoint; Solid if at/below setpoint.
# 4. Buttons: Mode Cycle (Green), SetPoint Increase (Red), SetPoint Decrease (Blue).
# 5. LCD: Line 1: Date/Time. Line 2: Alternates Temp and System State/Setpoint.
# 6. Serial: Sends comma-delimited state string to server every 30 seconds.
# 7. Connection Monitoring: Displays 'SRV DISCONNECTED' if no ACK from server.
#


#
# Thermostat.py - Final Integrated Prototype
#
# --- MUTE DEPRECATION WARNINGS ---
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
# ---------------------------------

from time import sleep
from datetime import datetime
from statemachine import StateMachine, State
import board
import adafruit_ahtx0
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import serial
from gpiozero import Button, PWMLED
from threading import Thread
from math import floor

# Debug flag for console output
DEBUG = True

# Initialize I2C and the AHT20 Temperature Sensor
i2c = board.I2C()
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Initialize UART Serial connection
# Using /dev/ttyS0 for the Pi's internal serial pins
ser = serial.Serial(
        port='/dev/ttyS0', 
        baudrate = 115200, 
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

# Initialize PWM-controlled LEDs
redLight = PWMLED(18) 
blueLight = PWMLED(23)

# --- LCD MANAGEMENT CLASS ---
class ManagedDisplay():
    def __init__(self):
        # Mappings from Module 4 wiring guide [cite: 122-129]
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Initialise 16x2 LCD logic
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 16, 2)
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

screen = ManagedDisplay()

# --- STATE MACHINE CLASS ---
class TemperatureMachine(StateMachine):
    "A state machine for thermostat logic"

    # Define core states
    off = State(initial = True)
    heat = State()
    cool = State()

    # Initial set point per business requirements
    setPoint = 72
    server_connected = True 

    # Transition logic
    cycle = off.to(heat) | heat.to(cool) | cool.to(off)

    # --- BUTTON WRAPPERS ---
    def processTempStateButton(self):
        self.cycle()
        if(DEBUG): print(f"* State changed to {self.current_state.id}")

    def processTempIncButton(self):
        self.setPoint += 1
        self.updateLights()
        if(DEBUG): print(f"* Set Point Increased: {self.setPoint}")

    def processTempDecButton(self):
        self.setPoint -= 1
        self.updateLights()
        if(DEBUG): print(f"* Set Point Decreased: {self.setPoint}")

    def updateLights(self):
        # Determine LED behavior based on mode and temp [cite: 244-249]
        temp = floor(self.getFahrenheit())
        current_id = self.current_state.id
        
        if current_id == 'heat':
            if temp < self.setPoint:
                redLight.pulse() # Fade if below setpoint
            else:
                redLight.value = 1 # Solid if at/above
            blueLight.off()
        elif current_id == 'cool':
            if temp > self.setPoint:
                blueLight.pulse() # Fade if above setpoint
            else:
                blueLight.value = 1 # Solid if at/below
            redLight.off()
        else:
            redLight.off()
            blueLight.off()

    def getFahrenheit(self):
        # Convert AHT20 Celsius to Fahrenheit
        return (((9/5) * thSensor.temperature) + 32)

    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        self.endDisplay = False
        while not self.endDisplay:
            current_time = datetime.now()
            # Date/Time on first line
            lcd_line_1 = current_time.strftime("%b %d  %H:%M:%S\n")
            current_id = self.current_state.id
    
            # Toggle logic for second line
            if not self.server_connected:
                lcd_line_2 = "SRV DISCONNECTED"
            elif(altCounter < 6):
                lcd_line_2 = f"T:{round(self.getFahrenheit(),1)}F"
                altCounter += 1
            else:
                lcd_line_2 = f"{current_id.upper()} SP:{self.setPoint}F"
                altCounter += 1
                if(altCounter >= 11):
                    # Periodically refresh lights to match ambient temp changes
                    self.updateLights()
                    altCounter = 1
    
            screen.updateScreen(lcd_line_1 + lcd_line_2)
    
            # Serial report every 30 seconds [cite: 257-265]
            if((counter % 30) == 0):
                # Comma delimited output: State, Temp, Setpoint
                report = f"{current_id},{round(self.getFahrenheit(),1)},{self.setPoint}\n"
                ser.write(report.encode())
                
                # Handshake check: Expecting ACK from Server Simulator
                sleep(0.5) 
                if ser.in_waiting > 0:
                    ser.read(ser.in_waiting) # Clear the buffer
                    self.server_connected = True
                else:
                    self.server_connected = False
                counter = 1
            else:
                counter += 1
            sleep(1)

        screen.cleanupDisplay()

# --- MAIN SETUP ---
tsm = TemperatureMachine()
# Daemon thread ensures clean shutdown on CTRL-C
Thread(target=tsm.manageMyDisplay, daemon=True).start()

# --- BUTTON ASSIGNMENTS [cite: 250-253] ---
# Green: Mode Cycle (GPIO 24)
greenButton = Button(24)
greenButton.when_pressed = tsm.processTempStateButton

# Red: SetPoint Increase (GPIO 25)
redButton = Button(25)
redButton.when_pressed = tsm.processTempIncButton

# Blue: SetPoint Decrease (GPIO 12)
blueButton = Button(12)
blueButton.when_pressed = tsm.processTempDecButton

try:
    while True:
        sleep(10)
except KeyboardInterrupt:
    tsm.endDisplay = True
    print("\nThermostat shutting down cleanly...")
    sleep(1.5) # Give the display thread a moment to clean up