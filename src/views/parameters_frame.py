from tkinter import ttk
import tkinter as tk

class ParametersFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.current_parameters = None

    def _clear_widgets(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def create_parameters_widgets(self, parameters) -> None:
        self._clear_widgets()
        for key, value in parameters.items():
            tk.Label(self, text=key).grid()
            match value['widget']:
                case 'entry':
                    entry = tk.Entry(self)
                    entry.grid()
                    entry.insert(0, value['default'])
                case 'spinbox':
                    spinbox = tk.Spinbox(self)
                    spinbox.grid()
                    spinbox.insert(0, value['default'])
                case 'checkbox':
                    radio_button = tk.Checkbutton(self, state="active")
                    radio_button.grid()
                case 'combobox':
                    combobox = ttk.Combobox(self)
                    combobox.grid()
                    combobox['values'] = value['choices']

        # Tutaj musisz dodać słownik na wszystkie widgety i pobierać z nich dane za każdym
        # razem kiedy włączasz detekcje Ekstraktorem
        # Ewentualnie dla lepszej optymalizacji zrobić flagę która sprawdza, czy coś się zmieniło
        # i dopiero wtedy wywolywac funkcje ale watpie ze ta jedna milisekunda straty ma sens

    def get_parameters(self) -> dict:
        return {}