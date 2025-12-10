from datetime import time
import os
import time
from pathlib import Path
from typing import Union

def save_to_txt(file_name: str, *output_texts: Union[str, list], timestamp: bool = False) -> None:
    """
    Dopisuje jeden lub więcej tekstów do pliku (nie nadpisuje istniejących danych).

    Parameters
    ----------
    file_name : str
        Nazwa pliku docelowego.
    *output_texts : str | list
        Dowolna liczba argumentów do zapisania.
        • Pojedynczy string zostanie dodany jako osobna linia.
        • Lista ― każdy jej element (po konwersji na str) trafi do osobnej linijki.
    timestamp : bool, default=False
        Gdy True, dodaje znacznik czasu jako pierwszą linię w tym zapisie.
    """
    # 1️⃣ Zebranie wszystkich linijek
    lines: list[str] = []
    if timestamp:
        lines.append(f"[LOG : {time.strftime('%Y-%m-%d %H:%M:%S')}]")

    for item in output_texts:
        if isinstance(item, list):
            lines.extend(str(x) for x in item)
        else:
            lines.append(str(item))

    # 2️⃣ Zapewnienie istnienia katalogu
    os.makedirs(os.path.dirname(os.path.abspath(file_name)), exist_ok=True)

    # 3️⃣ Dopisywanie do pliku
    try:
        with open(file_name, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as exc:
        print(f"Error saving to {file_name}: {exc}")

# Read file from path
def read_file(file_path):
    base = os.getcwd()
    path = os.path.join(base, file_path)
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def text_prettifier(text):
    return f'====================//////////{text}//////////===================='

def str_to_tuple(s):
    s = str(s).strip("()[] ")
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]

    def to_number(x):
        try:
            return int(x)
        except ValueError:
            return float(x)

    return tuple(to_number(p) for p in parts)