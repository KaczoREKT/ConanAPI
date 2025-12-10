import cv2
import pytesseract
from PIL import Image
from app.other.config import config
config = config['ocr']
pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']

class OCR:
    def __init__(self):
        pass

    def perform_ocr(self, img_cv) -> str:
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        ocr_result = pytesseract.image_to_string(img_rgb)
        return ocr_result



        