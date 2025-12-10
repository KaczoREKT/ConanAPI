import tkinter as tk
from tkinter import ttk

from app.views.parameters_frame import ParametersFrame
from app.views.photo_frame import PhotoFrame
from app.views.settings_frame import SettingsFrame
from app.views.ocr_frame import OCRFrame

class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.photo_frame = PhotoFrame()
        self.photo_frame.grid(row=0, column=0)

        self.settings_frame = SettingsFrame()
        self.settings_frame.grid(row=0, column=1, sticky='nsew')

        self.ocr_frame = OCRFrame()
        self.ocr_frame.grid(row=1, column=0, sticky='nsew')

        self.parameters_frame = ParametersFrame()
        self.parameters_frame.grid(row=0, column=2, sticky='nsew')





