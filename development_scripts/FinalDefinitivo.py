import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from PIL import Image, ImageTk
import pygame  # For audio feedback


class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Tracking App")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.cap = None
        self.running = False
        self.canvas = None
        self.frame_buffer = None
        self.selected_exercise = None
        self.rep_count = 0
        self.at_bottom = False  # To track rep transitions
        self.start_tracking = False

        # Initialize pygame mixer for audio
        pygame.mixer.init()
        self.ping_sound = "development_scripts/msg/ping.mp3"

        self.color_ranges = {
            'ankle': ([24, 145, 70], [36, 255, 255]),        # Yellow
            'knee': ([90, 51, 70], [128, 255, 255]),         # Blue
            'hip': ([0, 163, 4], [0, 255, 255]),             # Red
            'shoulder': ([42, 47, 159], [50, 155, 200]),     # Green
            'elbow': ([90, 51, 70], [128, 255, 255]),        # Blue
            'wrist': ([112, 54, 114], [129, 177, 255])       # Purple
        }
        self.main_menu()

    def main_menu(self):
        """Create the main menu for exercise selection."""
        self.clear_window()
        label = tk.Label(self.root, text="Select an Exercise", font=("Helvetica", 16))
        label.pack(pady=10)

        for exercise in ["Squat", "Deadlift", "Push-up"]:
            tk.Button(self.root, text=exercise, command=lambda e=exercise: self.start_exercise(e), width=20).pack(pady=10)

    def start_exercise(self, exercise):
        """Initialize exercise tracking."""
        self.selected_exercise = exercise
        self.rep_count = 0
        self.at_bottom = False
        self.start_tracking = False
        self.clear_window()

        tk.Button(self.root, text="Start Tracking", command=self.start_reps, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="Stop", command=self.stop_exercise, bg="red", fg="white").pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=640, height=480, bg="black")
        self.canvas.pack(pady=10)

        self.running = True
        Thread(target=self.video_feed, daemon=True).start()

    def start_reps(self):
        """Start counting repetitions."""
        self.start_tracking = True
        messagebox.showinfo("Info", "Repetition tracking started!")

    def stop_exercise(self):
        """Stop video feed and return to menu."""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.main_menu()

    def video_feed(self):
        """Capture video and process frames."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Camera not initialized.")
            return

        while self.running:
            ret, self.frame_buffer = self.cap.read()
            if not ret:
                break

            processed_frame = self.process_frame(self.frame_buffer)
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

        self.cap.release()

    def process_frame(self, frame):
        """Process the frame to detect joints, count reps, and detect form."""
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect joints
        joints = self.detect_joints(hsv)

        # Draw stick figure based on selected exercise
        if self.selected_exercise == "Push-up":
            connections = [("ankle", "hip"), ("hip", "shoulder"), ("shoulder", "elbow")]
        else:
            connections = [("knee", "hip"), ("hip", "shoulder")]

        for j1, j2 in connections:
            if j1 in joints and j2 in joints:
                cv2.line(frame, joints[j1], joints[j2], (0, 255, 0), 3)
        for joint, pos in joints.items():
            cv2.circle(frame, pos, 6, (0, 0, 255), -1)

        # Repetition detection logic
        if self.start_tracking:
            if self.selected_exercise == "Squat" and "knee" in joints and "hip" in joints:
                knee_y, hip_y = joints["knee"][1], joints["hip"][1]

                # Bottom position detected (knee below hip)
                if knee_y > hip_y + 20 and not self.at_bottom:
                    self.at_bottom = True

                # Top position detected (knee back above hip)
                elif knee_y < hip_y - 20 and self.at_bottom:
                    self.rep_count += 1
                    pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                    self.at_bottom = False

            elif self.selected_exercise == "Deadlift" and "shoulder" in joints and "hip" in joints:
                shoulder_y, hip_y = joints["shoulder"][1], joints["hip"][1]

                # Bottom position detected (shoulder almost at same y as hip)
                if abs(shoulder_y - hip_y) < 20 and not self.at_bottom:
                    self.at_bottom = True

                # Top position detected (shoulder back above hip)
                elif shoulder_y < hip_y - 20 and self.at_bottom:
                    self.rep_count += 1
                    pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                    self.at_bottom = False

            elif self.selected_exercise == "Push-up" and "elbow" in joints and "shoulder" in joints:
                elbow_y, shoulder_y = joints["elbow"][1], joints["shoulder"][1]

                # Bottom position detected (elbow and shoulder similarly in y)
                if abs(elbow_y - shoulder_y) < 20 and not self.at_bottom:
                    self.at_bottom = True

                # Top position detected (elbow and shoulder aligned)
                elif abs(elbow_y - shoulder_y) < 30 and self.at_bottom:
                    self.rep_count += 1
                    pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                    self.at_bottom = False

        # Display rep count
        cv2.putText(frame, f"Reps: {self.rep_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

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

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
