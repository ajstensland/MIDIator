from src.midi.midi_io import find_device
from src.midi.midi_enums import Notes
from src.windows.windows_enums import KeyFlags, DICodes, MouseFlags, MouseDirections
from src.windows.windows_io import send_key_event, send_mouse_movement_event, send_mouse_button_event
import threading
import time
from math import sin


class MIDIator:
    def __init__(self, midi_identifier, key_binds, mouse_movement_binds, mouse_button_binds,
                 midi_channel=0, mouse_sensitivity=4, mouse_refresh=0.005, verbose=True):
        """
        Constructor for MIDIator.
        :param midi_identifier: A string unique to the desired MIDI device.
        :param key_binds: A dictionary of the form {Notes.<note>: DICodes.<code>}.
        :param mouse_movement_binds: A dictionary of the form {Notes.<note>: MouseDirections.<direction>}.
        :param mouse_button_binds: A dictionary of the form
               {Notes.<note>: (MouseFlags.<press-flag>, MouseFlags.<release-flag>)}.
        :param midi_channel: The channel on which to listen for events (default: 0).
        :param mouse_sensitivity: The amount by which to move the mouse every time mouse_refresh elapses (default: 4).
        :param mouse_refresh: The time to wait between every mouse position update (default: 5ms) .
        :param verbose: Whether or not to print log messages (default: True).
        """
        self.verbose = verbose
        self.log("{+} Initializing MIDIator...")

        self.key_binds = key_binds
        self.mouse_movement_binds = mouse_movement_binds
        self.mouse_button_binds = mouse_button_binds

        self.log(f"    > Connecting to MIDI controller by identifier \"{midi_identifier}\"... ", end="")
        self.midi_port = find_device(midi_identifier)
        self.midi_channel = midi_channel
        self.log("Done.")

        self.mouse_sensitivity = mouse_sensitivity
        self.mouse_refresh = mouse_refresh
        self.mouse_vector = [0, 0]
        self.log("    > Initialization complete. ")

    def log(self, *args, **kwargs):
        """
        Prints a message to the screen if the verbose flag is set.
        :param args: The args to pass down to print().
        :param kwargs: The keyword arguments to pass down to print().
        """
        if self.verbose:
            print(*args, **kwargs)

    def start(self):
        """
        Starts handling MIDI messages and translating them into Windows input.
        """
        self.log("{+} Spawning mouse handler thread... ", end="")
        mouse_thread = threading.Thread(target=self.mouse_handler)
        mouse_thread.start()
        self.log("Done.")

        self.log("{+} Handling MIDI events...")
        for message in self.midi_port:
            self.triage_message(message)

    def mouse_handler(self):
        """
        A function that automates moving the mouse, since each mouse movement is atomic.
        """
        sin_45 = sin(45)
        while True:
            x, y = self.mouse_vector

            if abs(x) == abs(y) and x != 0:
                x = x * sin_45
                y = y * sin_45

            x, y = int(x), int(y)
            send_mouse_movement_event(x, y)
            time.sleep(self.mouse_refresh)

    def triage_message(self, message):
        """
        Sends messages to their relevant handlers, or does nothing if irrelevant.
        :param message: A MIDI message.
        """
        if message.channel == self.midi_channel and "note_" in message.type:
            if message.type == "note_on":
                self.log(f"    > Received MIDI code {message.note} ({Notes(message.note).name:3}) -> ", end="")

            if message.note in self.key_binds:
                self.translate_keystroke(message)
            elif message.note in self.mouse_movement_binds:
                self.translate_mouse_move(message)
            elif message.note in self.mouse_button_binds:
                self.translate_mouse_button(message)
            elif message.type == "note_on":
                self.log("Key not bound.")

    def translate_keystroke(self, message):
        """
        Triggers a keyboard event based on the contents of a MIDI message.
        :param message: A "note_on" or "note_off" MIDI message.
        """
        if message.type == "note_on":
            self.log(f"Key {self.key_binds[message.note].name}")

        direct_input_key = self.key_binds[message.note]
        flag = KeyFlags.PRESS if message.type == "note_on" else KeyFlags.RELEASE
        send_key_event(direct_input_key, flag)

    def translate_mouse_move(self, message):
        """
        Modifies the mouse movement vector based on the contents of a MIDI message.
        :param message: A "note_on" or "note_off" MIDI message.
        """
        if message.type == "note_on":
            self.log(f"Mouse {self.mouse_movement_binds[message.note].name}")

        x, y = self.mouse_movement_binds[message.note]
        polarity = 1 if message.type == "note_on" else -1
        self.mouse_vector[0] += polarity * x * self.mouse_sensitivity
        self.mouse_vector[1] += polarity * y * self.mouse_sensitivity

    def translate_mouse_button(self, message):
        """
        Triggers a mouse button event based on the contents of a MIDI message.
        :param message: A "note_on" or "note_off" MIDI message.
        """
        if message.type == "note_on":
            self.log(f"Mouse {self.mouse_button_binds[message.note][0].name}")

        click_flag, release_flag = self.mouse_button_binds[message.note]
        flag = click_flag if message.type == "note_on" else release_flag
        send_mouse_button_event(flag)


if __name__ == "__main__":
    #####################################################
    #  U S E R   C O N F I G U R A T I O N   B E L O W  #
    #####################################################

    # A string unique to the MIDI controller to connect to
    identifier = "Casio"

    # Map from MIDI key codes to DirectInput key codes
    # Note: "S" in a note name signifies "#" or "sharp"
    default_key_binds = {
        Notes.FS3: DICodes.W,
        Notes.E3: DICodes.A,
        Notes.F3: DICodes.S,
        Notes.G3: DICodes.D,
        Notes.D3: DICodes.LSHIFT,
        Notes.A3: DICodes.SPACE,
        Notes.GS3: DICodes.R
        }

    # Map from MIDI key codes to mouse movement directions
    default_mouse_movement_binds = {
        Notes.E4: MouseDirections.LEFT,
        Notes.F4: MouseDirections.DOWN,
        Notes.FS4: MouseDirections.UP,
        Notes.G4: MouseDirections.RIGHT,
        }

    # Map from MIDI key codes to mouse button flags
    # The first flag is the pressed flag, the second is the released flag
    default_mouse_button_binds = {
        Notes.D4: (MouseFlags.LEFT_CLICK, MouseFlags.LEFT_RELEASE),
        Notes.A4: (MouseFlags.RIGHT_CLICK, MouseFlags.RIGHT_RELEASE)
        }

    #####################################################
    #    E N D   U S E R   C O N F I G U R A T I O N    #
    #####################################################

    # Initializing and starting MIDIator
    midiator = MIDIator(identifier, default_key_binds, default_mouse_movement_binds, default_mouse_button_binds)
    midiator.start()
