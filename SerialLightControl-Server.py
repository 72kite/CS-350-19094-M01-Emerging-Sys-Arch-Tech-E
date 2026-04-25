#
# SerialLightControl-Server.py - This is the code to complete
# Milestone Two.
# 
# This Python code will be used to control the light in the circuit 
# that you built on your solderless breadboard in Milestone One based 
# on the instructions read from the serial port of your Raspberry pi.
#
# This script requires that you have correctly configured your Serial
# port and have a USB -> TTL cable connected appropriately.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#    2          Completed state machine: ON, OFF, EXIT/QUIT handlers
#    3          Replaced match/case with if/elif for Python 3.9 compatibility
#------------------------------------------------------------------

# This imports the Python serial package to handle communications over the
# Raspberry Pi's serial port. 
import serial

# Load the GPIO interface from the Raspberry Pi Python Module
# The GPIO interface will be available through the GPIO object
import RPi.GPIO as GPIO

# Because we imported the entire package instead of just importing Serial and
# some of the other flags from the serial package, we need to reference those
# objects with dot notation.
#
# e.g. ser = serial.Serial
#
ser = serial.Serial(
        port='/dev/ttyS0', # This would be /dev/ttyAM0 prior to Raspberry Pi 3
        baudrate = 115200, # This sets the speed of the serial interface in
                           # bits/second
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes 
        timeout=1          # Configure a 1-second timeout
)

# Setup the GPIO interface
#
# 1. Turn off warnings for now - they can be useful for debugging more
#    complex code.
# 2. Tell the GPIO library we are using Broadcom pin-numbering. The 
#    Raspberry Pi CPU is manufactured by Broadcom, and they have a 
#    specific numbering scheme for the GPIO pins. It does not match
#    the layout on the header. However, the Broadcom pin numbering is
#    what is printed on the GPIO Breakout Board, so this should match!
# 3. Tell the GPIO library that we are using GPIO line 18, and that 
#    we are using it for Output. When this state is configured, setting
#    the GPIO line to true will provide positive voltage on that pin.
#    Based on the circuit we have built, positive voltage on the GPIO
#    pin will flow through the LED, through the resistor to the ground
#    pin and the LED will light up. 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# Configure our loop variable
repeat = True

# Loop until the user hits CTRL-C or the client sends an exit/quit message
while repeat:

        # Read lines from the serial port 1 at a time.
        # This will block until we have data available.
        try:
                # Read a line from the serial port. 
                # This also decodes the result into a utf-8 String (utf-8 is the
                # default North American English character set) and
                # normalizes the input to lower case.
                command = ((ser.readline()).decode("utf-8")).lower()

                # This is a state-machine implementation using if/elif.
                # Each branch represents a state. We compare the command
                # string to each known value and act accordingly.
                # The final else represents the default case - unknown input.

                if command == "off":
                        # Set GPIO line 18 to False - disable output voltage
                        # This turns off voltage output to whatever may be 
                        # connected to GPIO line 18.
                        GPIO.output(18, False)

                elif command == "on":
                        # Set GPIO line 18 to True - enable output voltage
                        # This turns on voltage output to whatever may be 
                        # connected to GPIO line 18.
                        GPIO.output(18, True)

                elif command == "exit" or command == "quit":
                        # Cleanup the GPIO pins used in this application and 
                        # exit cleanly
                        GPIO.output(18, False)  # Ensure LED is OFF before exiting
                        GPIO.cleanup()          # Release all GPIO lines
                        repeat = False          # End the while loop cleanly

                else:
                        # No valid commands in the input so do nothing
                        pass

        except KeyboardInterrupt:
                # Exit cleanly when the user enters CTRL-C
                # Cleanup the GPIO pins used in this application and 
                # exit cleanly
                GPIO.output(18, False)
                GPIO.cleanup()
                repeat = False