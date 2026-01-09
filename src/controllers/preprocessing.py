from src.models.preprocessing import convert_image_to_tkinter


class PreprocessingController:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.preprocessing_combobox.bind("<<ComboboxSelected>>", self.on_change)
        self._bind()

    def _bind(self) -> None:
        preprocessing_names = self.model.preprocessing.get_preprocessing_keys()
        self.frame.settings_frame.preprocessing_combobox['values'] = preprocessing_names
        self.frame.settings_frame.preprocessing_combobox.current(0)

    def on_change(self, event) -> None:
        chosen_preprocessing = self.frame.settings_frame.preprocessing_combobox.get()
        self.model.preprocessing.current_preprocessing = self.model.preprocessing.preprocessing_dict[chosen_preprocessing]
        preprocessed_image = self.model.preprocessing.current_preprocessing(self.model.photo.current_cv2_image.copy())
        self.model.photo.current_preprocessed_image = preprocessed_image
        self.model.photo.current_tk_image = convert_image_to_tkinter(preprocessed_image)
        self._update_photo_label()

    def _update_photo_label(self) -> None:
        self.frame.photo_frame.photo_label.configure(image=self.model.photo.current_tk_image)
