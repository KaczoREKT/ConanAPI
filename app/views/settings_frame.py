import tkinter as tk
from tkinter import ttk

class SettingsFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.config(highlightbackground="black", highlightthickness=2)
        self.photo_combobox_label = tk.Label(self, text="Choose screenshot:")
        self.photo_combobox_label.grid(row=0, column=0, sticky="nw")

        self.photo_combobox = ttk.Combobox(self)
        self.photo_combobox.grid(row=1, column=0, sticky="nw")

        self.extractor_combobox_label = tk.Label(self, text="Choose extractor:")
        self.extractor_combobox_label.grid(row=2, column=0, sticky="nw")

        self.extractor_combobox = ttk.Combobox(self)
        self.extractor_combobox.grid(row=3, column=0, sticky="nw")

        self.create_extractor_setting()

    def create_extractor_setting(self):
        label = tk.Label(self, text='Dupa')
        label.grid(row=4, column=0, sticky="nw")
        spinbox = ttk.Spinbox(self, from_=20, to=100)
        spinbox.grid(row=5, column=0, sticky="nw")