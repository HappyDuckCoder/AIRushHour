# button_states.py
import pygame
import math
import time
from constants import *

class ButtonState:
    def apply_style(self, button, surf):
        raise NotImplementedError()

class DefaultState(ButtonState):
    def apply_style(self, button, surf):
        # Gradient background
        self.draw_gradient_rect(surf, button.base_color, button.rect)
        
        # Border glow effect
        glow_color = tuple(min(c + 60, 255) for c in button.base_color)
        pygame.draw.rect(surf, glow_color, button.rect, width=2, border_radius=12)
        
        button.draw_text(surf)

    def draw_gradient_rect(self, surf, color, rect):
        # Create gradient effect
        for i in range(rect.height):
            alpha = 1 - (i / rect.height) * 0.3
            gradient_color = tuple(int(c * alpha) for c in color)
            pygame.draw.rect(surf, gradient_color, 
                           (rect.x, rect.y + i, rect.width, 1))

class HoverState(ButtonState):
    def apply_style(self, button, surf):
        # Animated pulsing glow
        pulse = math.sin(time.time() * 8) * 0.3 + 0.7
        
        # Expanded rect for glow effect
        glow_rect = button.rect.inflate(8, 8)
        
        # Multiple glow layers
        for i in range(3):
            glow_alpha = (3 - i) * 30 * pulse
            glow_color = (*button.base_color, int(glow_alpha))
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surf.set_alpha(int(glow_alpha))
            glow_surf.fill(button.base_color)
            surf.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Elevated button effect
        elevated_rect = button.rect.move(0, -2)
        
        # Enhanced gradient
        hover_color = tuple(min(c + 50, 255) for c in button.base_color)
        self.draw_enhanced_gradient(surf, hover_color, elevated_rect)
        
        # Animated border
        border_intensity = int(pulse * 255)
        border_color = (255, 255, 255, border_intensity)
        pygame.draw.rect(surf, border_color[:3], elevated_rect, width=3, border_radius=12)
        
        # Shine effect
        self.draw_shine_effect(surf, elevated_rect, pulse)
        
        button.draw_enhanced_text(surf, elevated_rect)

    def draw_enhanced_gradient(self, surf, color, rect):
        # More complex gradient with multiple colors
        for i in range(rect.height):
            ratio = i / rect.height
            if ratio < 0.5:
                # Top half - lighter
                alpha = 1 + ratio * 0.4
            else:
                # Bottom half - darker
                alpha = 1.4 - (ratio - 0.5) * 0.6
            
            gradient_color = tuple(min(int(c * alpha), 255) for c in color)
            pygame.draw.rect(surf, gradient_color, 
                           (rect.x, rect.y + i, rect.width, 1))

    def draw_shine_effect(self, surf, rect, pulse):
        # Animated diagonal shine
        shine_pos = int(pulse * rect.width)
        shine_points = [
            (rect.x + shine_pos - 20, rect.y),
            (rect.x + shine_pos, rect.y),
            (rect.x + shine_pos - 10, rect.y + rect.height),
            (rect.x + shine_pos - 30, rect.y + rect.height)
        ]
        
        shine_surf = pygame.Surface((40, rect.height))
        shine_surf.set_alpha(int(pulse * 60))
        shine_surf.fill((255, 255, 255))
        
        if 0 <= shine_pos <= rect.width:
            surf.blit(shine_surf, (rect.x + shine_pos - 20, rect.y))

class ClickedState(ButtonState):
    def apply_style(self, button, surf):
        # Pressed down effect
        pressed_rect = button.rect.move(2, 2)
        
        # Darker color
        click_color = tuple(max(c - 60, 0) for c in button.base_color)
        
        # Inset shadow effect
        shadow_rect = pressed_rect.inflate(-4, -4)
        pygame.draw.rect(surf, (0, 0, 0), shadow_rect, border_radius=10)
        
        # Main button
        pygame.draw.rect(surf, click_color, pressed_rect, border_radius=12)
        
        # Inner glow
        inner_glow = tuple(min(c + 30, 255) for c in click_color)
        pygame.draw.rect(surf, inner_glow, pressed_rect, width=2, border_radius=12)
        
        button.draw_text(surf, pressed_rect)

class Button:
    def __init__(self, text, pos, width=140, height=50, color=(0, 160, 80)):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.base_color = color
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        # State pattern
        self.default_state = DefaultState()
        self.hover_state = HoverState()
        self.clicked_state = ClickedState()
        self.current_state = self.default_state

        self.is_clicked = False
        self.hover_start_time = 0
        self.was_hovering = False

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos)

        # Track hover timing for animations
        if is_hovering and not self.was_hovering:
            self.hover_start_time = time.time()
        self.was_hovering = is_hovering

        if is_hovering:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_clicked = True
                self.current_state = self.clicked_state
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_clicked = False
                self.current_state = self.hover_state
            else:
                self.current_state = self.hover_state
        else:
            self.current_state = self.default_state

    def draw_text(self, surf, rect=None):
        if rect is None:
            rect = self.rect
            
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        surf.blit(text_surface, text_rect)

    def draw_enhanced_text(self, surf, rect):
        # Text with subtle shadow and glow
        shadow_surface = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(rect.centerx + 1, rect.centery + 1))
        surf.blit(shadow_surface, shadow_rect)
        
        # Main text with slight glow
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        surf.blit(text_surface, text_rect)

    def draw(self, surf):
        # Enhanced shadow with multiple layers
        for i in range(3):
            shadow_offset = (i + 1) * 2
            shadow_alpha = 100 - (i * 30)
            shadow_rect = self.rect.move(shadow_offset, shadow_offset)
            
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height))
            shadow_surf.set_alpha(shadow_alpha)
            shadow_surf.fill((0, 0, 0))
            surf.blit(shadow_surf, shadow_rect)

        # Apply current state
        self.current_state.apply_style(self, surf)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)

    def get_hover_animation_progress(self):
        """Get animation progress for hover effects (0-1)"""
        if self.current_state == self.hover_state:
            return min((time.time() - self.hover_start_time) / 0.3, 1.0)
        return 0.0

# Example usage with different button styles
class GlowButton(Button):
    def __init__(self, text, pos, width=140, height=50, color=(255, 80, 80)):
        super().__init__(text, pos, width, height, color)
        
    def draw(self, surf):
        # Particle-like glow effect
        if self.current_state == self.hover_state:
            for i in range(8):
                angle = (time.time() * 2 + i * 0.8) % (2 * math.pi)
                radius = 40 + math.sin(time.time() * 3) * 10
                x = self.rect.centerx + math.cos(angle) * radius
                y = self.rect.centery + math.sin(angle) * radius
                
                glow_surf = pygame.Surface((20, 20))
                glow_surf.set_alpha(100)
                glow_surf.fill(self.base_color)
                surf.blit(glow_surf, (x - 10, y - 10))
        
        super().draw(surf)

class RainbowButton(Button):
    def __init__(self, text, pos, width=140, height=50):
        # Start with a base color that will be overridden
        super().__init__(text, pos, width, height, (255, 0, 0))
        
    def update_rainbow_color(self):
        # HSV to RGB conversion for rainbow effect
        hue = (time.time() * 100) % 360
        saturation = 1.0
        value = 0.8
        
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue/360, saturation, value)
        self.base_color = (int(r*255), int(g*255), int(b*255))
        
    def draw(self, surf):
        self.update_rainbow_color()
        super().draw(surf)