import cv2
from PIL import Image, ImageTk
import numpy as np
import logging
logger = logging.getLogger(__name__)

def to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def resize(image, size=(128, 128)):
    return cv2.resize(image, size)

def normalize(image):
    return image / 255.0

def load_image(screenshot_path: str):
    img = cv2.imread(screenshot_path)
    img = resize(img, size=(960, 540))
    return img

def convert_image_to_tkinter(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    return imgtk

def mask(image):
    _, mask = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)
    return mask.astype(np.uint8)