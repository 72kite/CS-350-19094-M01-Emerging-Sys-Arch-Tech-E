# CS 350: Emerging Systems Architectures & Technologies
    ## Smart Thermostat Prototype Portfolio
    
    ### Project Overview
    The goal of this project was to develop a functional prototype for a Cyber-Physical Smart Thermostat system. Utilizing a **Raspberry Pi 4**, the system integrates hardware sensors and software logic to regulate environmental temperature based on user-defined set points.
    
    The thermostat supports three primary modes: **Off, Heating, and Cooling**. It utilizes an **AHT20 sensor** for real-time temperature data via the I2C protocol, a **16x2 LCD** for a visual user interface, and three physical buttons for mode toggling and set point adjustment. Additionally, the system broadcasts its status (Current Temp, Set Point, and State) every 30 seconds to a remote server via a **UART serial connection**.
    
    ---
    
    ### Reflection
    
    #### 1. Summarize the project and what problem it was solving.
    This project addressed the need for a low-level prototype of a smart thermostat capable of managing environmental states in real-time. By bridging the gap between hardware (sensors, LEDs, buttons) and software (Python state machines), the system solves the problem of local temperature regulation while providing a foundation for cloud-based IoT integration.
    
    #### 2. What did you do particularly well?
    I excelled at the integration of multi-threaded software with hardware interrupts. Specifically, I successfully implemented a `ManagedDisplay` class to handle LCD updates in a background thread, ensuring that button presses for temperature adjustments remained responsive. I also effectively debugged complex library-specific issues, such as the `BadEventHandler` error in `gpiozero`, by implementing wrapper methods for state machine transitions.
    
    #### 3. Where could you improve?
    While the current prototype is functional, I could improve the User Experience (UX) on the LCD. Implementing a scrolling menu or a more detailed "Configuration Mode" would make the device more intuitive. Additionally, transitioning from simple threshold logic to a PID (Proportional-Integral-Derivative) control algorithm would allow for more precise temperature maintenance.
    
    #### 4. What tools and/or resources are you adding to your support network?
    * **Python Libraries:** `gpiozero` for simplified hardware interaction and `python-statemachine` for robust logic flow.
    * **Hardware Debugging:** Using USB-to-TTL cables for UART serial monitoring and I2C address scanning.
    * **Documentation:** Utilizing official Adafruit CircuitPython documentation and Raspberry Pi GPIO pinout guides.
    
    #### 5. What skills from this project will be particularly transferable?
    The ability to design and implement a **Finite State Machine (FSM)** is highly transferable in software engineering and cybersecurity. Furthermore, the experience of handling asynchronous communication (UART/I2C) and voltage logic protection is fundamental to embedded systems development.
    
    #### 6. How did you make this project maintainable, readable, and adaptable?
    * **Maintainability:** Utilized Object-Oriented Programming (OOP) to isolate logic. If hardware changes, only specific classes (e.g., `ManagedDisplay`) require updates.
    * **Readability:** Maintained consistent naming conventions and detailed comments for GPIO pin mapping and code blocks.
    * **Adaptability:** Included a `DEBUG` flag for console reporting and used comma-delimited UART output for easy server-side parsing.
    
    ---
    
    ### Artifacts Included
    * **Thermostat.py:** The main application logic containing the state machine, hardware drivers, and display management.
    * **ThermostatServer-Simulator.py:** A simulator demonstrating the system's ability to communicate over a serial interface.
    
    ### Hardware Requirements
    * Raspberry Pi 4 (or compatible)
    * 16x2 LCD Display (HD44780 compatible)
    * AHT20 Temperature/Humidity Sensor
    * 3x Momentary Push Buttons
    * 2x LEDs (Red and Blue)
    * 10k Ohm resistors and Potentiometer (for LCD contrast)
    
    ### How to Run
    1.  Connect hardware as specified in the Lab Guides.
    2.  Install required libraries:
        `pip3 install gpiozero python-statemachine adafruit-circuitpython-charlcd adafruit-circuitpython-ahtx0`
    3.  Start the Server Simulator on your PC:
        `python3 ThermostatServer-Simulator.py`
    4.  Run the Thermostat script on the Raspberry Pi:
        `sudo python3 Thermostat.py`
    
