import mido
from rtmidi import SystemError


def find_device(identifier):
    """
    Searches for and returns a MIDI device based on the identifier.
    :param identifier: A string (not case-sensitive) that makes up part of the MIDI device input name.
    :return: A MIDI input port as defined by mido.
    """
    try:
        for name in mido.get_input_names():
            if identifier.lower() in name.lower():
                return mido.open_input(name)
    except SystemError:
        print(f"\nError: \"{identifier}\" does not identify an active or valid MIDI device.")
        exit(1)
    except OSError:
        print(f"\nError: Device identified by \"{identifier}\" appears to be in use by another process.")
        exit(1)
    else:
        print(f"\nError: \"{identifier}\" does not identify an active or valid MIDI device.")
        exit(1)
