import pygame
import time
from UI.Text import Text, Font
from constants import *

class RippleEffect:
    def __init__(self, x, y, max_radius=60):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = max_radius
        self.alpha = 255
        self.active = True
        self.speed = 4
        
    def update(self):
        if self.active:
            self.radius += self.speed
            self.alpha = max(0, 255 - (self.radius / self.max_radius) * 255)
            
            if self.radius >= self.max_radius:
                self.active = False
                
    def draw(self, surf):
        if self.active and self.alpha > 0:
            ripple_surf = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            color = (255, 255, 255, int(self.alpha * 0.6))
            pygame.draw.circle(ripple_surf, color, (self.max_radius, self.max_radius), int(self.radius))
            surf.blit(ripple_surf, (self.x - self.max_radius, self.y - self.max_radius))

class ButtonState:
    def apply_style(self, button, surf):
        raise NotImplementedError()

class DefaultState(ButtonState):
    def apply_style(self, button, surf):
        # Tính toán vị trí với offset
        current_rect = button.rect.copy()
        current_rect.y += int(button.current_offset_y)
        
        # Vẽ shadow cho hiệu ứng nổi
        shadow_rect = current_rect.copy()
        shadow_rect.move_ip(4, 4)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=12)
        surf.blit(shadow_surf, shadow_rect)
        
        # Vẽ nút với gradient
        current_color = button.get_current_color()
        gradient_end = tuple(max(c - 20, 0) for c in current_color)
        gradient_surf = button.create_gradient_surface(current_color, gradient_end, current_rect.width, current_rect.height)
        
        button_surf = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, current_color, button_surf.get_rect(), border_radius=12)
        button_surf.blit(gradient_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        surf.blit(button_surf, current_rect)
        
        # Highlight cho hiệu ứng nổi
        highlight_rect = pygame.Rect(current_rect.x, current_rect.y, current_rect.width, current_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 60), highlight_surf.get_rect(), border_radius=12)
        surf.blit(highlight_surf, highlight_rect)
        
        button.draw_text(surf, current_rect)

class HoverState(ButtonState):
    def apply_style(self, button, surf):
        # Tính toán vị trí với offset
        current_rect = button.rect.copy()
        current_rect.y += int(button.current_offset_y)
        
        # Shadow lớn hơn khi hover
        shadow_rect = current_rect.copy()
        shadow_rect.move_ip(6, 6)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect(), border_radius=12)
        surf.blit(shadow_surf, shadow_rect)
        
        # Vẽ nút với gradient
        current_color = button.get_current_color()
        gradient_end = tuple(max(c - 20, 0) for c in current_color)
        gradient_surf = button.create_gradient_surface(current_color, gradient_end, current_rect.width, current_rect.height)
        
        button_surf = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, current_color, button_surf.get_rect(), border_radius=12)
        button_surf.blit(gradient_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        surf.blit(button_surf, current_rect)
        
        # Highlight khi hover
        highlight_rect = pygame.Rect(current_rect.x, current_rect.y, current_rect.width, current_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 80), highlight_surf.get_rect(), border_radius=12)
        surf.blit(highlight_surf, highlight_rect)
        
        button.draw_text(surf, current_rect)

