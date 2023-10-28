#!/usr/bin/env python3

import tkinter as tk
from tkinter import Toplevel, ttk
from PIL import Image, ImageTk
import pandas as pd
import subprocess
import threading

# グローバル変数でウィンドウとボタンのサイズを制御
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
BUTTON_WIDTH = 30
BUTTON_HEIGHT = 3
HISTORY_WINDOW_WIDTH = 800
HISTORY_WINDOW_HEIGHT = 500
CSV_FILE_PATH = "./data/history.csv"  # CSVファイルのパス
IMAGE_PATH = "./data/instruction.png"  # 画像ファイルのパス

def run_main():
    threading.Thread(target=lambda: subprocess.run(["python", "main.py"])).start()

def open_history_window():
    history_window = Toplevel(root)
    history_window.title("Shortcut History")
    history_window.grab_set()  # Make history window modal
    history_window.geometry(f"{HISTORY_WINDOW_WIDTH}x{HISTORY_WINDOW_HEIGHT}")

    tk.Label(history_window, text="Shortcut History", font=("Arial", 16)).pack(pady=10)

    # Create table for shortcut history
    table = ttk.Treeview(history_window, columns=("Time", "Action"), show="headings")
    table.heading("Time", text="Time")
    table.heading("Action", text="Action")
    table.pack(fill=tk.BOTH, expand=True)  # Fill the window

    # Load data from CSV file and populate the table
    data = pd.read_csv(CSV_FILE_PATH)
    for index, row in data.iterrows():
        table.insert("", "end", values=(row["Time"], row["Action"]))

    tk.Button(history_window, text="Close", command=history_window.destroy, width=BUTTON_WIDTH, height=BUTTON_HEIGHT).pack(pady=10)

def exit_app():
    root.quit()

def on_configure(event, canvas):
    # Update the scrollregion whenever the size of the inner frame changes.
    canvas.configure(scrollregion=canvas.bbox('all'))

def main():
    global root
    root = tk.Tk()
    root.title("Posture Shortcut")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    frame = tk.Frame(canvas)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0,0), window=frame, anchor="nw")

    frame.bind("<Configure>", lambda event: on_configure(event, canvas))  # Pass canvas as an argument
    # Change 'root' to 'frame' for all widgets
    tk.Label(frame, text="Posture Shortcut", font=("Arial", 36)).pack(pady=10)
    tk.Label(frame, text="Usage", font=("Arial", 24)).pack(pady=10)

    # Load and display the image
    image = Image.open(IMAGE_PATH)
    new_width = BUTTON_WIDTH * 10  # Assuming each character in the button is about 10 pixels wide
    new_height = int((new_width / image.width) * image.height)  # Keep the aspect ratio
    resized_image = image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(resized_image)
    img_label = tk.Label(frame, image=photo)  # Change 'root' to 'frame'
    img_label.photo = photo
    img_label.pack(pady=10)

    tk.Button(frame, text="Start", command=run_main, width=BUTTON_WIDTH, height=BUTTON_HEIGHT).pack(pady=5)
    tk.Button(frame, text="Shortcut History", command=open_history_window, width=BUTTON_WIDTH, height=BUTTON_HEIGHT).pack(pady=5)
    tk.Button(frame, text="Exit", command=exit_app, width=BUTTON_WIDTH, height=BUTTON_HEIGHT).pack(pady=5)

    # This line is important to link the scrollbar to the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    root.mainloop()

if __name__ == '__main__':
    main()
