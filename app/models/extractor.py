import logging

logger = logging.getLogger(__name__)

import os
from app.other.config import Config
import cv2
import numpy as np
from app.models.preprocessing import to_gray, mask


class AbstractFeatureExtractor:
    def __init__(self):
        self.name = None
        self.parameters = None
        self.instance = None

    def extract(self, image):
        keypoint_image = image.copy()
        gray_image = to_gray(keypoint_image)
        gray_blur = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
        keypoint, descriptor = self.instance.detectAndCompute(gray_blur, None)
        keypoint_image = cv2.drawKeypoints(
            keypoint_image, keypoint, None, color=(0, 255, 0),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        return keypoint_image


class AbstractTextExtractor:
    def __init__(self):
        self.name = None
        self.parameters = None
        self.instance = None

    def set_parameters(self):
        raise NotImplementedError

    def extract(self, image):
        boxes, confidences = self.instance.detect(image)
        main_keypoint_image = image.copy()
        sub_keypoint_images = []
        for box in boxes:  
            pts = np.array(box, dtype=int).reshape(-1, 2)
            x, y, w, h = cv2.boundingRect(pts)
            sub_keypoint_images.append(main_keypoint_image[y:y+h, x:x+w])
            cv2.polylines(main_keypoint_image, [pts], isClosed=True, color=(0, 255, 0), thickness=1)
        return main_keypoint_image, sub_keypoint_images


class AbstractStatExtractor:
    def __init__(self):
        self.name = None
        self.roi = None

    def extract(self, image):
        val = self.get_value(image)
        output_image = image.copy()
        if self.roi:
            x, y, w, h = self.roi
            cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(output_image, f"{self.name}: {val}", (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return output_image

    def get_value(self, image):
        raise NotImplementedError


class SIFT(AbstractFeatureExtractor):
    def __init__(self):
        super().__init__()
        self.name = "SIFT"
        self.parameters = {
            'nfeatures': 10,
            'nOctaveLayers': 3,
            'contrastThreshold': 4,
            'edgeThreshold': 10,
            'sigma': 16
        }
        self.instance = cv2.SIFT_create()


class ORB(AbstractFeatureExtractor):
    def __init__(self):
        super().__init__()
        self.name = "ORB"
        self.instance = cv2.ORB_create()


class EAST(AbstractTextExtractor):
    def __init__(self):
        super().__init__()
        self.name = "EAST"
        self.parameters = {
            'confidence_threshold': 0.05,
            'nms_threshold': 0.04,
            'size': (1920, 1088),
            'scale': 1.0 / 255.0,
            'mean': (123.68, 116.78, 103.94),
            'swapRB': True,
            'crop': False
        }
        self.east_model_path = os.path.join(os.getcwd(), 'frozen_east_text_detection.pb')
        self.instance = cv2.dnn.TextDetectionModel_EAST(self.east_model_path)
        self.set_parameters()

    def set_parameters(self):
        self.instance.setConfidenceThreshold(self.parameters['confidence_threshold'])
        self.instance.setNMSThreshold(self.parameters['nms_threshold'])
        self.instance.setInputParams(size=self.parameters['size'],
                                     scale=self.parameters['scale'],
                                     mean=self.parameters['mean'],
                                     swapRB=self.parameters['swapRB'])


class DB50(AbstractTextExtractor):
    def __init__(self):
        self.name = "DB50"
        self.parameters = {
            'binary_threshold': 0.5,
            'polygon_threshold': 0.4,
            'size': (1920, 1088),
            'scale': 1.0 / 255.0,
            'mean': (123.68, 116.78, 103.94),
            'swapRB': True,
            'crop': True

        }
        self.model_path = os.path.join(os.getcwd(), 'DB_TD500_resnet50.onnx')
        try:
            self.instance = cv2.dnn_TextDetectionModel_DB(self.model_path)
            self.set_parameters()
        except SystemError as e:
            logger.error(e) 

    def set_parameters(self):
        self.instance.setBinaryThreshold(self.parameters['binary_threshold'])
        self.instance.setPolygonThreshold(self.parameters['polygon_threshold'])
        self.instance.setInputParams(size=self.parameters['size'],
                                     scale=self.parameters['scale'],
                                     mean=self.parameters['mean'],
                                     swapRB=self.parameters['swapRB'])


class DB18(AbstractTextExtractor):
    def __init__(self):
        self.name = "DB18"
        self.parameters = {

        }

        self.model_path = os.path.join(os.getcwd(), 'DB_TD500_resnet18.onnx')
        try:
            self.instance = cv2.dnn_TextDetectionModel_DB(self.model_path)
            self.set_parameters()
        except SystemError as e:
            logger.error(e) 
            
    def set_parameters(self):
        self.instance.setBinaryThreshold(self.parameters['binary_threshold']['default'])
        self.instance.setPolygonThreshold(self.parameters['polygon_threshold']['default'])
        self.instance.setInputParams(size=self.parameters['size']['default'],
                                     scale=self.parameters['scale']['default'],
                                     mean=self.parameters['mean']['default'],
                                     swapRB=self.parameters['swapRB']['default'])


class HealthExtractor(AbstractStatExtractor):
    def __init__(self):
        super().__init__()
        self.name = "Health"
        self.roi = None

        # Zakres koloru zielonego w HSV
        # H: 35-90 (zielony), S: 50-255 (nasycony), V: 50-255 (jasny)
        self.lower_green = np.array([35, 50, 50])
        self.upper_green = np.array([90, 255, 255])

    def extract(self, image):
        if self.roi is None:
            print("Szukam paska zdrowia...")
            self.calibrate(image)

            if self.roi is None:
                cv2.putText(image, "HP BAR NOT FOUND", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return image

        val = self.get_value(image)
        output_image = image.copy()
        x, y, w, h = self.roi

        cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(output_image, f"HP: {val}%", (x, y + h + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return output_image

    def calibrate(self, image):
        """Automatycznie wykrywa pasek zdrowia na podstawie koloru i kształtu"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # Znajdź kontury na masce
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width = image.shape[:2]
        best_roi = None
        max_area = 0

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # FILTR 1: Pozycja (Musi być w lewej górnej ćwiartce)
            if x > width / 2 or y > height / 2:
                continue

            # FILTR 2: Kształt (Pasek jest szeroki, a nie wysoki)
            aspect_ratio = w / float(h)
            if aspect_ratio < 3.0:  # Musi być co najmniej 3x szerszy niż wyższy
                continue

            # FILTR 3: Rozmiar (Ignoruj małe plamki)
            area = w * h
            if area < 500:
                continue

            # Wybieramy największy pasujący obiekt (to prawdopodobnie pasek HP)
            if area > max_area:
                max_area = area
                best_roi = (x, y, w, h)

        if best_roi:
            self.roi = best_roi
            print(f"Skalibrowano pasek zdrowia: {self.roi}")
        else:
            print("Nie udało się znaleźć paska zdrowia. Upewnij się, że masz pełne HP!")

    def get_value(self, image):
        if self.roi is None: return 0

        x, y, w, h = self.roi
        crop = image[y:y + h, x:x + w]
        if crop.size == 0: return 0

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)

        non_zero = cv2.findNonZero(mask)
        if non_zero is None: return 0
        rightmost_point = np.max(non_zero[:, 0, 0])
        percentage = int(((rightmost_point + 1) / w) * 100)

        return  min(100, max(0, percentage))


class Extractor:
    def __init__(self):
        self.extractor_dict = {
            'SIFT': SIFT(),
            'ORB': ORB(),
            'EAST': EAST(),
            'DB50': DB50(),
            'DB18': DB18(),
            'Health': HealthExtractor()
        }
        self.current_extractor = self.extractor_dict['SIFT']

    def get_keypoint_image(self, image):
        main_keypoint_image, keypoint_images = self.current_extractor.extract(image)
        return main_keypoint_image, keypoint_images

    def get_extractor_keys(self):
        return list(self.extractor_dict.keys())


if __name__ == "__main__":
    health_extractor = HealthExtractor()
    test_image_path = "../../test/Screenshots/Monster_Hunter_Wilds/mh_test_image_2.png"
    test_image = cv2.imread(test_image_path)
    health_extractor.calibrate(test_image)
    cv2.imshow("okno", health_extractor.extract(test_image))
    cv2.waitKey(0)
    middle_health_image_path = "../../test/Screenshots/Monster_Hunter_Wilds/mh_test_image_middle_hp.jpg"
    middle_image = cv2.imread(middle_health_image_path)
    image = health_extractor.extract(middle_image)
    cv2.imshow("okno", image)
    cv2.waitKey(0)
    print(health_extractor.get_value(test_image))
