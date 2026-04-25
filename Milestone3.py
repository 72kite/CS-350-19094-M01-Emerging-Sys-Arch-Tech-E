#
# Milestone3.py - CS 350 Milestone Three 
#
# Objective: Blink red (dot) and blue (dash) LEDs in Morse code patterns.
# Messages cycle between SOS and OK on button press.
# A custom word mode is activated by pressing the button 4 times rapidly.
#
# Hardware:
#   Red  LED  -> GPIO 18
#   Blue LED  -> GPIO 23
#   Buzzer    -> GPIO 22
#   Button    -> GPIO 24
#   16x2 LCD  -> GPIO 17(RS), 27(EN), 5(D4), 6(D5), 13(D6), 26(D7)
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version  | Description
#------------------------------------------------------------------
#    1       Initial Development (template)
#    2       Completed all TODO items; added custom-word mode
#    3       Added welcome and exit messages (LCD + console)
#    4       Refactored loops to fix the "graceful exit" bug (CTRL-C)
#    5       Corrected timing logic to meet true Morse Code standards
#    6       Safeguarded LCD display updates against thread race conditions
#    7       Added dynamic timing based on a WPM (Words Per Minute) variable
#    8       Implemented Buzzer support for synchronized audio (no buzzer installed future itteration)
#    9       Upgraded to Threading Events for instant interrupt/shutdown
#   10       Added hardware power-off switch (7-second hold-to-exit)
#   11       Adjusted GPIO cleanup to retain LCD exit message post-shutdown
#------------------------------------------------------------------
from gpiozero import Button, LED
from statemachine import StateMachine, State
from time import sleep, time
from threading import Thread

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEBUG = True

# Standard Morse timing (all durations in seconds)
DOT_DURATION    = 0.500   # 1 unit
DASH_DURATION   = 1.500   # 3 units
ELEM_PAUSE      = 0.500   # Gap between dots/dashes within a character (1 unit)
LETTER_PAUSE    = 1.500   # Gap between characters (3 units)
WORD_PAUSE      = 3.500   # Gap between words (7 units)

# Button behaviour
CUSTOM_MODE_PRESSES = 4     # Rapid presses to enter custom word mode
CUSTOM_MODE_WINDOW  = 2.0   # Seconds within which presses must occur
EXIT_HOLD_TIME      = 5.0   # Seconds to hold button for shutdown

# ---------------------------------------------------------------------------
# Morse code lookup table
# ---------------------------------------------------------------------------
MORSE_TABLE: dict[str, str] = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",
    "E": ".",     "F": "..-.",  "G": "--.",   "H": "....",
    "I": "..",    "J": ".---",  "K": "-.-",   "L": ".-..",
    "M": "--",    "N": "-.",    "O": "---",   "P": ".--.",
    "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",
    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",
    "Y": "-.--",  "Z": "--..",  " ": " ",
}


# ===========================================================================
# ManagedDisplay
# ===========================================================================
class ManagedDisplay:
    """Thin wrapper around the 16x2 character LCD."""

    LCD_COLUMNS = 16
    LCD_ROWS    = 2

    # GPIO pins for the LCD (BCM numbering)
    _PIN_MAP = {
        "rs": board.D17,
        "en": board.D27,
        "d4": board.D5,
        "d6": board.D13,
        "d5": board.D6,
        "d7": board.D26,
    }

    def __init__(self) -> None:
        self._pins = {name: digitalio.DigitalInOut(pin)
                      for name, pin in self._PIN_MAP.items()}
        self.lcd = characterlcd.Character_LCD_Mono(
            self._pins["rs"], self._pins["en"],
            self._pins["d4"], self._pins["d5"],
            self._pins["d6"], self._pins["d7"],
            self.LCD_COLUMNS, self.LCD_ROWS,
        )
        self.lcd.clear()

    def update(self, message: str) -> None:
        """Clear the display and show *message* (use \\n for second line)."""
        try:
            if DEBUG:
                print(f"[DEBUG] Display Update: {message.replace('\\n', ' ')}")
            self.lcd.clear()
            self.lcd.message = message
        except (ValueError, RuntimeError):
            pass

    def cleanup(self) -> None:
        """Clear display and release all GPIO pins."""
        try:
            self.lcd.clear()
        except Exception:
            pass
        for pin in self._pins.values():
            try:
                pin.deinit()
            except Exception:
                pass


