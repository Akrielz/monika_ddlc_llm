from typing import Tuple

import pygame
from pygame import Surface


Coordinates = Tuple[int, int]
ScreenSize = Tuple[int, int]


class Sprite:
    image: Surface
    x: int
    y: int

    def __init__(self, image: Surface, pos: Coordinates = (0, 0)):
        self.image = image
        self.x, self.y = pos

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def center_x(self):
        return self.x + self.image.get_width() / 2

    def center_y(self):
        return self.y + self.image.get_height() / 2

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_to(self, x, y):
        self.x = x
        self.y = y
