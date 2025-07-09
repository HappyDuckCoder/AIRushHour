import pygame
import os

class Font:
    def __init__(self, size, path="assets/fonts/vinizinho.ttf"):
        if os.path.exists(path):
            self.font = pygame.font.Font(path, size)
        else:
            print(f"[Warning] Không tìm thấy font '{path}', dùng font mặc định.")
            self.font = pygame.font.SysFont("arial", size)

    def render(self, text, color=(255, 255, 255)):
        return self.font.render(text, True, color)

class Text:
    def __init__(self, text, color, pos, font=None, center=True):
        self.text = text
        self.font = font 
        self.color = color
        self.pos = pos
        self.center = center
        self.image = self.font.render(self.text, self.color)
        
        if self.center:
            self.rect = self.image.get_rect(center=self.pos)
        else:
            self.rect = self.image.get_rect(topleft=self.pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_text(self, new_text):
        self.text = new_text
        self.image = self.font.render(self.text, self.color)
        
        if self.center:
            # Giữ nguyên vị trí center khi thay đổi text
            center_pos = self.rect.center
            self.rect = self.image.get_rect(center=center_pos)
        else:
            # Giữ nguyên vị trí topleft khi thay đổi text
            topleft_pos = self.rect.topleft
            self.rect = self.image.get_rect(topleft=topleft_pos)
    
    def set_position(self, new_pos):
        """Cập nhật vị trí của text"""
        self.pos = new_pos
        if self.center:
            self.rect.center = new_pos
        else:
            self.rect.topleft = new_pos