import cv2 as cv
import numpy as np
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

zelda_img = cv.imread('Zelda.png', cv.IMREAD_UNCHANGED)
heart_img = cv.imread('Heart.png', cv.IMREAD_UNCHANGED)

# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
result = cv.matchTemplate(zelda_img, heart_img, cv.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
print('Best match top left position: %s' % str(max_loc))
print('Best match confidence: %s' % max_val)
cv.imshow('result', result)
cv.waitKey(0)
threshold = 0.32
locations = np.where(result >= threshold)

locations = list(zip(*locations[::-1]))
print(locations)
print('found %d locations' % len(locations))

stone_img_w = heart_img.shape[1]
print(stone_img_w)
stone_img_h = heart_img.shape[0]
print(stone_img_h)

for loc in locations:
    top_left = loc
    bottom_right = (top_left[0] + stone_img_w, top_left[1] + stone_img_h)
    cv.rectangle(zelda_img, top_left, bottom_right, (0, 255, 0), 2)

cv.imshow('conan_img', zelda_img)
cv.waitKey(0)