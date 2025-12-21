import logging

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
        self.instance.setInputParams(size=str_to_tuple(self.parameters['size']['default']),
                                     scale=self.parameters['scale']['default'],
                                     mean=self.parameters['mean']['default'],
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
        except SystemError as e:
            logger.error(e)

    def set_parameters(self):
        self.instance.setBinaryThreshold(self.parameters['binary_threshold']['default'])
        self.instance.setPolygonThreshold(self.parameters['polygon_threshold']['default'])
        self.instance.setInputParams(size=str_to_tuple(self.parameters['size']['default']),
                                     scale=self.parameters['scale']['default'],
                                     mean=str_to_tuple(self.parameters['mean']['default']),
                                     swapRB=self.parameters['swapRB']['default'])

class Extractor:
    def __init__(self):
        self.extractor_dict = {
            'EAST': EAST(),
            'DB50': DB50(),
            'DB18': DB18(),
        }
        self.current_extractor = self.extractor_dict['EAST']
        self.current_image_keypoints = None

    def get_keypoint_image(self, image):
        main_keypoint_image, keypoint_images = self.current_extractor.extract(image)
        return main_keypoint_image, keypoint_images

    def get_extractor_keys(self):
        return list(self.extractor_dict.keys())


if __name__ == "__main__":
    pass
