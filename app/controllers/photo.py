import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PhotoController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.photo_combobox.bind("<<ComboboxSelected>>", self.on_change)
        self._bind()

    def _bind(self):
        self.frame.photo_combobox['values'] = self.model.photo.get_screenshot_names()
        self.frame.photo_image.configure(file=self.model.photo.get_screenshot_by_name(self.frame.photo_combobox.get()))

    def on_change(self, event):
        logger.info(f"ComboBox change")
        screenshot = self.model.photo.get_screenshot_by_name(self.get_chosen_photo())
        print(screenshot)
        self.frame.photo_label.configure(image=screenshot)

    def get_chosen_photo(self):
        result_photo = self.frame.photo_combobox.get()
        print(result_photo)
        return result_photo