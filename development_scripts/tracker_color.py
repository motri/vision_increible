import cv2
import numpy as np

def main():
    # HSV color range for red (adjust as needed)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # Start video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Resize frame for consistency
        #frame = cv2.resize(frame, (640, 480))

        # Convert frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the red color
        mask = cv2.inRange(hsv_frame, lower_red, upper_red)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Approximate the contour to check if it is square-like
            epsilon = 0.05 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 4:  # Quadrilateral check
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if 0.9 <= aspect_ratio <= 1.1:  # Close to square
                    # Draw the contour and calculate the center
                    M = cv2.moments(contour)
                    if M['m00'] > 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])

                        # Draw square and center on the frame
                        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                        cv2.putText(frame, f"Center: ({cx}, {cy})", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Show the frame with the drawn contours
        cv2.imshow('Detected Squares', frame)
        cv2.imshow('Mask', mask)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
