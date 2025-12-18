import tkinter as tk
from src.other.config import config

class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        # self.geometry(f"{config['window_width']}x{config['window_height']}")
        self.title("Feature Extractor")
        self.resizable(False, False)
