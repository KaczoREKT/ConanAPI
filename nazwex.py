from pathlib import Path

folder = Path(r"test/Screenshots/Final_Fantasy_VII")  # <- zmień
prefix = "image_"

files = sorted([p for p in folder.iterdir() if p.is_file()])

for i, p in enumerate(files, start=1):
    new_name = f"{prefix}{i}{p.suffix}"
    p.rename(p.with_name(new_name))