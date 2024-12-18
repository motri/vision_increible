import cv2
import numpy as np

# Callback function for mouse events
def draw_rectangle(event, x, y, flags, param):
    global drawing, x_start, y_start, x_end, y_end, rectangle_drawn, stored_hsv_values

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_start, y_start = x, y
        rectangle_drawn = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            x_end, y_end = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_end, y_end = x, y
        rectangle_drawn = True

        # Calculate HSV values once the rectangle is finalized
        if rectangle_drawn:
            roi = frame[min(y_start, y_end):max(y_start, y_end), min(x_start, x_end):max(x_start, x_end)]
            if roi.size > 0:  # Avoid empty ROI
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                avg_hsv = np.mean(hsv_roi, axis=(0, 1))
                h, s, v = avg_hsv

                # Store the HSV values
                stored_hsv_values.append((int(h), int(s), int(v)))
                print(f"Stored HSV: {stored_hsv_values[-1]}")

# Initialize variables
drawing = False
x_start, y_start, x_end, y_end = -1, -1, -1, -1
rectangle_drawn = False
stored_hsv_values = []  # List to store HSV values

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Create a named window and set the mouse callback
cv2.namedWindow('Frame')
cv2.setMouseCallback('Frame', draw_rectangle)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for better visibility
    frame = cv2.resize(frame, (640, 480))

    # If a rectangle is being drawn or finalized, show it on the frame
    if drawing or rectangle_drawn:
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

    # Display stored HSV values on the frame
    for i, (h, s, v) in enumerate(stored_hsv_values):
        cv2.putText(frame, f"HSV {i+1}: ({h}, {s}, {v})", (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Display the frame
    cv2.imshow('Frame', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close windows
cap.release()
cv2.destroyAllWindows()

# Print all stored HSV values
print("All Stored HSV Values:")
for idx, hsv in enumerate(stored_hsv_values):
    print(f"HSV {idx + 1}: {hsv}")
