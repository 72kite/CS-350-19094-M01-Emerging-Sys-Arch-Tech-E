#
# ThermostatServer-Simulator.py - This is the Python code used to simulate 
# the Thermostat Server. It reads the data the thermostat sends over the 
# serial port and acknowledges receipt to confirm the connection is alive.
#
# This script will loop until the user interrupts the program by 
# pressing CTRL-C.
#

import time
import serial

# Configure the serial connection
ser = serial.Serial(
        port='/dev/ttyUSB0', 
        baudrate = 115200,   
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1 # 1-second timeout for readline
)

print("Thermostat Server Simulator Started. Listening for data...")

# Initialize variables to track connection status
last_heartbeat = time.time()
thermostat_active = True
repeat = True

while repeat:
    try:
        # Read a line from the serial port
        dataline = ((ser.readline()).decode("utf-8")).lower().strip()

        if(len(dataline) > 1):
            # We received data, update the clock and the status
            print(f"[{time.strftime('%H:%M:%S')}] Received: {dataline}")
            
            # Send 'ACK' so the Thermostat knows the server is alive
            ser.write(b"ACK\n") 
            
            last_heartbeat = time.time()
            thermostat_active = True
            
        else:
            # If readline() times out (returns empty), check how long it's been
            # We allow 35 seconds (30s reporting interval + 5s lag) 
            if (time.time() - last_heartbeat > 35) and thermostat_active:
                print("!!! ALERT: Thermostat Disconnected (No data received for >35s) !!!")
                thermostat_active = False

    except KeyboardInterrupt:
        print("\nExiting Server Simulator...")
        repeat = False