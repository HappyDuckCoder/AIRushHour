from constants import *
import pygame
from Graphic.Graphic import *

# ===============================
# Button Class
# ===============================
class Button:
    def __init__(self, text, pos, width=120, height=40, color=GREEN, image=None):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.SysFont(None, 24)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def set_text(self, text):
        self.text = text

    def draw(self, surf):
        gfx.draw_button(surf, self)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)