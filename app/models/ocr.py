import os
from pathlib import Path

import cv2
import numpy
import pytesseract
from PIL import Image
from app.other.config import main_config
config = main_config['ocr']
pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']
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

    def sort_reading_order(self, keypoint_images, line_threshold=10):
        boxes = sorted(keypoint_images, key=lambda b: (b["y"], b["x"]))

        rows = []
        for box in boxes:
            placed = False
            for row in rows:
                if abs(box["y"] - row["mean_y"]) <= line_threshold:
                    row["items"].append(box)
                    row["mean_y"] = sum(b["y"] for b in row["items"]) / len(row["items"])
                    placed = True
                    break
            if not placed:
                rows.append({"mean_y": box["y"], "items": [box]})

        rows.sort(key=lambda r: r["mean_y"])

        ordered = []
        for row in rows:
            row["items"].sort(key=lambda b: b["x"])
            ordered.extend(row["items"])

        return ordered

    def perform_ocr(self, image: numpy.ndarray, keypoints: dict) -> str:
        result = ""

        ordered_boxes = self.sort_reading_order(keypoints, line_threshold=10)

        for i, box in enumerate(ordered_boxes):
            current_image = image.copy()
            current_image = current_image[box["y"]:box["y"] + box["h"], box["x"]:box["x"] + box["w"]]

            img_rgb = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
            self.save_image(f"ocr_box_{i}.png", current_image)
            ocr_result = pytesseract.image_to_string(current_image, lang='pol')

            if ocr_result.strip():
                result += ocr_result

        return result



        