import os
from pathlib import Path

from Model.VPR.new_model import pixel_art_descriptor
from config import main_config
import cv2
import numpy as np


class FeatureExtractor:
    def __init__(self):
        self.gui_name = "Zeldonator"

    def get_images_from_path(self, image_path):
        def read_image_path(image_path):
            return cv2.imread(image_path)

        def resize(image):
            # scale = 10.0
            # image = cv2.resize(image,
            #                    None,
            #                    fx=scale,
            #                    fy=scale,
            #                    interpolation=cv2.INTER_CUBIC)
            return image

        def pre_compute(image):
            gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return gray_img

        og_image = read_image_path(image_path)
        resized_image = resize(og_image)
        gray_image = pre_compute(resized_image)
        return gray_image, resized_image

    def mask(self, image):
        _, mask = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
        return mask.astype(np.uint8)

    def sift(self, gray_image, resized_image, parameters):
        sift_object = cv2.SIFT_create(*parameters)
        gray_blur = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
        keypoint, descriptor = sift_object.detectAndCompute(gray_blur, self.mask(gray_image))
        keypoint_image = cv2.drawKeypoints(
            resized_image, keypoint, None, color=(0, 255, 0),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        return keypoint_image

    def orb(self, gray_image, resized_image, parameters):
        orb_object = cv2.ORB_create(*parameters)
        gray_blur = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
        keypoint, descriptor = orb_object.detectAndCompute(gray_blur, self.mask(gray_image))
        keypoint_image = cv2.drawKeypoints(resized_image, keypoint, None,
                                           color=(0, 255, 0))
        return keypoint_image

    def hog(self, gray_image, resized_image, parameters):
        hog_object = cv2.HOGDescriptor()

    def akaze(self, gray_image, resized_image, parameters):
        akaze_object = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                                        descriptor_size=parameters[1],
                                        descriptor_channels=parameters[2],
                                        threshold=parameters[3]/1000,
                                        nOctaves=parameters[4],
                                        nOctaveLayers=parameters[5],
                                        diffusivity=cv2.KAZE_DIFF_PM_G2)
        gray_blur = cv2.GaussianBlur(gray_image, (0, 0), 1.0)
        keypoint, descriptor = akaze_object.detectAndCompute(gray_blur, self.mask(gray_image))
        keypoint_image = cv2.drawKeypoints(resized_image, keypoint, None,
                                           color=(0, 255, 0))
        return keypoint_image

    def PAHD(self, img):
        desc, im32, qimg, mask = pixel_art_descriptor(img)
        vis = im32.copy()
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return cv2.drawContours(vis, contours, -1, (0, 255, 0), 1)

    def show_gui(self, image_path):
        gray_image, resized_image = self.get_images_from_path(image_path)

        cv2.namedWindow(self.gui_name, cv2.WINDOW_NORMAL)
        extractor_map = self.initialize_extractor()
        self.create_trackbars(extractor_map)

        while True:
            parameters = self.get_trackbar_parameters(extractor_map)
            new_image = self.update_image(gray_image, resized_image, parameters)

            cv2.imshow(self.gui_name, new_image)

            key = cv2.waitKey(16)
            if key == 27:  # ESC key to exit
                break

        cv2.destroyWindow(self.gui_name)

    def get_trackbar_parameters(self, extractor_map):
        parameters = []
        for key in extractor_map.keys():
            parameters.append(cv2.getTrackbarPos(key, self.gui_name))
        return parameters

    def initialize_extractor(self):
        extractor_map = {}
        match main_config['extractor']:
            case 'SIFT':
                extractor_map = {
                    'nfeatures': [10, 100],
                    'nOctaveLayers': [3, 10],
                    'contrastThreshold': [4, 10],
                    'edgeThreshold': [10, 30],
                    'sigma': [16, 30]
                }
            case 'ORB':
                extractor_map = {
                    'nfeatures': [10, 100],
                    'scaleFactor': [1, 2],
                    'nlevels': [8, 16],
                    'edgeThreshold': [31, 100],
                    'firstLevel': [0, 8],
                    'WTA_K': [2, 5],
                    'patchSize': [31, 100],
                    'fastThreshold': [20, 100]
                }
            case 'AKAZE':
                extractor_map = {
                    'descriptor_type': [5, 5],  # 5 = DESCRIPTOR_MLDB
                    'descriptor_size': [0, 0],  # 0 = full size
                    'descriptor_channels': [3, 3],  # force 3 for MLDB
                    'threshold': [1, 10],  # maps to 0.001..0.010
                    'nOctaves': [1, 6],
                    'nOctaveLayers': [1, 6],
                    'diffusivity': [1, 1],
                }
            case 'PAHD':
                extractor_map = {}
        return extractor_map

    def create_trackbars(self, extractor_map):
        for key, value in extractor_map.items():
            try:
                cv2.createTrackbar(key, self.gui_name, value[0], value[1], lambda x: None)
            except TypeError:
                cv2.createTrackbar(key, self.gui_name, int(value[0]), int(value[1]), lambda x: None)

    def update_image(self, gray_image, resized_image, parameters):
        new_image = None
        match main_config['extractor']:
            case 'SIFT':
                new_image = self.sift(gray_image, resized_image, parameters)
            case 'ORB':
                new_image = self.orb(gray_image, resized_image, parameters)
            case 'AKAZE':
                new_image = self.akaze(gray_image, resized_image, parameters)
            case 'PAHD':
                new_image = self.PAHD(resized_image)
        return new_image


if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent  # katalog tego pliku
    imgs_dir = base_path / "zelda_items_images"  # ./zelda_items_images

    fe = FeatureExtractor()
    for image_path in imgs_dir.glob("*.png"):
        fe.show_gui(str(image_path))
