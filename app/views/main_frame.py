import tkinter as tk
from tkinter import ttk

from app.views.photo_frame import PhotoFrame
from app.views.settings_frame import SettingsFrame


class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.photo_frame = PhotoFrame()
        self.photo_frame.grid(row=0, column=0)

        self.settings_frame = SettingsFrame()
        self.settings_frame.grid(row=0, column=1, sticky='nsew')





