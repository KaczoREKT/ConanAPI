from app.models.preprocessing import convert_image_to_tkinter
import threading
import time
from app.other.utils import crop_img
import numpy

class ExtractorController:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.extractor_combobox.bind("<<ComboboxSelected>>", self._on_change)
        self.frame.settings_frame.extractor_button.config(command=self.update_image)
        self.frame.settings_frame.loop_button.config(command=self.start_capture_loop)
        self._bind()

    def _bind(self) -> None:
        extractor_names = self.model.extractor.get_extractor_keys()
        self.frame.settings_frame.extractor_combobox['values'] = extractor_names
        self.frame.settings_frame.extractor_combobox.current(0)
    
    def start_capture_loop(self) -> None:
        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        capture_thread.start()

    def _capture_loop(self) -> numpy.ndarray:
        while True:
            screenshot = self.model.windowcapture.get_screenshot()
            screenshot = crop_img(screenshot, top=30, bottom=25)
            keypoint_image, keypoints = self.model.extractor.current_extractor.extract(screenshot)
            imgtk = convert_image_to_tkinter(keypoint_image)
            self.model.photo.current_cv2_image = screenshot
            self.model.photo.current_tk_image = imgtk
            self._update_photo_label()
            ocr_result = self.model.ocr.perform_ocr(screenshot, keypoints)
            self.frame.ocr_frame.ocr_label.config(text=ocr_result)
            time.sleep(0.01)

    def _on_change(self, event) -> None:
        chosen_extractor = self._get_selected_from_combobox()
        self.model.extractor.current_extractor = self.model.extractor.extractor_dict[chosen_extractor]
        self.frame.parameters_frame.create_parameters_widgets(self.model.extractor.current_extractor.parameters.config)


    def _get_selected_from_combobox(self) -> str:
        result_extractor = self.frame.settings_frame.extractor_combobox.get()
        return result_extractor

    def update_image(self):
        self.model.extractor.parameters = self.frame.parameters_frame.get_parameters()
        keypoint_image, keypoints = self.model.extractor.get_keypoint_image(self.model.photo.current_cv2_image)
        self.model.extractor.current_image_keypoints = keypoints
        self.model.photo.current_tk_image = convert_image_to_tkinter(keypoint_image)
        self._update_photo_label()

    def _update_photo_label(self) -> None:
        self.frame.photo_frame.photo_label.configure(image=self.model.photo.current_tk_image)
