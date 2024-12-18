import pygame

class AudioFeedback:
    def __init__(self):
        pygame.mixer.init()
        self.ping_sound = "assets/ping.mp3"
        self.back_straight_sound = "assets/mantenga_espalda.mp3"

    def play_ping(self):
        pygame.mixer.Sound(self.ping_sound).play()

    def play_back_straight(self):
        pygame.mixer.Sound(self.back_straight_sound).play()