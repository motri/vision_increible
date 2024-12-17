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


    def process_frame(self, frame):
        """Process the video frame for tracking"""
        frame = cv2.resize(frame, (640, 480))
        cv2.putText(frame, f"Exercise: {self.selected_exercise}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if self.start_repetitions:
            cv2.putText(frame, "Tracking...", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return frame

    def clear_window(self):
        """Clear all widgets in the current window"""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
