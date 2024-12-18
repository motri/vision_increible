import cv2
import numpy as np
from threading import Thread
from PIL import Image, ImageTk
import tkinter as tk
from joint_detection import JointDetector
from audio_feedback import AudioFeedback
from rep_counter_relative import RepCounterRelative
from posture_checker import PostureChecker

class VideoProcessor:
    def __init__(self):
        self.cap = None
        self.running = False
        self.frame_buffer = None
        self.joint_detector = JointDetector()
        self.audio_feedback = AudioFeedback()
        self.rep_counter = RepCounterRelative(self.audio_feedback)
        self.posture_checker = PostureChecker(self.audio_feedback)
        self.selected_exercise = None
        self.start_tracking = False

    def start_video_feed(self, canvas, selected_exercise, update_rep_count_callback):
        self.canvas = canvas
        self.selected_exercise = selected_exercise
        self.update_rep_count_callback = update_rep_count_callback
        self.running = True
        Thread(target=self.video_feed, daemon=True).start()

    def stop_video_feed(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def video_feed(self):
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

            # Schedule the update of the canvas in the main thread
            self.canvas.after(0, self.update_canvas, img)

        self.cap.release()

    def update_canvas(self, img):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def process_frame(self, frame):
        """Process the frame to detect joints, count reps, and detect form."""
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect joints
        joints = self.joint_detector.detect_joints(hsv)

        # Draw stick figure based on selected exercise
        if self.selected_exercise == "Push-up":
            connections = [("ankle", "hip"), ("hip", "shoulder"), ("shoulder", "elbow")]
        else:
            connections = [("knee", "hip"), ("hip", "shoulder"),("ankle", "knee") ]

        for j1, j2 in connections:
            if j1 in joints and j2 in joints:
                cv2.line(frame, joints[j1], joints[j2], (0, 255, 0), 3)
        for joint, pos in joints.items():
            cv2.circle(frame, pos, 6, (0, 0, 255), -1)

        # Initialize rep_count
        rep_count = 0

        # Repetition detection logic using angles
        if self.start_tracking:
            rep_count = self.rep_counter.count_reps(self.selected_exercise, joints)
            #self.posture_checker.check_posture(self.selected_exercise, joints)

        # Display rep count
        cv2.putText(frame, f"Reps: {rep_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.update_rep_count_callback(rep_count)
        return frame