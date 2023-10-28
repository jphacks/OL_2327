from enum import Enum
import pyautogui


class Shortcut(Enum):
    COPY = ('command', 'c')
    PASTE = ('command', 'v')
    CUT = ('command', 'x')
    UNDO = ('command', 'z')
    REDO = ('command', 'y')
    SCREENSHOT = ('command', 'shift', '3')

def perform_operation(shortcut):
    print(f"ショートカット: {shortcut.value}")
    pyautogui.hotkey(*shortcut.value)

def perform_gesture_action(gesture_label):
    if gesture_label == "copy":
        perform_operation(Shortcut.COPY)
    elif gesture_label == "paste":
        perform_operation(Shortcut.PASTE)
    elif gesture_label == "cut":
        perform_operation(Shortcut.CUT)
    elif gesture_label == "undo":
        perform_operation(Shortcut.UNDO)
    elif gesture_label == "redo":
        perform_operation(Shortcut.REDO)
    elif gesture_label == "screenshot":
        perform_operation(Shortcut.SCREENSHOT)


def main():
    # app.py を実行
    # try:
    #     subprocess.run(["python", "app.py"], check=True)
    # except subprocess.CalledProcessError as e:
    #     print(f"app.py 実行中にエラーが発生しました: {e}")
    # except FileNotFoundError:
    #     print("Python インタープリタが見つかりません。")
    perform_gesture_action("screenshot") 

if __name__ == "__main__":
    main()