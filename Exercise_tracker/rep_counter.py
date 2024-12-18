import pygame

class RepCounter:
    def __init__(self, audio_feedback):
        self.audio_feedback = audio_feedback
        self.rep_count = 0
        self.at_bottom = False
        pygame.mixer.init()
        self.ping_sound = "assets/ping.mp3"

    def count_reps(self, exercise, joints):
        if exercise == "Squat" and "shoulder" in joints and "hip" in joints:
            shoulder_y, hip_y = joints["shoulder"][1], joints["hip"][1]

            # Bottom position detected (shoulder almost at same y as hip)
            if abs(shoulder_y - hip_y) < 20 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (shoulder back above hip)
            elif shoulder_y < hip_y - 20 and self.at_bottom:
                self.rep_count += 1
                pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                self.at_bottom = False

        elif exercise == "Deadlift" and "shoulder" in joints and "hip" in joints:
            shoulder_y, hip_y = joints["shoulder"][1], joints["hip"][1]

            # Bottom position detected (shoulder almost at same y as hip)
            if abs(shoulder_y - hip_y) < 20 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (shoulder back above hip)
            elif shoulder_y < hip_y - 20 and self.at_bottom:
                self.rep_count += 1
                pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                self.at_bottom = False

        elif exercise == "Push-up" and "elbow" in joints and "shoulder" in joints:
            elbow_y, shoulder_y = joints["elbow"][1], joints["shoulder"][1]

            # Bottom position detected (elbow and shoulder similarly in y)
            if abs(elbow_y - shoulder_y) < 20 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (elbow and shoulder aligned)
            elif abs(elbow_y - shoulder_y) < 30 and self.at_bottom:
                self.rep_count += 1
                pygame.mixer.Sound(self.ping_sound).play()  # Play sound for completed rep
                self.at_bottom = False

        return self.rep_count