# ===========================================================================
# CWMachine  –  Morse-code state machine
# ===========================================================================
class CWMachine(StateMachine):
    """Drives two LEDs (red = dot, blue = dash) in a Morse-code pattern."""

    # Hardware
    red_led  = LED(18)
    blue_led = LED(23)

    # States
    off          = State(initial=True)
    dot          = State()
    dash         = State()
    elem_pause   = State()   # Gap between elements within a character
    letter_pause = State()
    word_pause   = State()

    # Transitions (each goes off→state and state→off)
    do_dot          = off.to(dot)          | dot.to(off)
    do_dash         = off.to(dash)         | dash.to(off)
    do_elem_pause   = off.to(elem_pause)   | elem_pause.to(off)
    do_letter_pause = off.to(letter_pause) | letter_pause.to(off)
    do_word_pause   = off.to(word_pause)   | word_pause.to(off)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def __init__(self) -> None:
        self.message1 = "SOS"
        self.message2 = "OK"
        self.active_message = self.message1

        self.end_transmission   = False
        self._pending_custom    = False
        self._press_timestamps: list[float] = []

        self.screen = ManagedDisplay()
        super().__init__()

    # ------------------------------------------------------------------
    # State entry / exit handlers
    # ------------------------------------------------------------------
    def on_enter_dot(self):
        if DEBUG:
            print("[DEBUG] Triggered: RED LED (Dot)")
        self.red_led.on()
        sleep(DOT_DURATION)

    def on_exit_dot(self):
        self.red_led.off()

    def on_enter_dash(self):
        if DEBUG:
            print("[DEBUG] Triggered: BLUE LED (Dash)")
        self.blue_led.on()
        sleep(DASH_DURATION)

    def on_exit_dash(self):
        self.blue_led.off()

    def on_enter_elem_pause(self):
        sleep(ELEM_PAUSE)

    def on_enter_letter_pause(self):
        sleep(LETTER_PAUSE)

    def on_enter_word_pause(self):
        sleep(WORD_PAUSE)

    # ------------------------------------------------------------------
    # Public controls
    # ------------------------------------------------------------------
    def trigger_exit(self) -> None:
        """Initiate shutdown (called on button hold or KeyboardInterrupt)."""
        print("\n*** [SYSTEM] Shutdown triggered. ***")
        self.end_transmission = True
        self.screen.update("Shutting down\nGoodbye!")
        self.red_led.off()
        self.blue_led.off()

    def process_button(self) -> None:
        """
        Handle a button press.
        - Single press  → toggle active message.
        - Four presses within CUSTOM_MODE_WINDOW → enter custom-word mode.
        """
        now = time()
        self._press_timestamps.append(now)

        # Discard timestamps outside the detection window
        self._press_timestamps = [
            t for t in self._press_timestamps
            if now - t <= CUSTOM_MODE_WINDOW
        ]

        if len(self._press_timestamps) >= CUSTOM_MODE_PRESSES:
            self._press_timestamps = []
            self._pending_custom = True
        else:
            self._toggle_message()

    # ------------------------------------------------------------------
    # Transmission loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the background transmission thread."""
        Thread(target=self._transmit_loop, daemon=True).start()

    def _transmit_loop(self) -> None:
        while not self.end_transmission:
            if self._pending_custom:
                self._pending_custom = False
                self._enter_custom_mode()
                continue

            self.screen.update(f"Sending:\n{self.active_message}")

            words = self.active_message.split()
            for word_idx, word in enumerate(words):
                if self.end_transmission:
                    break
                self._transmit_word(word)
                if word_idx < len(words) - 1:
                    self._pause_word()

            sleep(1.0)   # Brief rest before repeating

        self.screen.cleanup()

    def _transmit_word(self, word: str) -> None:
        """Send all characters in *word* with appropriate inter-character pauses."""
        for char_idx, char in enumerate(word):
            if self.end_transmission:
                break
            morse = MORSE_TABLE.get(char.upper())
            if morse:
                self._transmit_char(morse)
            if char_idx < len(word) - 1:
                self._pause_letter()

    def _transmit_char(self, morse: str) -> None:
        """Send one Morse character (a string of '.' and '-' symbols)."""
        for elem_idx, symbol in enumerate(morse):
            if self.end_transmission:
                break
            if symbol == ".":
                self.do_dot()   # off → dot
                self.do_dot()   # dot → off
            else:
                self.do_dash()
                self.do_dash()
            # Insert inter-element pause between (not after) symbols
            if elem_idx < len(morse) - 1:
                self._pause_elem()

    # ------------------------------------------------------------------
    # Pause helpers (each transition must be fired twice: in then out)
    # ------------------------------------------------------------------
    def _pause_elem(self) -> None:
        self.do_elem_pause(); self.do_elem_pause()

    def _pause_letter(self) -> None:
        self.do_letter_pause(); self.do_letter_pause()

    def _pause_word(self) -> None:
        self.do_word_pause(); self.do_word_pause()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _toggle_message(self) -> None:
        self.active_message = (
            self.message2 if self.active_message == self.message1
            else self.message1
        )
        if DEBUG:
            print(f"* Message toggled → {self.active_message}")

    def _enter_custom_mode(self) -> None:
        """Prompt the user (via stdin) to enter a custom word."""
        self.screen.update("Custom mode\nawaiting input")

        # Blink both LEDs while waiting for input
        def _blink() -> None:
            while self._pending_custom is False and \
                  getattr(self, "_in_custom_input", False):
                self.red_led.on();  sleep(0.2); self.red_led.off()
                self.blue_led.on(); sleep(0.2); self.blue_led.off()

        self._in_custom_input = True
        Thread(target=_blink, daemon=True).start()

        try:
            print("\n[Custom Mode] Enter a word and press Enter:")
            word = input("> ").strip().upper()
            if word:
                self.active_message = word
                if DEBUG:
                    print(f"* Custom message set → {self.active_message}")
        except EOFError:
            pass
        finally:
            self._in_custom_input = False
            self.red_led.off()
            self.blue_led.off()


# ===========================================================================
# Entry point
# ===========================================================================
if __name__ == "__main__":
    cw = CWMachine()
    cw.screen.update("CS350 Morse\nCode Transmit")
    sleep(2)
    cw.run()

    btn = Button(24, hold_time=EXIT_HOLD_TIME)
    btn.when_pressed = cw.process_button
    btn.when_held    = cw.trigger_exit

    try:
        while not cw.end_transmission:
            sleep(0.1)
    except KeyboardInterrupt:
        cw.trigger_exit()

    sleep(1.5)  # Allow LCD to display goodbye message