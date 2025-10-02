import os


class Photo:
    def __init__(self):
        base_dir = os.getcwd()
        print(base_dir)
        self.folder = os.path.join(base_dir, "Screenshots")
        self.screenshots = self.load_screenshots()


    def load_screenshots(self):
        files = os.listdir(self.folder)
        screenshots = {
            f: os.path.join(self.folder, f)
            for f in files
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        }
        return screenshots

    def get_screenshot_names(self):
        return list(self.screenshots.keys())

    def get_screenshot_by_name(self, name):
        return self.screenshots.get(name)
