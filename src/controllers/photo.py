import logging
import threading
from src.models.preprocessing import load_image, convert_image_to_tkinter
import time

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
        self.frame.settings_frame.photo_combobox.current(0)
        self.update_image(list(self.model.photo.screenshots.values())[0])

    def on_change(self, event) -> None:
        logger.info(f"ComboBox change")
        screenshot_path = self.model.photo.get_screenshot_by_key(self.get_selected_from_combobox())
        self.update_image(screenshot_path)

    def get_selected_from_combobox(self) -> str:
        result_photo = self.frame.settings_frame.photo_combobox.get()
        return result_photo

    def update_image(self, screenshot_path: str) -> None:
        cv2_img = load_image(screenshot_path)
        imgtk = convert_image_to_tkinter(cv2_img)
        self.model.photo.current_cv2_image = cv2_img
        self.model.photo.current_preprocessed_image = cv2_img
        self.model.photo.current_tk_image = imgtk
        self.update_photo_label()

    def update_photo_label(self) -> None:
        self.frame.photo_frame.photo_label.configure(image=self.model.photo.current_tk_image)