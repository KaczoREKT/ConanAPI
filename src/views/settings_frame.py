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

        self.preprocessing_combobox_label = tk.Label(self, text="Choose preprocessing:")
        self.preprocessing_combobox_label.grid(row=2, column=0, sticky="nw")

        self.preprocessing_combobox = ttk.Combobox(self)
        self.preprocessing_combobox.grid(row=3, column=0, sticky="nw")

        self.extractor_combobox_label = tk.Label(self, text="Choose extractor:")
        self.extractor_combobox_label.grid(row=4, column=0, sticky="nw")

        self.extractor_combobox = ttk.Combobox(self)
        self.extractor_combobox.grid(row=5, column=0, sticky="nw")

        self.detector_combobox_label = tk.Label(self, text="Choose detector:")
        self.detector_combobox_label.grid(row=6, column=0, sticky="nw")

        self.detector_combobox = ttk.Combobox(self)
        self.detector_combobox.grid(row=7, column=0, sticky="nw")

        self.extractor_button = tk.Button(self, text="Extract Keypoints")
        self.extractor_button.grid(row=8, column=0, sticky="nw")

        self.ocr_button = tk.Button(self, text="Perform OCR")
        self.ocr_button.grid(row=9, column=0, sticky="nw")

        self.loop_button = tk.Button(self, text="Start Capture Loop")
        self.loop_button.grid(row=10, column=0, sticky="nw")
