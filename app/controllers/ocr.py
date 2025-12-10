class OCRController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.frame = view.frames['main_frame']
        self.frame.settings_frame.ocr_button.config(command=self.perform_ocr)
    
    def perform_ocr(self):
        ocr_result = self.model.ocr.perform_ocr(self.model.photo.current_cv2_image)
        self.frame.ocr_frame.ocr_label.config(text=ocr_result)