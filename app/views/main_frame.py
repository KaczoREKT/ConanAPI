import tkinter as tk
from tkinter import ttk

class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.photo_image = tk.PhotoImage()
        self.photo_label = tk.Label(self)
        self.photo_label.grid(row=0, column=0)

        self.photo_combobox = ttk.Combobox(self)
        self.photo_combobox.grid(row=0, column=1)