import cv2
import numpy as np

def nothing(x):
    pass

# Create a blank image
img = np.zeros((300, 512, 3), np.uint8)

# Create a window
cv2.namedWindow('Test Window')

# Add a trackbar
cv2.createTrackbar('Test', 'Test Window', 0, 100, nothing)

while True:
    cv2.imshow('Test Window', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
