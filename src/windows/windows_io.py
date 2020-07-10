"""
The majority of the below code is adapted from Nicholas Brochu's work on Serpent.AI, specifically from the below file:

    https://github.com/SerpentAI/SerpentAI/blob/dev/serpent/input_controllers/native_win32_input_controller.py

Since Serpent.AI is made available under the MIT License, here's the copy of the original, as required:

    MIT License

    Copyright (c) 2017-2020 Serpent.AI

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""

import ctypes
from src.windows.windows_enums import MouseFlags


class KeyBdInput(ctypes.Structure):
    """
    Class to represent a Windows KEYBDINPUT struct. Originally written by Nicholas Brochu.

    Microsoft Documentation: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput
    """
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class HardwareInput(ctypes.Structure):
    """
    Class to represent a Windows HARDWAREINPUT struct. Originally written by Nicholas Brochu.

    Microsoft Documentation: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-hardwareinput
    """
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    """
    Class to represent a Windows MOUSEINPUT struct. Originally written by Nicholas Brochu.

    Microsoft Documentation: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
    """
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class InputI(ctypes.Union):
    """
    Helper class for building a Windows INPUT struct. Originally written by Nicholas Brochu.
    """
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    """
    Class to represent a Windows INPUT struct. Originally written by Nicholas Brochu.

    Microsoft Documentation https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
    """
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", InputI)]


def send_key_event(key, flag):
    """
    Sends a keystroke to the focused window.
    :param key: A DirectInput key code, as found in the DICodes enum.
    :param flag: A number representing if the key is being pressed or released, as found in the KeyFlags enum.
    """
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(0, key, flag, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def send_mouse_movement_event(x, y):
    """
    Sends an atomic mouse movement event to the focused window.
    :param x: The offset by which to move on the x-axis (negative is left, positive is right).
    :param y: The offset by which to move on the y-axis (negative is up, positive is down).
    """
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.mi = MouseInput(x, y, 0, MouseFlags.MOVE, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def send_mouse_button_event(flag):
    """
    Sends a mouse button event (e.g. clicking or releasing) to the focused window.
    :param flag: A number that corresponds to a mouse button event, as found in the MouseFlags enum.
    """
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.mi = MouseInput(0, 0, 0, flag, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
