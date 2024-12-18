from utils import calculate_angle

class RepCounter:
    def __init__(self, audio_feedback):
        self.audio_feedback = audio_feedback
        self.rep_count = 0
        self.at_bottom = False

    def count_reps(self, exercise, joints):
        if exercise == "Squat" and "knee" in joints and "hip" in joints and "shoulder" in joints:
            angle = calculate_angle(joints["knee"], joints["hip"], joints["shoulder"])

            # Bottom position detected (angle less than 90 degrees)
            if angle < 90 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (angle greater than 160 degrees)
            elif angle > 160 and self.at_bottom:
                self.rep_count += 1
                self.audio_feedback.play_ping()
                self.at_bottom = False

        elif exercise == "Deadlift" and "knee" in joints and "hip" in joints and "shoulder" in joints:
            angle = calculate_angle(joints["knee"], joints["hip"], joints["shoulder"])

            # Bottom position detected (angle less than 90 degrees)
            if angle < 90 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (angle greater than 160 degrees)
            elif angle > 160 and self.at_bottom:
                self.rep_count += 1
                self.audio_feedback.play_ping()
                self.at_bottom = False

        elif exercise == "Push-up" and "elbow" in joints and "shoulder" in joints and "hip" in joints:
            angle = calculate_angle(joints["elbow"], joints["shoulder"], joints["hip"])

            # Bottom position detected (angle less than 90 degrees)
            if angle < 90 and not self.at_bottom:
                self.at_bottom = True

            # Top position detected (angle greater than 160 degrees)
            elif angle > 160 and self.at_bottom:
                self.rep_count += 1
                self.audio_feedback.play_ping()
                self.at_bottom = False

        return self.rep_count