class ClickedState(ButtonState):
    def apply_style(self, button, surf):
        # Tính toán vị trí với offset
        current_rect = button.rect.copy()
        current_rect.y += int(button.current_offset_y)
        
        # Shadow nhỏ hơn khi click (hiệu ứng ấn xuống)
        shadow_rect = current_rect.copy()
        shadow_rect.move_ip(2, 2)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=12)
        surf.blit(shadow_surf, shadow_rect)
        
        # Màu tối hơn khi click với animation
        current_color = button.get_current_click_color()
        gradient_end = tuple(max(c - 20, 0) for c in current_color)
        gradient_surf = button.create_gradient_surface(current_color, gradient_end, current_rect.width, current_rect.height)
        
        button_surf = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, current_color, button_surf.get_rect(), border_radius=12)
        button_surf.blit(gradient_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        surf.blit(button_surf, current_rect)
        
        # Highlight nhẹ hơn khi click
        highlight_rect = pygame.Rect(current_rect.x, current_rect.y, current_rect.width, current_rect.height // 4)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 30), highlight_surf.get_rect(), border_radius=12)
        surf.blit(highlight_surf, highlight_rect)
        
        button.draw_text(surf, current_rect)

class Button:
    def __init__(self, text, pos, width=140, height=50, color=(0, 160, 80)):
        self.text = text
        self.original_text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.base_color = color
        # self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        self.font = Font(24)

        # State pattern
        self.default_state = DefaultState()
        self.hover_state = HoverState()
        self.clicked_state = ClickedState()
        self.current_state = self.default_state

        # Animation properties
        self.is_clicked = False
        self.click_start_time = 0
        self.click_duration = 0.2  # 0.2 giây
        self.click_base_color = tuple(max(c - 60, 0) for c in self.base_color)
        
        # Web-style animation properties
        self.current_offset_y = 0
        self.target_offset_y = 0
        self.is_hovered = False
        self.text_change_time = 0
        self.text_change_duration = 0.3
        
        # Colors
        self.hover_color = tuple(min(c + 30, 255) for c in self.base_color)
        
        # Ripple effects
        self.ripples = []
        
    def create_gradient_surface(self, color1, color2, width, height):
        """Tạo surface với gradient"""
        surf = pygame.Surface((width, height))
        for y in range(height):
            progress = y / height
            r = int(color1[0] + (color2[0] - color1[0]) * progress)
            g = int(color1[1] + (color2[1] - color1[1]) * progress)
            b = int(color1[2] + (color2[2] - color1[2]) * progress)
            pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
        return surf
        
    def get_current_color(self):
        """Tính toán màu hiện tại dựa trên trạng thái"""
        if self.is_clicked:
            return self.get_current_click_color()
        elif self.is_hovered:
            return self.hover_color
        else:
            return self.base_color
        
    def get_current_click_color(self):
        """Tính toán màu hiện tại dựa trên thời gian animation"""
        if not self.is_clicked:
            return self.base_color
            
        current_time = time.time()
        elapsed = current_time - self.click_start_time
        
        if elapsed >= self.click_duration:
            # Animation hoàn thành
            return self.click_base_color
        
        # Interpolation tuyến tính từ màu gốc đến màu tối
        progress = elapsed / self.click_duration
        current_color = tuple(
            int(self.base_color[i] + (self.click_base_color[i] - self.base_color[i]) * progress)
            for i in range(3)
        )
        return current_color

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        if self.rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_clicked = True
                self.click_start_time = time.time()
                self.text_change_time = time.time()
                self.text = "Đã nhấn!"
                self.current_state = self.clicked_state
                self.target_offset_y = 2
                
                # Tạo ripple effect
                local_x = mouse_pos[0] - self.rect.x
                local_y = mouse_pos[1] - self.rect.y
                self.ripples.append(RippleEffect(self.rect.x + local_x, self.rect.y + local_y))
                
                clicked = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.target_offset_y = 0
                # Kiểm tra nếu animation chưa hoàn thành
                if time.time() - self.click_start_time < self.click_duration:
                    # Giữ trạng thái clicked cho đến khi animation hoàn thành
                    pass
                else:
                    self.is_clicked = False
                    self.current_state = self.hover_state
            else:
                if not self.is_clicked:
                    self.is_hovered = True
                    self.current_state = self.hover_state
                    self.target_offset_y = -2
        else:
            if not self.is_clicked:
                self.is_hovered = False
                self.current_state = self.default_state
                self.target_offset_y = 0
                
        return clicked

    def update(self):
        try:
            current_time = time.time()
            
            if self.is_clicked:
                if current_time - self.click_start_time >= self.click_duration:
                    self.is_clicked = False
                    mouse_pos = pygame.mouse.get_pos()
                    if self.rect.collidepoint(mouse_pos):
                        self.is_hovered = True
                        self.current_state = self.hover_state
                        self.target_offset_y = -2
                    else:
                        self.is_hovered = False
                        self.current_state = self.default_state
                        self.target_offset_y = 0
                        
            # Update text change
            if self.text != self.original_text and current_time - self.text_change_time >= self.text_change_duration:
                self.text = self.original_text
                
            # Smooth animation cho offset
            self.current_offset_y += (self.target_offset_y - self.current_offset_y) * 0.3
            
            # Update ripples
            self.ripples = [r for r in self.ripples if r.active]
            for ripple in self.ripples:
                ripple.update()
                
        except Exception as e:
            print(f"[ERROR] update() failed on button '{self.text}': {e}")

    def draw_text(self, surf, rect=None):
        if rect is None:
            rect = self.rect

        text_surface = self.font.render(self.text, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        
        surf.blit(text_surface, text_rect)

    def draw(self, surf):
        # Vẽ ripple effects trước
        for ripple in self.ripples:
            ripple.draw(surf)
            
        # Vẽ nút
        self.current_state.apply_style(self, surf)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)