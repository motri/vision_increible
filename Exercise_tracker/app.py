import tkinter as tk
from tkinter import messagebox
from threading import Thread
from video_processing import VideoProcessor
from audio_feedback import AudioFeedback

class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Tracking App")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.video_processor = VideoProcessor()
        self.audio_feedback = AudioFeedback()

        self.selected_exercise = None
        self.rep_count = 0
        self.at_bottom = False
        self.start_tracking = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
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

        self.video_processor.start_video_feed(self.canvas, self.selected_exercise, self.update_rep_count)

    def start_reps(self):
        """Start counting repetitions."""
        self.start_tracking = True
        messagebox.showinfo("Info", "Repetition tracking started!")

    def stop_exercise(self):
        """Stop video feed and return to menu."""
        self.video_processor.stop_video_feed()
        self.main_menu()

    def update_rep_count(self, rep_count):
        self.rep_count = rep_count

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_closing(self):
        """Handle the window close event."""
        self.video_processor.stop_video_feed()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()