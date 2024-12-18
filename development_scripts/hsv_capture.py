import cv2
import numpy as np

def nothing(x):
    pass

# Load an image or start a video stream
# Replace 'image.jpg' with 0 for webcam input
cap = cv2.VideoCapture(0)  # Use an image path if needed, e.g., cv2.imread('image.jpg')

# Create a window to display results
cv2.namedWindow('HSV Adjustments')

# Create trackbars for HSV ranges
cv2.createTrackbar('Lower Hue', 'HSV Adjustments', 0, 179, nothing)
cv2.createTrackbar('Lower Sat', 'HSV Adjustments', 0, 255, nothing)
cv2.createTrackbar('Lower Val', 'HSV Adjustments', 0, 255, nothing)
cv2.createTrackbar('Upper Hue', 'HSV Adjustments', 179, 179, nothing)
cv2.createTrackbar('Upper Sat', 'HSV Adjustments', 255, 255, nothing)
cv2.createTrackbar('Upper Val', 'HSV Adjustments', 255, 255, nothing)

while True:
    # Read frame (for video stream) or load an image
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame for better visibility
    #frame = cv2.resize(frame, (640, 480))

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get current positions of trackbars
    lower_hue = cv2.getTrackbarPos('Lower Hue', 'HSV Adjustments')
    lower_sat = cv2.getTrackbarPos('Lower Sat', 'HSV Adjustments')
    lower_val = cv2.getTrackbarPos('Lower Val', 'HSV Adjustments')
    upper_hue = cv2.getTrackbarPos('Upper Hue', 'HSV Adjustments')
    upper_sat = cv2.getTrackbarPos('Upper Sat', 'HSV Adjustments')
    upper_val = cv2.getTrackbarPos('Upper Val', 'HSV Adjustments')

    # Create HSV range boundaries
    lower_bound = np.array([lower_hue, lower_sat, lower_val])
    upper_bound = np.array([upper_hue, upper_sat, upper_val])

    # Create a binary mask for the specified range
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply the mask to the original frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Display the original frame, mask, and result
    cv2.imshow('HSV Adjustments', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Filtered Result', result)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close windows
cap.release()
cv2.destroyAllWindows()
