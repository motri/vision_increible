import cv2
import numpy as np

def main():
    # HSV color ranges for validation
    lower_hsv = np.array([49, 158, 220])
    upper_hsv = np.array([49, 166, 189])

    # Start video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Resize frame for consistency
        frame = cv2.resize(frame, (640, 480))

        # Convert frame to grayscale and HSV
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Blur the frame to reduce noise
        blurred_frame = cv2.GaussianBlur(gray_frame, (9, 9), 2)

        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(blurred_frame, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                                   param1=50, param2=30, minRadius=10, maxRadius=100)

        if circles is not None:
            # Convert the circle parameters to integers
            circles = np.round(circles[0, :]).astype("int")

            for (x, y, r) in circles:
                # Validate the circle's color in HSV
                mask = np.zeros(hsv_frame.shape[:2], dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                mean_hsv = cv2.mean(hsv_frame, mask=mask)[:3]  # Extract HSV mean under the circle

                # Check if the mean HSV falls within the specified range
                if (lower_hsv[0] <= mean_hsv[0] <= upper_hsv[0] and
                    lower_hsv[1] <= mean_hsv[1] <= upper_hsv[1] and
                    lower_hsv[2] <= mean_hsv[2] <= upper_hsv[2]):

                    # Draw the circle
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    # Draw the center of the circle
                    cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
                    # Display the center coordinates
                    cv2.putText(frame, f"Center: ({x}, {y})", (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Show the frame with the detected and validated circles
        cv2.imshow('Detected Circles', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
