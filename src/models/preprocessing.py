import cv2
from PIL import Image, ImageTk
import numpy as np
import logging

logger = logging.getLogger(__name__)

def resize(image, size=(128, 128)):
    return cv2.resize(image, size)


def load_image(screenshot_path: str):
    bgr = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    return bgr


def convert_image_to_tkinter(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = resize(img, size=(960, 540))
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    return imgtk


def mask(image):
    _, mask = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
    return mask.astype(np.uint8)

def clean(image):
    return image

def preprocess_clahe_bilateral(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 5, 50, 50)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    return cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)


def preprocess_clahe_sharp(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    blur = cv2.GaussianBlur(eq, (0, 0), 1.0)
    sharp = cv2.addWeighted(eq, 1.6, blur, -0.6, 0)
    return cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR)


def preprocess_clahe_close(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    closed = cv2.morphologyEx(eq, cv2.MORPH_CLOSE, kernel)  # [web:456]
    return cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)

def preprocess_clahe_otsu(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    eq = clahe.apply(gray)
    eq = cv2.GaussianBlur(eq, (3,3), 0)
    _, th = cv2.threshold(eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

def preprocess_clahe_adaptive(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    eq = clahe.apply(gray)
    th = cv2.adaptiveThreshold(
        eq, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )
    return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

class Preprocessing:
    def __init__(self):
        self.preprocessing_dict = {
            'CLEAN': clean,
            'CLAHE': preprocess_clahe_otsu,
            'BILATERAL': preprocess_clahe_bilateral,
            'SHARP': preprocess_clahe_sharp,
            'CLOSE': preprocess_clahe_close,
            'ADAPTIVE': preprocess_clahe_adaptive
        }
        self.current_preprocessing = self.preprocessing_dict['BILATERAL']

    def get_preprocessing_keys(self):
        return list(self.preprocessing_dict.keys())