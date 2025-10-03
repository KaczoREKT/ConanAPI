import logging

from PIL import Image, ImageTk

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PhotoController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.photo_combobox.bind("<<ComboboxSelected>>", self.on_change)
        self._bind()

    def _bind(self) -> None:
        self.frame.settings_frame.photo_combobox['values'] = self.model.photo.get_screenshot_names()
        self.update_image(list(self.model.photo.screenshots.values())[0])

    def on_change(self, event) -> None:
        logger.info(f"ComboBox change")
        screenshot_path = self.model.photo.get_screenshot_by_name(self.get_chosen_photo())
        self.update_image(screenshot_path)

    def get_chosen_photo(self) -> str:
        result_photo = self.frame.settings_frame.photo_combobox.get()
        return result_photo

    def update_image(self, screenshot_path: str) -> None:
        img = Image.open(screenshot_path)
        img = img.resize((1024, 600))
        img = ImageTk.PhotoImage(img)
        self.model.photo.current_tk_image = img
        self.update_photo_label(self.model.photo.current_tk_image)

    def update_photo_label(self, image) -> None:
        self.frame.photo_frame.photo_label.configure(image=image)