import tkinter as tk

class OCRFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.config(highlightbackground="black", highlightthickness=2)

        self.ocr_label = tk.Label(self, height=12, width=50, justify="left", anchor="nw")
        self.ocr_label.grid(row=0, column=0)



