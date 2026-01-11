import glob
import json
import logging
from pathlib import Path

import easyocr
from easyocr.craft import CRAFT
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

from src.models.evaluation import csv_yolo_to_coco, predictions_to_coco, yolo_txt_to_coco
from src.other.utils import str_to_tuple

logger = logging.getLogger(__name__)

import os
from src.other.config import Config
import cv2
import numpy as np


class AbstractTextExtractor:
    def __init__(self):
        self.name = None
        self.parameters = None
        self.instance = None

    def set_parameters(self):
        raise NotImplementedError

    def extract(self, image):
        boxes, confidences = self.instance.detect(image)
        keypoint_image = image.copy()
        keypoints = []
        for box in boxes:
            pts = np.array(box, dtype=int).reshape(-1, 2)
            x, y, w, h = cv2.boundingRect(pts)
            keypoints.append({
                'x': max(0, x),
                'y': max(0, y),
                'w': max(0, w),
                'h': max(0, h)
            })
            cv2.polylines(keypoint_image, [pts], isClosed=True, color=(0, 255, 0), thickness=1)
        return keypoint_image, keypoints

class EAST(AbstractTextExtractor):
    def __init__(self):
        super().__init__()
        self.name = "EAST"
        self.parameters = Config("parameters/east.yaml")
        self.east_model_path = os.path.join(os.getcwd(), 'frozen_east_text_detection.pb')
        try:
            self.instance = cv2.dnn.TextDetectionModel_EAST(self.east_model_path)
            self.set_parameters()
        except SystemError as e:
            logger.error(e)

    def set_parameters(self):
        self.instance.setConfidenceThreshold(self.parameters['confidence_threshold']['default'])
        self.instance.setNMSThreshold(self.parameters['nms_threshold']['default'])
        print(str_to_tuple(self.parameters['size']['default']))
        self.instance.setInputParams(size=str_to_tuple(self.parameters['size']['default']),
                                     scale=self.parameters['scale']['default'],
                                     mean=str_to_tuple(self.parameters['mean']['default']),
                                     swapRB=self.parameters['swapRB']['default'])


class DB50(AbstractTextExtractor):
    def __init__(self):
        self.name = "DB50"
        self.parameters = Config("parameters/db50.yaml")
        self.model_path = os.path.join(os.getcwd(), 'DB_TD500_resnet50.onnx')
        try:
            self.instance = cv2.dnn_TextDetectionModel_DB(self.model_path)
            self.set_parameters()
        except SystemError as e:
            logger.error(e)

    def set_parameters(self):
        self.instance.setBinaryThreshold(self.parameters['binary_threshold']['default'])
        self.instance.setPolygonThreshold(self.parameters['polygon_threshold']['default'])
        self.instance.setInputParams(size=str_to_tuple(self.parameters['size']['default']),
                                     scale=self.parameters['scale']['default'],
                                     mean=str_to_tuple(self.parameters['mean']['default']),
                                     swapRB=self.parameters['swapRB']['default'])


class DB18(AbstractTextExtractor):
    def __init__(self):
        self.name = "DB18"
        self.parameters = Config("parameters/db18.yaml")

        self.model_path = os.path.join(os.getcwd(), 'DB_TD500_resnet18.onnx')
        try:
            self.instance = cv2.dnn_TextDetectionModel_DB(self.model_path)
            self.set_parameters()
            print("Dobry model")
        except SystemError as e:
            logger.error(e)

    def set_parameters(self):
        self.instance.setBinaryThreshold(self.parameters['binary_threshold']['default'])
        self.instance.setPolygonThreshold(self.parameters['polygon_threshold']['default'])
        self.instance.setInputParams(size=str_to_tuple(self.parameters['size']['default']),
                                     scale=self.parameters['scale']['default'],
                                     mean=str_to_tuple(self.parameters['mean']['default']),
                                     swapRB=self.parameters['swapRB']['default'])

