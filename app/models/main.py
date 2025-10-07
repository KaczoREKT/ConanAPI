from app.models.extractor import Extractor
from app.models.photo import Photo


class Model:
    def __init__(self):
        self.photo = Photo()
        self.extractor = Extractor()