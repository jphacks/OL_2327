import tkinter as tk
from tkinter import Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class FingerDrawingApp:
    def __init__(self, root):
        self.root = root
        root.title("FingerDrawing")
        root.geometry("800x1000")

        self.title = tk.Label(root, text="FingerDrawing", font=("Helvetica", 36))
        self.title.pack(pady=10)

        self.title = tk.Label(root, text="2023/10/28-29, JPHACK2023, All Reserve in CambriaExplosion", font=("Helvetica", 14))
        self.title.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.axis('off')  # 軸を非表示にする
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.quit_button = Button(self.button_frame, text="Quit", command=self.quit, width=10, height=2)
        self.quit_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.delete_button = Button(self.button_frame, text="Delete", command=self.delete, width=10, height=2)
        self.delete_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.save_button = Button(self.button_frame, text="Save", command=self.save, width=10, height=2)
        self.save_button.pack(side=tk.LEFT, padx=10, expand=True)

    def quit(self):
        self.root.destroy()

    def delete(self):
        self.ax.clear()
        self.ax.axis('off')  # 軸を再度非表示にする
        self.canvas.draw()

    def save(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drawfinger_{timestamp}.png"
        self.fig.savefig(filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = FingerDrawingApp(root)
    root.mainloop()
