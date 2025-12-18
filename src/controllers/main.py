from app.controllers.extractor import ExtractorController
from app.controllers.photo import PhotoController
from app.controllers.ocr import OCRController
from app.models.main import Model
from app.views.main import View

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.photo_controller = PhotoController(model, view)
        self.extractor_controller = ExtractorController(model, view)
        self.ocr_controller = OCRController(model, view)

    def start(self):
        self.view.start_mainloop()

