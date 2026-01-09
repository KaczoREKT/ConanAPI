import tkinter as tk

class OCRFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.config(highlightbackground="black", highlightthickness=2)

        self.ocr_label = tk.Label(self, height=12, justify="left", anchor="nw", wraplength=300)
        self.ocr_label.grid(row=0, column=0)

        self.result_label = tk.Label(self, text="Result:", pady=10)
        self.result_label.grid(row=2, column=0)


