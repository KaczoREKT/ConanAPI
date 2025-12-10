import cv2
import pytesseract
from PIL import Image
from app.other.config import config
config = config['ocr']
pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']

class OCR:
    def __init__(self):
        pass

    def perform_ocr(self, keypoint_images: list) -> str:
        result = ""
        for image in keypoint_images:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ocr_result = pytesseract.image_to_string(image=img_rgb, 
                                                     lang='pl',
                                                     config = r'--tessdata-dir "C:\praktykant\Tesseract-OCR\tessdata"')
            if ocr_result.strip() != "":
                print("OCR Result for one keypoint image:" + ocr_result)
                result += ocr_result
        return result



        