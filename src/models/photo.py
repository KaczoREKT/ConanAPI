import os

from .preprocessing import load_image, convert_image_to_tkinter


class Photo:
    def __init__(self):
        base_dir = os.getcwd()
        self.folder = os.path.join(base_dir, "test/Screenshots/Conan_Exiles")
        self.screenshots = self.load_screenshots()
        self.current_cv2_image = load_image(list(self.screenshots.values())[0])
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
