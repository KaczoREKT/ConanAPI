import logging
logger = logging.getLogger(__name__)

import os

import cv2
import numpy as np
from app.models.preprocessing import to_gray, mask


class Extractor:
    def __init__(self):
        self.extractor_dict = {
            'SIFT': SIFT(),
            'ORB': ORB(),
            'EAST': EAST()

        }
        self.current_extractor = self.extractor_dict['SIFT']


    def get_keypoint_image(self, image):
        return self.current_extractor.extract(image)

    def get_extractor_keys(self):
        return list(self.extractor_dict.keys())

class AbstractExtractor:
    def __init__(self):
        self.name = None
        self.parameters = None
        self.instance = None


    def extract(self, image):
        gray_image = to_gray(image)
        gray_blur = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
        keypoint, descriptor = self.instance.detectAndCompute(gray_blur, None)
        print(self.instance)
        print("wykryto ")
        print(len(keypoint))
        keypoint_image = cv2.drawKeypoints(
            image, keypoint, None, color=(0, 255, 0),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        return keypoint_image


class SIFT(AbstractExtractor):
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


class ORB(AbstractExtractor):
    def __init__(self):
        super().__init__()
        self.name = "ORB"
        self.instance = cv2.ORB_create()

class EAST(AbstractExtractor):
    def __init__(self):
        super().__init__()
        self.name = "EAST"
        self.parameters = {
            'confidence_threshold': 0.5,
            'nms_threshold': 0.4,
            'size': (320, 320),
            'scale': 1.0 / 255.0,
            'mean': (123.68, 116.78, 103.94),
            'swapRB': True,
            'crop': False
        }
        self.east_model_path = os.path.join(os.getcwd(), r'app\other\frozen_east_text_detection.pb')
        self.instance = cv2.dnn.TextDetectionModel_EAST(self.east_model_path)
        self.instance.setConfidenceThreshold(self.parameters['confidence_threshold'])
        self.instance.setNMSThreshold(self.parameters['nms_threshold'])
        self.instance.setInputParams(
            scale=self.parameters['scale'],
            size=self.parameters['size'],
            mean=self.parameters['mean'],
            swapRB=self.parameters['swapRB'],
            crop=self.parameters['crop']
        )


    def extract(self, image):
        orig_image = image.copy()
        inpaint_mask = np.zeros(orig_image.shape[:2], dtype=np.uint8)
        boxes, confs = self.instance.detect(orig_image)
        print('Liczba wykrytych boxów:', len(boxes))
        print('Confidence:', confs)
        for box in boxes:
            cv2.fillPoly(inpaint_mask, [np.array(box, np.int32)], 255)
        inpainted_east_image = cv2.inpaint(orig_image, inpaint_mask, inpaintRadius=5,
                                               flags=cv2.INPAINT_NS)
        return inpainted_east_image



if __name__ == "__main__":
    extractor = SIFT()
    img = cv2.imread(os.path.join(os.getcwd(), '20250924190109_1.jpg'))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)
    print("Liczba wykrytych punktów:", len(kp))
    img_kp = cv2.drawKeypoints(img, kp, None, (0, 255, 0), 4)
    cv2.imshow("SIFT test", img_kp)
    cv2.waitKey(0)



