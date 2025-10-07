from app.models.preprocessing import convert_image_to_tkinter


class ExtractorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.extractor_combobox.bind("<<ComboboxSelected>>", self.on_change)
        self._bind()

    def _bind(self) -> None:
        extractor_names = self.model.extractor.get_extractor_keys()
        self.frame.settings_frame.extractor_combobox['values'] = extractor_names
        self.model.extractor.instance = self.model.extractor.extractor_dict[extractor_names[0]]
        self.update_image()

    def on_change(self, event) -> None:
        chosen_extractor = self.get_selected_from_combobox()
        self.model.extractor.current_extractor = self.model.extractor.extractor_dict[chosen_extractor]
        self.update_image()

    def get_selected_from_combobox(self) -> str:
        result_extractor = self.frame.settings_frame.extractor_combobox.get()
        return result_extractor

    def update_image(self):
        keypoint_image = self.model.extractor.get_keypoint_image(self.model.photo.current_cv2_image)
        self.model.photo.current_tk_image = convert_image_to_tkinter(keypoint_image)
        self.update_photo_label()

    def update_photo_label(self) -> None:
        self.frame.photo_frame.photo_label.configure(image=self.model.photo.current_tk_image)
