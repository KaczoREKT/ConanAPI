from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import ImageGrab
import logging
from app.utils.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def health_bar_color_detection(image, parameters=None):
    def create_mask(hsv_image):
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask = mask1 + mask2
        return mask
    health_bar = image.copy()

    if config['test']:
        x1, x2, y1, y2 = get_trackbar_parameters("Color detection", parameters)
    else:
        x1, x2, y1, y2 = parameters['x1'][0], parameters['x2'][0], parameters['y1'][0], parameters['y2'][0]

    hsv_image = cv2.cvtColor(health_bar, cv2.COLOR_BGR2HSV)
    mask = create_mask(hsv_image)

    filled = np.sum(mask > 0)
    total = mask.size
    percent = filled / total * 100
    return percent


def load_images():
    """
    Returns a list of images from the "Screenshots" folder.
    :return: images list
    """
    base_path = Path(__file__).resolve().parent
    imgs_dir = base_path / "Screenshots"
    images = list()
    for image_path in imgs_dir.glob("*.jpg"):
        images.append(cv2.imread(str(image_path)))
    return images

def create_cv2_gui(parameters, gui_name=None):
    gui_name = "Color detection"
    cv2.namedWindow(gui_name, cv2.WINDOW_NORMAL)
    create_trackbars(gui_name, parameters)

def gui_thread(image, parameters, gui_name=None):
    while True:
        get_trackbar_parameters(gui_name, parameters)
        new_image = update_image_x_y(image, parameters)
        detection_result = health_bar_color_detection(new_image, parameters)
        print(detection_result)
        cv2.imshow(gui_name, image)
        key = cv2.waitKey(16)
        if key == 27:  # ESC key to exit
            break

def update_image_x_y(image, parameters):
    x1 = parameters['x1'][0]
    x2 = parameters['x2'][0]
    y1 = parameters['y1'][0]
    y2 = parameters['y2'][0]
    new_image = image[x1:x2, y1:y2]
    return new_image


def create_trackbars(gui_name, parameters):
    for key, value in parameters.items():
        try:
            cv2.createTrackbar(key, gui_name, value[0], value[1], lambda x: None)
        except TypeError:
            cv2.createTrackbar(key, gui_name, int(value[0]), int(value[1]), lambda x: None)


def get_trackbar_parameters(gui_name, parameters):
    for key in parameters.keys():
        parameters[key][0] = cv2.getTrackbarPos(key, gui_name)
    return parameters

def get_current_window_screen(parameters):
    x1, x2, y1, y2 = parameters['x1'][0], parameters['x2'][0], parameters['y1'][0], parameters['y2'][0]
    left, right = min(x1, x2), max(x1, x2)
    top, bottom = min(y1, y2), max(y1, y2)
    bbox = (left, top, right, bottom)
    img = ImageGrab.grab(bbox=bbox)
    frame_rgb = np.array(img)  # ndarray w RGB
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    show_image(frame_rgb)
    return frame_bgr

def show_image(image):
    plt.imshow(image)
    plt.show()

def pipeline(screen, parameters, gui_name):
    detection_result = health_bar_color_detection(screen, parameters)
    print(detection_result)
    gui_thread(screen, parameters, gui_name)

def main():
    image_shape = (1080, 1920, 3)
    parameters = {'x1': [40, image_shape[1]],
            'x2': [500, image_shape[1]],
            'y1': [20, image_shape[0]],
            'y2': [120, image_shape[0]]
    }
    gui_name = 'Color detection'
    create_cv2_gui(parameters, gui_name)
    while True:
        screen = get_current_window_screen(parameters)
        pipeline(screen, parameters, gui_name)

if __name__ == "__main__":
    main()
