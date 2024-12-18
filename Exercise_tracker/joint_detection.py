import cv2
import numpy as np

class JointDetector:
    def __init__(self):
        self.color_ranges = {
            'ankle': ([24, 145, 70], [36, 255, 255]),        # Yellow
            'knee': ([90, 51, 70], [128, 255, 255]),         # Blue
            'hip': ([0, 163, 4], [0, 255, 255]),             # Red
            'shoulder': ([42, 47, 159], [50, 155, 200]),     # Green
            'elbow': ([90, 51, 70], [128, 255, 255]),        # Blue
            'wrist': ([112, 54, 114], [129, 177, 255])       # Purple
        }

    def detect_joints(self, hsv):
        """Detect joints based on HSV ranges."""
        joints = {}
        for joint, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"]:
                    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                    joints[joint] = (cx, cy)
        return joints