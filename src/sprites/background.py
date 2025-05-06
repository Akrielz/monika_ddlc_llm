import pygame

from src.sprites.sprite import Sprite, ScreenSize


class Background(Sprite):
    def __init__(self, image_path: str, screen_size: ScreenSize):
        self.screen_size = screen_size
        self.load_image(image_path)
        super().__init__(self.image)

    def load_image(self, image_path: str):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.smoothscale(self.image, self.screen_size)