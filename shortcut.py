from enum import Enum
import pyautogui

class Shortcut(Enum):
    COPY = ('command', 'c')
    PASTE = ('command', 'v')
    CUT = ('command', 'x')
    UNDO = ('command', 'z')
    REDO = ('command', 'y')

def perform_operation(shortcut):
    pyautogui.hotkey(*shortcut.value)

# usage
perform_operation(Shortcut.COPY)