class MyCRAFT(AbstractTextExtractor):
    def __init__(self):
        self.name = "CRAFT"
        self.parameters = Config("parameters/craft.yaml")
        self.instance = easyocr.Reader(['pl', 'en'], gpu=True)
        self.set_parameters()

    def set_parameters(self):
        pass

    def extract(self, image):
        horizontal_list, free_list = self.instance.detect(image,
                                                          min_size=self.parameters['min_size']['default'],
                                                          text_threshold=self.parameters['text_threshold']['default'],
                                                          link_threshold=self.parameters['link_threshold']['default'],
                                                          low_text=self.parameters['low_text']['default'],
                                                          canvas_size=self.parameters['canvas_size']['default'],
                                                          mag_ratio=self.parameters['mag_ratio']['default'],
                                                          slope_ths=self.parameters['slope_ths']['default'],
                                                          ycenter_ths=self.parameters['ycenter_ths']['default'],
                                                          height_ths=self.parameters['height_ths']['default'],
                                                          width_ths=self.parameters['width_ths']['default'],
                                                          add_margin=self.parameters['add_margin']['default'],
                                                          optimal_num_chars=self.parameters['optimal_num_chars']['default'])
        keypoint_image = image.copy()
        keypoints = []

        for group in horizontal_list:
            for (x_min, x_max, y_min, y_max) in group:
                x_min, x_max, y_min, y_max = map(int, (x_min, x_max, y_min, y_max))

                pts = np.array([
                    [x_min, y_min],
                    [x_max, y_min],
                    [x_max, y_max],
                    [x_min, y_max],
                ], dtype=np.int32)

                x, y, w, h = cv2.boundingRect(pts)
                keypoints.append({'x': max(0, x), 'y': max(0, y), 'w': max(0, w), 'h': max(0, h)})

                cv2.polylines(keypoint_image, [pts], True, (0, 255, 0), 1)
        for group in free_list:
            for quad in group:
                pts = np.array(quad, dtype=np.int32)
                x, y, w, h = cv2.boundingRect(pts)
                keypoints.append({'x': max(0, x), 'y': max(0, y), 'w': max(0, w), 'h': max(0, h)})
                cv2.polylines(keypoint_image, [pts], True, (0, 255, 0), 1)

        return keypoint_image, keypoints

class Extractor:
    def __init__(self):
        self.extractor_dict = {
            'EAST': EAST(),
            'DB50': DB50(),
            'DB18': DB18(),
            'CRAFT': MyCRAFT()
        }
        self.current_extractor = self.extractor_dict['EAST']
        self.current_image_keypoints = None

    def get_keypoint_image(self, image):
        main_keypoint_image, keypoint_images = self.current_extractor.extract(image)
        return main_keypoint_image, keypoint_images

    def get_extractor_keys(self):
        return list(self.extractor_dict.keys())


if __name__ == "__main__":
    # Dostosuj ścieżki
    labels_dir = '../../test/Screenshots/Metroid Prime/Metroid_Prime_yolo'  # *.txt dla każdego img
    images_dir = '../../test/Screenshots/Metroid Prime/'
    images_path = Path(images_dir)

    print(os.listdir(images_dir))
    test_images = sorted(
        list(images_path.glob("image_*.png")) +
        list(images_path.glob("image_*.jpg")) +
        list(images_path.glob("image_*.jpeg"))
    )
    print("Test images:", len(test_images), [p.name for p in test_images])

    extractor = Extractor()
    models = ['EAST', 'DB50', 'DB18', 'CRAFT']

    # GT → COCO
    coco_gt = yolo_txt_to_coco(labels_dir, images_dir)
    gt_file = 'gt_line_level.json'
    with open(gt_file, 'w') as f:
        json.dump(coco_gt, f)
    gt_coco = COCO(gt_file)

    print(f"GT loaded: {len(gt_coco.imgs)} imgs, {len(gt_coco.anns)} anns")

    results = "| Model | mAP@0.5 | Prec | Rec | F1   |\n|-------|---------|------|-----|-----|\n"

    for model_name in models:
        print(f"Evaluating {model_name}...")
        extractor.current_extractor = extractor.extractor_dict[model_name]

        all_preds = []  # lista annotations dla WSZYSTKICH test imgs

        for img_path in test_images:
            image = cv2.imread(str(img_path))
            print(str(img_path))
            _, keypoints = extractor.current_extractor.extract(image)  # FIX: current_extractor.extract!

            img_name = os.path.basename(img_path)
            img_obj = next((img for img in coco_gt['images'] if img['file_name'] == img_name), None)
            if img_obj:
                pred_anns = predictions_to_coco(keypoints, img_obj['id'])
                all_preds.extend(pred_anns)

        # Zapisz DT jako lista anns
        dt_file = f'dt_{model_name}.json'
        with open(dt_file, 'w') as f:
            json.dump(all_preds, f)  # TYLKO lista!

        coco_dt = gt_coco.loadRes(dt_file)
        coco_eval = COCOeval(gt_coco, coco_dt, 'bbox')
        coco_eval.params.imgIds = [img['id'] for img in coco_gt['images'] if
                                   img['file_name'] in [os.path.basename(p) for p in test_images]]
        coco_eval.evaluate()
        coco_eval.accumulate()
        coco_eval.summarize()

        ap = coco_eval.stats[0]  # AP@IoU=0.50:0.95
        ap50 = coco_eval.stats[1]  # AP@0.5
        prec = coco_eval.stats[8]
        rec = coco_eval.stats[9]
        f1 = 2 * prec * rec / (prec + rec + 1e-6)

        results += f"| {model_name} | {ap50:.3f} | {prec:.3f} | {rec:.3f} | {f1:.3f} |\n"

    print(results)

