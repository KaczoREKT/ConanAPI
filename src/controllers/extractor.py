from src.models.preprocessing import convert_image_to_tkinter
import threading
import time
from src.other.utils import crop_img
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
        capture_thread = threading.Thread(target=self._capture_loop)
        capture_thread.start()

    def _capture_loop(self) -> numpy.ndarray:
        while True:
            screenshot = self.model.windowcapture.get_screenshot()
            screenshot = crop_img(screenshot, top=30, bottom=25)
            screenshot = self.model.preprocessing.current_preprocessing(screenshot)
            keypoints = self.update_image(screenshot)
            ocr_result = self.model.ocr.perform_ocr(screenshot, keypoints)
            self.frame.ocr_frame.ocr_label.config(text=ocr_result)
            time.sleep(0.1)

    def _update_extractor_parameters(self, *args) -> None:
        current_extractor_parameters = self.model.extractor.current_extractor.parameters.config
        for key, value in self.frame.parameters_frame.vars.items():
            current_extractor_parameters[key]['default'] = value.get()

    def _on_change(self, event) -> None:
        chosen_extractor = self._get_selected_from_combobox()
        self.model.extractor.current_extractor = self.model.extractor.extractor_dict[chosen_extractor]
        current_extractor_parameters = self.model.extractor.current_extractor.parameters.config
        self.frame.parameters_frame.create_parameters_widgets(current_extractor_parameters)
        for key, value in self.frame.parameters_frame.vars.items():
            value.trace_add("write", self._update_extractor_parameters)


    def _get_selected_from_combobox(self) -> str:
        result_extractor = self.frame.settings_frame.extractor_combobox.get()
        return result_extractor

    def update_image(self, image=None):
        if image is None:
            image = self.model.photo.current_preprocessed_image
        self.model.extractor.current_extractor.set_parameters()
        self.model.extractor.parameters = self.frame.parameters_frame.get_parameters()
        keypoint_image, keypoints = self.model.extractor.get_keypoint_image(image)
        self.model.extractor.current_image_keypoints = keypoints
        self.model.photo.current_tk_image = convert_image_to_tkinter(keypoint_image)
        self._update_photo_label()
        return keypoints

    def _update_photo_label(self) -> None:
        self.frame.photo_frame.photo_label.configure(image=self.model.photo.current_tk_image)
