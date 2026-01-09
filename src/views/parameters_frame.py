from tkinter import ttk
import tkinter as tk

class ParametersFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.vars = {}

    def _clear_widgets(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self.vars.clear()

    def create_parameters_widgets(self, parameters) -> None:
        self._clear_widgets()
        for key, value in parameters.items():
            widget_name = value['widget']
            default = value['default']
            match widget_name:
                case 'entry':
                    var = tk.StringVar(value=default)
                    widget = tk.Entry(self, textvariable=var)
                case 'spinbox':
                    var = tk.DoubleVar()
                    widget = tk.Spinbox(self,
                                        from_=value['from_'],
                                        to=value['to'],
                                        increment=value['step'],
                                        textvariable=var,
                                        font=("Segoe UI", 14))
                    var.set(default)
                case 'checkbox':
                    var = tk.BooleanVar(value=default)
                    widget = tk.Checkbutton(self, variable=var)
                case 'None':
                    continue
            tk.Label(self, text=key).grid()
            widget.grid()
            self.vars[key] = var


        # Tutaj musisz dodać słownik na wszystkie widgety i pobierać z nich dane za każdym
        # razem kiedy włączasz detekcje Ekstraktorem
        # Ewentualnie dla lepszej optymalizacji zrobić flagę która sprawdza, czy coś się zmieniło
        # i dopiero wtedy wywolywac funkcje ale watpie ze ta jedna milisekunda straty ma sens

    def get_parameters(self) -> dict:
        return {}