from .evaluation import Evaluation
from .extractor import Extractor
from .photo import Photo
from .ocr import OCR
from .preprocessing import Preprocessing
from .windowcapture import WindowCapture

class Model:
    def __init__(self):
        self.photo = Photo()
        self.extractor = Extractor()
        self.ocr = OCR()
        self.windowcapture = WindowCapture()
        self.preprocessing = Preprocessing()
        self.evaluation = Evaluation()