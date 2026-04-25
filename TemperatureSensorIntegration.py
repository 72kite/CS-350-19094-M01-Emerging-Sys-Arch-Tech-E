#
# TemperatureSensorIntegration.py - This is the Python code template 
# used to demonstrate the integration of the temperature sensor with
# some of our other components. 
#
# The goal of this module will be to display the temperature on our 
# 16x2 display, and when the button is pressed switch between 
# displaying the temperature in Celsius or Fahrenheit. 
#
# We will manage transitions between temperature scales with a state
# machine.
#
# This code works with the test circuit that was built for module 6.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#    2          UPGRADE: Added functional LED state indicators
#    3          UPGRADE: Added robust I2C error handling
#------------------------------------------------------------------

##
## Imports required to handle our Button, and our LED devices
##
from gpiozero import Button, LED

##
## Imports required to allow us to build a fully functional state machine
##
from statemachine import StateMachine, State

##
## Import required to allow us to pause for a specified length of time
##
import sys
from time import sleep
from datetime import datetime

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
import board
import digitalio
import busio
import adafruit_character_lcd.character_lcd as characterlcd

##
## This is the package we need for our Temperature Sensor
##
import adafruit_ahtx0

##
## Threads are required so that we can manage multiple tasks
## at the same time
##
from threading import Thread

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

##
## ManagedDisplay - Class intended to manage the 16x2 
## Display
##
class ManagedDisplay():
    ##
    ## Class Initialization method to setup the display
    ##
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Modify this if you have a different sized character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2 

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        # wipe LCD screen before we start
        self.lcd.clear()

    ##
    ## cleanupDisplay - Method used to cleanup the digitalIO lines that
    ## are used to run the display.
    ##
    def cleanupDisplay(self):
        # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()
        
    ##
    ## clear - Convenience method used to clear the display
    ##
    def clear(self):
        self.lcd.clear()

    ##
    ## updateScreen - Convenience method used to update the message.
    ##
    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

    ## End class ManagedDisplay definition  
    

##
## TempMachine - This is our StateMachine implementation class.
##
class TempMachine(StateMachine):
    "A state machine designed to manage temperature messages and LED indicators"

    ## Our two LEDs, utilizing GPIO 18, and GPIO 23
    ##
    redLight = LED(18)
    blueLight = LED(23)

    ##
    ## Set the contents of our scale
    ##
    scale1 = 'F'
    scale2 = 'C'

    ##
    ## keep track of the active scale
    ##
    activeScale = scale2

    ##
    ## Define these states for our machine.
    ##
    Celsius = State(initial = True)
    Fahrenheit = State()

    ##
    ## Configure our display
    ##
    screen = ManagedDisplay()

    ##
    ## Configure our temperature sensor (Upgraded with Error Handling)
    ##
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        thSensor = adafruit_ahtx0.AHTx0(i2c)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Could not connect to the AHTx0 Sensor.")
        print(f"System Error Message: {e}")
        print("Please check that your QWIIC cable is securely plugged in.")
        sys.exit(1)

    ##
    ## doDot - Event that moves between scales
    ##
    cycle = (
        Celsius.to(Fahrenheit) | Fahrenheit.to(Celsius)
    )

    ##
    ## on_enter_Celsius - Action performed when entering the Celsius state
    ##
    def on_enter_Celsius(self):
        # Change scale and update LEDs (Blue ON, Red OFF)
        self.activeScale = self.scale2
        self.blueLight.on()
        self.redLight.off()
        if(DEBUG):
            print("* Changing state to Celsius")

    ##
    ## on_enter_Fahrenheit - Action performed when entering the Fahrenheit state
    ##
    def on_enter_Fahrenheit(self):
        # Change scale and update LEDs (Red ON, Blue OFF)
        self.activeScale = self.scale1
        self.redLight.on()
        self.blueLight.off()
        if(DEBUG):
            print("* Changing state to Fahrenheit")

    ##
    ## processButton - Trigger a change in state
    ##
    def processButton(self):
        if(DEBUG):
            print('*** processButton Triggered')
        self.send("cycle")

    ##
    ## run - kickoff the display management thread
    ##
    def run(self):
        # Initialize the correct LED state on startup
        self.blueLight.on()
        self.redLight.off()
        myThread = Thread(target=self.displayTemp)
        myThread.start()

    ##
    ## Get the temperature in Fahrenheit
    ##
    def getFahrenheit(self):
        t = self.thSensor.temperature
        return (((9/5) * t) + 32)

    ##
    ## Get the temperature in Celsius
    ##
    def getCelsius(self):
        return self.thSensor.temperature

    ##
    ## Get the Relative Humidity
    ##
    def getRH(self):
        return self.thSensor.relative_humidity

    ##
    ## Flag to indicate whether or not to shutdown the thread
    ##
    endDisplay = False

    ##
    ## displayTemp - loop to continuously update the display
    ##
    def displayTemp(self):

        while not self.endDisplay:

            ## Setup line 1
            line1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

            ## Setup line 2
            if self.activeScale == 'C':
                line2 = f"T:{self.getCelsius():0.1f}C H:{self.getRH():0.1f}%"
            else:
                line2 = f"T:{self.getFahrenheit():0.1f}F H:{self.getRH():0.1f}%"

            self.screen.updateScreen(line1 + line2)
            sleep(1)

        ## Cleanup the display i.e. clear it
        self.screen.cleanupDisplay()

    ## End class TempMachine definition


##
## Initialize our State Machine, and begin transmission
##
tempMachine = TempMachine()
tempMachine.run()

##
## greenButton - setup our Button, tied to GPIO 24.
##
greenButton = Button(24)
greenButton.when_pressed = tempMachine.processButton

##
## Setup loop variable
##
repeat = True

##
## Repeat until the user creates a keyboard interrupt (CTRL-C)
##
while repeat:
    try:
        if(DEBUG):
            print("Killing time in a loop...")
        sleep(20)
    except KeyboardInterrupt:
        print("\nCleaning up. Exiting...")
        repeat = False
        
        ## Cleanly exit the state machine
        tempMachine.endDisplay = True
        sleep(1)