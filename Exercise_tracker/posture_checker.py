import numpy as np

class PostureChecker:
    def __init__(self, audio_feedback):
        self.audio_feedback = audio_feedback

    def check_posture(self, exercise, joints):
        if exercise == "Squat" and "hip" in joints and "shoulder" in joints:
            shoulder_hip_distance = np.linalg.norm(np.array(joints["shoulder"]) - np.array(joints["hip"]))
            if shoulder_hip_distance > 100:  # Adjust the threshold as needed
                self.audio_feedback.play_back_straight()

        elif exercise == "Deadlift" and "hip" in joints and "shoulder" in joints:
            shoulder_hip_distance = np.linalg.norm(np.array(joints["shoulder"]) - np.array(joints["hip"]))
            if shoulder_hip_distance < 50:  # Adjust the threshold as needed
                self.audio_feedback.play_back_straight()