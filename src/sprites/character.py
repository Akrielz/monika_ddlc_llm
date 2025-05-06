import os
import random

import pygame

from src.sprites.sprite import Sprite, ScreenSize


class Character(Sprite):
    def __init__(self, character_path: str, screen_size: ScreenSize, mood: str = "happy"):
        self.screen_size = screen_size
        self.character_path = character_path
        self.emotions = self.read_emotions()
        self.set_mood(mood)

        x = (screen_size[0] - self.image.get_width()) // 2
        super().__init__(self.image, (x, 0))

    def set_mood(self, mood):
        if mood not in self.emotions:
            mood = 'glitched'
            # raise ValueError(f"Invalid mood: {mood}")
        self.mood = mood
        self.select_emotion()

    def read_emotions(self):
        emotion_dirs = [f for f in os.listdir(self.character_path) if os.path.isdir(os.path.join(self.character_path, f))]
        emotions = {}
        for emotion_dir in emotion_dirs:
            emotion_path = os.path.join(self.character_path, emotion_dir)
            emotions[emotion_dir] = [os.path.join(emotion_path, f) for f in os.listdir(emotion_path)]

        return emotions

    def select_emotion(self):
        random_index = random.randint(0, len(self.emotions[self.mood]) - 1)
        self.load_image(self.emotions[self.mood][random_index])

    def load_image(self, image_path: str):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.smoothscale(self.image, (int(self.screen_size[1]), self.screen_size[1]))

    @property
    def available_emotions(self):
        return sorted(list(self.emotions.keys()))