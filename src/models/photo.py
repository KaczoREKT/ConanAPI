import os

from .preprocessing import load_image, convert_image_to_tkinter
from ..other.config import Config


class Photo:
    def __init__(self):
        base_dir = os.getcwd()
        self.folder = os.path.join(base_dir, "test/Screenshots/Resident_Evil_2")
        self.screenshots = self.load_screenshots()
        self.screenshots_transcriptions = Config(os.path.join(self.folder, "transcriptions.yaml"))
        self.current_cv2_image = load_image(list(self.screenshots.values())[0])
        self.current_preprocessed_image = None
        self.current_tk_image = convert_image_to_tkinter(self.current_cv2_image)

    def load_screenshots(self) -> dict[str, str]:
        files = os.listdir(self.folder)
        screenshots = {
            f: os.path.join(self.folder, f)
            for f in files
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        }
        return screenshots

    def get_screenshot_names(self) -> list[str]:
        return list(self.screenshots.keys())

    def get_screenshot_by_key(self, name) -> str | None:
        return self.screenshots.get(name)
