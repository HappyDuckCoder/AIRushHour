from constants import *
import pygame

# ===============================
# Button Class
# ===============================
class Button:
    def __init__(self, text, pos, width=120, height=40, color=GREEN):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.SysFont(None, 24)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 2)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)