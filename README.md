# CS 350: Emerging Systems Architectures & Technologies
## Smart Thermostat Prototype Portfolio

### Project Overview
[cite_start]The goal of this project was to develop a functional prototype for a Cyber-Physical Smart Thermostat system[cite: 157]. [cite_start]Utilizing a **Raspberry Pi 4**, the system integrates hardware sensors and software logic to regulate environmental temperature based on user-defined set points[cite: 183, 269]. 

[cite_start]The thermostat supports three primary modes: **Off, Heating, and Cooling**[cite: 159, 251]. [cite_start]It utilizes an **AHT20 sensor** for real-time temperature data via the I2C protocol, a **16x2 LCD** for a visual user interface, and three physical buttons for mode toggling and set point adjustment[cite: 7, 242, 250]. [cite_start]Additionally, the system broadcasts its status (State, Current Temp, and Set Point) every 30 seconds to a remote server via a **UART serial connection** using a comma-delimited string[cite: 257, 258, 259].

---

### Reflection

#### 1. Summarize the project and what problem it was solving.
[cite_start]This project involved building a low-level prototype for a smart thermostat to manage environmental states in real-time[cite: 268, 270]. [cite_start]By bridging the gap between hardware components (sensors, LEDs, buttons) and software logic (Python state machines), the system solves the challenge of local temperature regulation while providing a foundation for cloud-connected IoT architectures[cite: 158, 161, 271].

#### 2. What did you do particularly well?
I excelled at the integration of multi-threaded software with hardware interrupts. Specifically, I implemented a `ManagedDisplay` class to handle LCD updates in a background thread, ensuring that button presses for temperature adjustments remained responsive and did not block the system's execution. I also effectively debugged library-specific issues, such as the `BadEventHandler` error in `gpiozero`, by implementing clean wrapper methods for state transitions.

#### 3. Where could you improve?
While the prototype is fully functional, I could improve the **User Experience (UX)** on the LCD. [cite_start]Implementing a scrolling menu or a more detailed "Configuration Mode" would make the device more intuitive for users[cite: 148, 149]. [cite_start]Additionally, transitioning from simple threshold-based logic to a **PID (Proportional-Integral-Derivative)** control algorithm would allow for more precise temperature maintenance with less system fluctuation[cite: 173].

#### 4. What tools and/or resources are you adding to your support network?
* **Python Libraries:** `gpiozero` for simplified hardware interaction and `python-statemachine` for managing complex logical flows.
* **Hardware Debugging Tools:** Utilizing USB-to-TTL cables for UART serial monitoring and I2C scanning tools.
* [cite_start]**Technical Documentation:** Relying on official Adafruit CircuitPython and Raspberry Pi GPIO pinout resources[cite: 121, 131].

#### 5. What skills from this project will be particularly transferable?
[cite_start]The ability to design and implement a **Finite State Machine (FSM)** is highly transferable across software engineering and cybersecurity disciplines[cite: 251]. [cite_start]Furthermore, handling **asynchronous communication** (UART/I2C) and understanding voltage logic levels (protecting 3.3V Pi pins from 5V components) are fundamental skills for any embedded systems development[cite: 113, 114, 257].

#### 6. How did you make this project maintainable, readable, and adaptable?
* **Maintainability:** I utilized **Object-Oriented Programming (OOP)** by creating classes like `TemperatureMachine` and `ManagedDisplay`, isolating hardware logic from application state.
* **Readability:** I maintained consistent naming conventions and included detailed comments for GPIO pin mappings and operational blocks.
* **Adaptability:** I included a `DEBUG` flag for easy console monitoring and used a comma-delimited output format for the UART serial connection, making the data easily parsable by any external server software.

---

### Artifacts Included
* **`Thermostat.py`**: The main application containing the state machine, hardware drivers, and multi-threaded display management.
* **`ThermostatServer-Simulator.py`**: A Python script designed to simulate a remote server receiving serial telemetry from the thermostat.

---

### Hardware Requirements
* [cite_start]**Raspberry Pi 4** (or compatible)[cite: 183].
* [cite_start]**16x2 LCD Display** (HD44780 compatible)[cite: 7].
* [cite_start]**AHT20** Temperature and Humidity Sensor[cite: 242].
* [cite_start]**3x Momentary Push Buttons**[cite: 184].
* [cite_start]**2x LEDs** (Red and Blue)[cite: 243].
* [cite_start]**10k Ohm resistors** and **Potentiometer**[cite: 80, 184].

### How to Run
1.  Connect hardware components as specified in the **Module Seven/Eight Lab Guides**.
2.  Install the required Python libraries:
    `pip3 install gpiozero python-statemachine adafruit-circuitpython-charlcd adafruit-circuitpython-ahtx0`.
3.  Start the Server Simulator on your PC:
    `python3 ThermostatServer-Simulator.py`.
4.  Run the main application on the Raspberry Pi:
    `sudo python3 Thermostat.py`[cite: 236].
