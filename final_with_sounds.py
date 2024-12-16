import cv2
import numpy as np
import time
import pygame
import os

# Initialize Pygame for audio feedback
pygame.mixer.init()
success_sound = pygame.mixer.Sound("./msg/ping.mp3")

# Avoid macOS GUI issues
os.environ['QT_MAC_WANTS_LAYER'] = '1'

# Global Variables
selected_exercise = None
repetition_count = 0
repetition_status = ""
start_repetitions = False

# Function to calculate angles
def calculate_angles(a, b, c):
    """Calculates the angle formed by three points a, b, c."""
    if None in (a, b, c):
        return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ab, cb = a - b, c - b
    cosine = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.degrees(angle)

# Function to log repetition data
def log_repetition(exercise_name):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("repetition_stats.txt", "a") as file:
        file.write(f"{timestamp} - {exercise_name}: Repetition completed successfully\n")

# Function to play audio feedback
def play_audio_feedback(audio_file=None, sound=None):
    """Plays an audio message or sound."""
    if audio_file:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Wait until playback finishes
            pass
    elif sound:
        sound.play()

# Function to detect stickers and process frames
def detect_and_process_frames():
    global selected_exercise, repetition_count, repetition_status, start_repetitions

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    color_ranges = {
        'WRIST': ([90, 51, 70], [128, 255, 255]),  # Blue
        'ELBOW': ([129, 50, 70], [158, 255, 255]),  # Purple
        'SHOULDER': ([42, 47, 159], [50, 155, 200]),  # Green
        'WAIST': ([0, 163, 4], [0, 255, 255]),  # Red
        'ANKLE': ([24, 145, 70], [36, 255, 255])  # Yellow
    }

    articulation_colors = {
        'WRIST': (255, 0, 0),    # Blue
        'ELBOW': (128, 0, 128),  # Purple
        'SHOULDER': (0, 255, 0),  # Green
        'WAIST': (0, 0, 255),    # Red
        'ANKLE': (0, 255, 255)  # Yellow
    }

    print("\nPress 'q' to exit the program.\n")
    print("Press 's' to start counting repetitions.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame.")
            break

        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        centers = {}

        # Detect body parts
        for body_part, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 300:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cx, cy = x + w // 2, y + h // 2
                    cv2.circle(frame, (cx, cy), 8, articulation_colors[body_part], -1)
                    centers[body_part] = (cx, cy)

        # Process angles and repetitions
        if start_repetitions:
            process_repetitions(centers, frame)

        # Display repetition count and status
        cv2.putText(frame, f"Repetitions: {repetition_count}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Status: {repetition_status}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Show the frame
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nExiting program...\n")
            break
        elif key == ord('s'):
            start_repetitions = True

    cap.release()
    cv2.destroyAllWindows()

# Function to process repetitions
def process_repetitions(centers, frame):
    global repetition_count, repetition_status

    if selected_exercise == "Push-up":
        check_pushup_thresholds(centers)
    elif selected_exercise == "Squat":
        check_squat_thresholds(centers)
    elif selected_exercise == "Deadlift":
        check_deadlift_thresholds(centers)

# Threshold logic for Push-ups
def check_pushup_thresholds(centers):
    global repetition_count, repetition_status

    upper_threshold = [170.0, 60.0, 170.0]
    lower_threshold = [40.0, 40.0, 170.0]

    if all(part in centers for part in ['WRIST', 'ELBOW', 'SHOULDER']):
        angles = [
            calculate_angles(centers['WRIST'], centers['ELBOW'], centers['SHOULDER']),
            calculate_angles(centers['SHOULDER'], centers['ELBOW'], centers['WRIST']),
        ]
        if angles[0] < lower_threshold[0] or angles[1] < lower_threshold[1]:
            repetition_status = "Incomplete Movement"
            play_audio_feedback(audio_file="./msg/push_up_failure.mp3")
        elif angles[0] > upper_threshold[0] and angles[1] > upper_threshold[1]:
            repetition_status = "Well Done!"
            repetition_count += 1
            log_repetition("Push-up")
            play_audio_feedback(sound=success_sound)

# Threshold logic for Squats
def check_squat_thresholds(centers):
    # Add Squat-specific logic here, following a similar pattern
    pass

# Threshold logic for Deadlifts
def check_deadlift_thresholds(centers):
    # Add Deadlift-specific logic here, following a similar pattern
    pass

# Function to choose exercise
def get_exercise_choice():
    global selected_exercise
    print("Choose your exercise:")
    print("1. Push-up")
    print("2. Deadlift")
    print("3. Squat")
    choice = input("Enter the number of the exercise: ")
    if choice == '1':
        selected_exercise = "Push-up"
    elif choice == '2':
        selected_exercise = "Deadlift"
    elif choice == '3':
        selected_exercise = "Squat"
    else:
        print("Invalid option. Defaulting to Push-up.")
        selected_exercise = "Push-up"

# Main function
if __name__ == "__main__":
    get_exercise_choice()
    detect_and_process_frames()
