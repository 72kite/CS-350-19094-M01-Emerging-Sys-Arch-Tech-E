#
# SerialLightControl-Client.py - This is the Python code that will be used
# to control the LED circuit from Milestone 1 throught the Serial connection
# via the USB -> TTL cable utilizing the Raspberry Pi's UART.
#
# This script will loop prompting the user to enter one of four commands:
#
#       on, off, exit, quit
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

# Load the time module so that we can utilize the sleep method to 
# inject a pause into our operation
import time

# This imports the Python serial package to handle communications over the
# Raspberry Pi's serial port. 
import serial

# Because we imported the entire package instead of just importing Serial and
# some of the other flags from the serial package, we need to reference those
# objects with dot notation.
#
# e.g. ser = serial.Serial
#
ser = serial.Serial(
        port='/dev/ttyUSB0', # This command assumes that the USB -> TTL cable
                             # is installed and the device that it uses is 
                             # /dev/ttyUSB0. This is the case with the USB -> TTL
                             # cable and Raspberry Pi 4B included in your kit.
        baudrate = 115200,   # This sets the speed of the serial interface in
                             # bits/second
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes 
        timeout=1          # Configure a 1-second timeout
)

# Setup loop variable
repeat = True

# Loop until the user enters a keyboard interrupt with CTRL-C
while repeat:
        try:
                # Configure our output string to be a simple line and increment
                # the counter each time through the loop
                outline = str(input('Light Control, Enter: on, off, exit, or quit - '))

                # Use the encode method of the string datatype to turn our output
                # into a byte array and write it to our serial output.
                ser.write(outline.encode())

                # If we choose exit or quit, exit our loop
                if (outline.lower()).startswith('exit') or (outline.lower()).startswith('quit'):
                        # exit cleanly
                        repeat = False

        except KeyboardInterrupt:
                # We only reach here when the user has processed a Keyboard
                # Interrupt by pressing CTRL-C, so Exit cleanly
                repeat = False