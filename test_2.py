import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from PIL import Image, ImageTk  # For displaying frames in Tkinter Canvas


class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Tracking App")
        self.root.geometry("800x600")  # Fixed window size
        self.root.resizable(False, False)
        self.selected_exercise = None
        self.start_repetitions = False
        self.cap = None
        self.running = False
        self.canvas = None  # Canvas for video display
        self.reference_joints = None  # Store initial static joints
        self.mask = None  # Static stick-figure mask

        # GUI Components
        self.main_menu()

    def main_menu(self):
        """Initial menu for exercise selection"""
        self.clear_window()
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True)

        label = tk.Label(main_frame, text="Select an Exercise", font=("Helvetica", 16))
        label.pack(pady=10)

        pushup_btn = tk.Button(main_frame, text="Push-up", command=lambda: self.start_exercise("Push-up"), width=20)
        pushup_btn.pack(pady=10)

        squat_btn = tk.Button(main_frame, text="Squat", command=lambda: self.start_exercise("Squat"), width=20)
        squat_btn.pack(pady=10)

        deadlift_btn = tk.Button(main_frame, text="Deadlift", command=lambda: self.start_exercise("Deadlift"), width=20)
        deadlift_btn.pack(pady=10)

    def start_exercise(self, exercise):
        """Set the exercise and start video feed"""
        self.selected_exercise = exercise
        self.clear_window()

        # Main container with padding
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True)

        # Add buttons
        iniciar_btn = tk.Button(main_frame, text="Iniciar", command=self.start_tracking, bg="green", fg="white", width=15)
        iniciar_btn.pack(pady=10)

        finalizar_btn = tk.Button(main_frame, text="Finalizar", command=self.stop_exercise, bg="red", fg="white", width=15)
        finalizar_btn.pack(pady=10)

        # Add Canvas for video feed
        self.canvas = tk.Canvas(main_frame, width=640, height=480, bg="black")
        self.canvas.pack(pady=10)

        # Start video feed in a separate thread
        self.running = True
        self.video_thread = Thread(target=self.initialize_video_capture)
        self.video_thread.start()

    def initialize_video_capture(self):
        """Threaded video capture initialization"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Camera failed to initialize.")
            return
        self.show_frame()

    def start_tracking(self):
        """Set start flag for repetitions"""
        self.start_repetitions = True
        messagebox.showinfo("Tracking", f"Tracking started for {self.selected_exercise}!")

    def stop_exercise(self):
        """Stop video feed and return to main menu"""
        if self.cap and self.cap.isOpened():
            self.running = False
            time.sleep(0.5)  # Allow threads to stop cleanly
            self.cap.release()
            self.cap = None
            cv2.destroyAllWindows()
        self.main_menu()

    def show_frame(self):
        """Display camera feed on Tkinter Canvas"""
        try:
            while self.running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Cannot read from camera.")
                    break

                # Process the frame
                frame = self.process_frame(frame)

                # Convert frame to ImageTk format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                # Update Canvas
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk

            if self.cap:
                self.cap.release()
        except Exception as e:
            print(f"Error during video feed: {e}")
        finally:
            cv2.destroyAllWindows()

    def detect_dots(self, frame):
        """Detect joint positions based on HSV color ranges."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        joints = {}

        # Define HSV ranges for each joint
        color_ranges = {
            'MUÑECA/RODILLA': ([90, 51, 70], [128, 255, 255]),  # Blue
            'CODO': ([129, 50, 70], [158, 255, 255]),          # Purple
            'HOMBRO': ([42, 47, 159], [50, 155, 200]),         # Green
            'CINTURA': ([0, 163, 4], [0, 255, 255]),           # Red
            'TOBILLO': ([24, 145, 70], [36, 255, 255])         # Yellow
        }

        # Detect center of the largest contour for each joint
        for joint_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Smooth the mask
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.erode(mask, None, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    joints[joint_name] = (cx, cy)

        return joints

    def process_frame(self, frame):
        """Detect joints dynamically, draw the stick-figure overlay."""
        frame = cv2.resize(frame, (640, 480))

        # Detect joints using HSV ranges
        detected_joints = self.detect_dots(frame)

        # Define connections for stick figure
        connections = [
            ("TOBILLO", "MUÑECA/RODILLA"),
            ("MUÑECA/RODILLA", "CINTURA"),
            ("CINTURA", "HOMBRO"),
            ("HOMBRO", "CODO"),
            ("CODO", "MUÑECA/RODILLA")
        ]

        # Create an empty mask for stick figure
        mask = np.zeros_like(frame, dtype=np.uint8)

        # Draw lines connecting the joints
        for joint1, joint2 in connections:
            if joint1 in detected_joints and joint2 in detected_joints:
                cv2.line(mask, detected_joints[joint1], detected_joints[joint2], (0, 255, 0), 3)

        # Draw joint markers
        for joint, position in detected_joints.items():
            cv2.circle(mask, position, 6, (0, 0, 255), -1)

        # Overlay the stick figure mask onto the original frame
        frame_with_mask = cv2.addWeighted(frame, 0.8, mask, 0.5, 0)

        # Display tracking information
        cv2.putText(frame_with_mask, f"Exercise: {self.selected_exercise}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        if self.start_repetitions:
            cv2.putText(frame_with_mask, "Tracking...", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame_with_mask

    def clear_window(self):
        """Clear all widgets in the current window"""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
