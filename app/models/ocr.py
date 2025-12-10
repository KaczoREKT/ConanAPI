import os
from pathlib import Path

import cv2
import pytesseract
from PIL import Image
from app.other.config import main_config
config = main_config['ocr']
# pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']
# tessdata_dir_config = r'--tessdata-dir "C:\praktykant\Tesseract-OCR\tessdata"'
class OCR:
    def __init__(self):
        pass

    def save_image(self, filename, image):
        folder_path = Path(config['output_folder'])
        if not Path(folder_path).exists():
            os.mkdir(folder_path)
        if not Path(os.path.join(folder_path, filename)).exists():
            cv2.imwrite(os.path.join(folder_path, filename), image)

    def perform_ocr(self, keypoint_images: list) -> str:
        result = ""
        for i, image in enumerate(keypoint_images):
            self.save_image(f"{i}.png", image)
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ocr_result = pytesseract.image_to_string(image=img_rgb, 
                                                    #  lang='pol',
                                                    #  config = tessdata_dir_config
                                                    )
            if ocr_result.strip() != "":
                result += ocr_result
        return result



        