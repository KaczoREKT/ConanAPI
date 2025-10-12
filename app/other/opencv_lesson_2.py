import cv2 as cv

zelda_img = cv.imread('Zelda.png', cv.IMREAD_UNCHANGED)
heart_img = cv.imread('Heart.png', cv.IMREAD_UNCHANGED)

orb = cv.ORB_create()
# Wykrywamy punkty charakterystyczne + deskryptory
kp1, des1 = orb.detectAndCompute(zelda_img, None)
kp2, des2 = orb.detectAndCompute(heart_img, None)
# Dopasowujemy deskryptory
bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)
# Wyrysowanie najlepszych dopasowań
cv.drawMatches(zelda_img, kp1, heart_img, kp2, matches[:10], None, flags=2)
cv.imshow('matches', result)
cv.waitKey(0)