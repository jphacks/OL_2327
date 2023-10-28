import keyboard
import time


def perform_operation(shortcut):
    keyboard.press_and_release(shortcut)
    time.sleep(0.5)


def perform_gesture_action(gesture_label):
    if gesture_label == "copy":
        perform_operation('command+c')
    elif gesture_label == "paste":
        perform_operation('command+v')
    elif gesture_label == "cut":
        perform_operation('command+x')
    elif gesture_label == "undo":
        perform_operation('command+z')
    elif gesture_label == "redo":
        perform_operation('command+y')
    elif gesture_label == "screenshot":
        perform_operation('command+shift+3')
    elif gesture_label == "bookmark":
        perform_operation('command+d')


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
