import tkinter as tk

class PhotoFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.config(highlightbackground="black", highlightthickness=2)

        self.photo_label = tk.Label(self)
        self.photo_label.grid(row=0, column=0)



