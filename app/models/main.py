from app.models.extractor import Extractor
from app.models.photo import Photo
from app.models.ocr import OCR

class Model:
    def __init__(self):
        self.photo = Photo()
        self.extractor = Extractor()
        self.ocr = OCR()