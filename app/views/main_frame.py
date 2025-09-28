import tkinter as tk
from tkinter import ttk

class MainFrame(tk.Frame):
    def __init__(self):
        super().__init__()

        self.photo_label = tk.Label(self)
        self.photo_label.grid(row=0, column=0)

        self.photo_combobox = ttk.Combobox(self)
        self.photo_combobox['values'] = ('1.jpg', '2.jpg', '3.jpg')
        self.photo_combobox.grid(row=0, column=1)
        self.photo_combobox.bind(
            "<<ComboboxSelected>>",
            lambda _: self.photo_label.config(image=self.photo_combobox.get())
        )