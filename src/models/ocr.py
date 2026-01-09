import os
import re
from pathlib import Path

import cv2
import easyocr
import numpy
import pytesseract
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch
from src.other.config import config
config = config['ocr']
# pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']
# tessdata_dir_config = r'--tessdata-dir "C:\praktykant\Tesseract-OCR\tessdata"'

class TrOCRRecognizer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
        self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed").to(self.device)

    @torch.no_grad()
    def detect(self, image):
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text

class EasyOCRRecognizer:
    def __init__(self):
        self.reader = easyocr.Reader(['pl', 'en'], gpu=True)

    def detect(self, image):
        return self.reader.recognize(image)[0][1]

class TesseractRecognizer:
    def __init__(self):
        self.reader = pytesseract.image_to_string

    def detect(self, image):
        return self.reader(image, lang='eng')

class OCR:
    def __init__(self):
        self.readerr = easyocr.Reader(['pl', 'en'], gpu=True)
        self.detector_dict = {
            'easyocr': EasyOCRRecognizer(),
            'tesseract': TesseractRecognizer(),
            'trocr': TrOCRRecognizer()
        }
        self.current_detector = self.detector_dict['easyocr']

    def get_detector_keys(self):
        return list(self.detector_dict.keys())

    def save_image(self, filename, image):
        folder_path = Path(config['output_folder'])
        if not Path(folder_path).exists():
            os.mkdir(folder_path)
        if not Path(os.path.join(folder_path, filename)).exists():
            cv2.imwrite(os.path.join(folder_path, filename), image)

    def sort_reading_order(self, boxes, line_ths_factor=0.6):
        if not boxes:
            return []

        boxes2 = []
        for b in boxes:
            b2 = dict(b)
            b2["yc"] = b["y"] + b["h"] / 2.0
            boxes2.append(b2)

        median_h = sorted([b["h"] for b in boxes2])[len(boxes2) // 2]
        line_threshold = max(2, int(line_ths_factor * median_h))

        boxes2.sort(key=lambda b: (b["yc"], b["x"]))

        rows = []
        for b in boxes2:
            placed = False
            for row in rows:
                if abs(b["yc"] - row["mean_yc"]) <= line_threshold:
                    row["items"].append(b)
                    row["mean_yc"] = sum(x["yc"] for x in row["items"]) / len(row["items"])
                    placed = True
                    break
            if not placed:
                rows.append({"mean_yc": b["yc"], "items": [b]})

        rows.sort(key=lambda r: r["mean_yc"])

        ordered = []
        for row in rows:
            row["items"].sort(key=lambda b: b["x"])
            ordered.extend(row["items"])

        return ordered

    def perform_ocr(self, image: numpy.ndarray, keypoints: dict) -> str:
        result = ""

        ordered_boxes = self.sort_reading_order(keypoints)

        for i, box in enumerate(ordered_boxes):
            current_image = image.copy()
            current_image = current_image[box["y"]:box["y"] + box["h"], box["x"]:box["x"] + box["w"]]


            ocr_result = self.current_detector.detect(current_image)

            if ocr_result:
                result += ocr_result.strip().lower() + ' '

        return result

if __name__ == "__main__":
    image = cv2.imread('../../test/Screenshots/Conan_Exiles/20250924190109_1.jpg')
    reader = TrOCRRecognizer()
    print(reader.detect(image))

        