import pygame
from UI.Text import Text, Font
from constants import *

class Button:
    def __init__(self, text, pos, width=140, height=50, color=(0, 160, 80)):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], width, height)        
        self.text_obj = Text(text, WHITE, self.rect.center, font=Font(24))
        
        # Hover properties
        self.is_hovered = False
        self.hover_color = tuple(min(c + 30, 255) for c in self.color)
        
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def update(self):
        self.text_obj.rect.center = self.rect.center
        
    def get_current_color(self):
        return self.hover_color if self.is_hovered else self.color
        
    def draw(self, surface):
        current_color = self.get_current_color()
        
        # Draw shadow for depth
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Draw main button
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        # Draw highlight for 3D effect
        highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height // 3)
        highlight_color = tuple(min(c + 40, 255) for c in current_color)
        pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=8)
        
        # Draw text
        self.text_obj.draw(surface)
        
    def hit(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
        
    def set_text(self, new_text):
        self.text = new_text
        self.text_obj.set_text(new_text)

    def set_color(self, new_color):
        self.color = new_color
        self.hover_color = tuple(min(c + 30, 255) for c in self.color)