import cv2
import numpy as np

def update(_):
    min_conf = cv2.getTrackbarPos('min_confidence', winname) / 100.0
    width = cv2.getTrackbarPos('width', winname)
    height = cv2.getTrackbarPos('height', winname)
    width = max(32, int(round(width / 32) * 32))
    height = max(32, int(round(height / 32) * 32))
    cv2.setTrackbarPos('width', winname, width)
    cv2.setTrackbarPos('height', winname, height)
    text_detector.setConfidenceThreshold(min_conf)
    text_detector.setInputSize((width, height))
    boxes, confidences = text_detector.detect(image)
    display = image.copy()
    for box in boxes:
        if len(box) == 5:
            cx, cy, w, h, angle = box
            rect = ((cx, cy), (w, h), angle)
            pts = cv2.boxPoints(rect).astype(int)
        else:
            pts = np.array(box, dtype=int).reshape(-1, 2)
        cv2.polylines(display, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    cv2.imshow(winname, cv2.resize(display, (1280, 720)))

if __name__ == '__main__':
    image_path = 'image.jpg'
    image = cv2.imread(image_path)
    east_path = '../../frozen_east_text_detection.pb'
    winname = 'EAST Text Detection'

    # Inicjalny rozmiar
    default_w = 1920
    default_h = 1080

    text_detector = cv2.dnn.TextDetectionModel_EAST(east_path)

    cv2.namedWindow(winname)
    cv2.createTrackbar('min_confidence', winname, 50, 100, update)
    cv2.createTrackbar('width', winname, default_w, 1920, update)
    cv2.createTrackbar('height', winname, default_h, 1280, update)

    # Pierwszy pokaz
    update(0)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()
