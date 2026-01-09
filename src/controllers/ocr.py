class OCRController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.ocr_button.config(command=self.perform_ocr)
        self.frame.settings_frame.detector_combobox.bind("<<ComboboxSelected>>", self._on_change)
        self._bind()

    def _bind(self) -> None:
        detector_names = self.model.ocr.get_detector_keys()
        self.frame.settings_frame.detector_combobox['values'] = detector_names
        self.frame.settings_frame.detector_combobox.current(0)

    def _on_change(self, event) -> None:
        chosen_detector = self.frame.settings_frame.detector_combobox.get()
        self.model.ocr.current_detector = self.model.ocr.detector_dict[chosen_detector]
    
    def perform_ocr(self):
        image = self.model.photo.current_preprocessed_image
        keypoints = self.model.extractor.current_image_keypoints
        try:
            original_text = self.model.photo.screenshots_transcriptions[self.frame.settings_frame.photo_combobox.get()]
        except KeyError:
            original_text = None
        ocr_result = self.model.ocr.perform_ocr(image, keypoints)
        self.frame.ocr_frame.ocr_label.config(text=ocr_result)
        print(original_text, ocr_result)
        self.frame.ocr_frame.result_label.config(text=self.model.evaluation.full_evaluation(original_text, ocr_result))