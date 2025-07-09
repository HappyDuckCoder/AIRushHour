import pygame
from Resource.Resource import ResourceManager

class Mouse:
    def __init__(self):
        self.image = ResourceManager().get_image("mouse")
        if self.image is None:
            raise FileNotFoundError("Mouse image 'mouse' not found in ResourceManager.")

    def draw(self, screen):
        pos = pygame.mouse.get_pos()
        screen.blit(self.image, pos)
