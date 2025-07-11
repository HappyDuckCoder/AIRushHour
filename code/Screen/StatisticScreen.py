from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Audio.AudioManager import AudioManager
from Resource.Resource import ResourceManager
from constants import *
import pygame

# ===============================
# Statistic Screen with Slider
# ===============================
class StatisticScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        # Slider properties
        self.current_map = 0  # Index của map hiện tại (0-9)
        self.total_maps = 10
        self.transition_speed = 0.1
        self.auto_slide_timer = 0
        self.auto_slide_delay = 3000  # 3 giây
        self.is_auto_sliding = False
        
        # UI Elements
        self.map_title = Text("Map 1 Statistics", WHITE, (SCREEN_W//2, 100), font=Font(32))
        self.back_button = Button("BACK", (30, SCREEN_H - 80), 120, 50, BLUE)
        
        # Navigation buttons
        self.prev_button = Button("◀", (100, SCREEN_H//2), 60, 60, GRAY)
        self.next_button = Button("▶", (SCREEN_W - 160, SCREEN_H//2), 60, 60, GRAY)
        
        # Toggle auto-slide button
        self.auto_button = Button("AUTO: OFF", (SCREEN_W//2 - 80, SCREEN_H - 80), 160, 50, GREEN)
        
        # Slide indicators (dots)
        self.indicator_radius = 8
        self.indicator_spacing = 25
        self.indicator_y = SCREEN_H - 150
        
        # Load statistic images for all maps
        self.map_statistics = []
        for i in range(1, 11):  # Map 1 to Map 10
            try:
                img = ResourceManager().get_image(f'map_{i}_statistic')
                self.map_statistics.append(img)
            except:
                # If image doesn't exist, create a placeholder
                placeholder = pygame.Surface((600, 400))
                placeholder.fill(GRAY)
                placeholder_text = Font(24).render(f"Map {i} Statistics", True, WHITE)
                placeholder.blit(placeholder_text, (300 - placeholder_text.get_width()//2, 200))
                self.map_statistics.append(placeholder)
        
        # Animation properties
        self.slide_offset = 0
        self.is_sliding = False
        self.slide_direction = 0  # -1 for left, 1 for right

    def draw(self, surface):
        self.draw_background(surface)
        
        # Draw current map statistic
        current_img = self.map_statistics[self.current_map]
        img_rect = current_img.get_rect()
        img_rect.center = (SCREEN_W//2 + self.slide_offset, SCREEN_H//2)
        surface.blit(current_img, img_rect)
        
        # Draw next/previous image during transition
        if self.is_sliding:
            if self.slide_direction == 1:  # Sliding to next
                next_index = (self.current_map + 1) % self.total_maps
                next_img = self.map_statistics[next_index]
                next_rect = next_img.get_rect()
                next_rect.center = (SCREEN_W//2 + self.slide_offset - SCREEN_W, SCREEN_H//2)
                surface.blit(next_img, next_rect)
            else:  # Sliding to previous
                prev_index = (self.current_map - 1) % self.total_maps
                prev_img = self.map_statistics[prev_index]
                prev_rect = prev_img.get_rect()
                prev_rect.center = (SCREEN_W//2 + self.slide_offset + SCREEN_W, SCREEN_H//2)
                surface.blit(prev_img, prev_rect)
        
        # Update map title
        self.map_title.text = f"Map {self.current_map + 1} Statistics"
        self.map_title.draw(surface)
        
        # Draw navigation buttons
        self.prev_button.draw(surface)
        self.next_button.draw(surface)
        
        # Draw slide indicators
        self.draw_indicators(surface)
        
        # Draw control buttons
        self.back_button.draw(surface)
        self.auto_button.draw(surface)
        
        # Draw map info
        map_info = Text(f"{self.current_map + 1} / {self.total_maps}", WHITE, 
                       (SCREEN_W//2, self.indicator_y + 40), font=Font(20))
        map_info.draw(surface)

    def draw_indicators(self, surface):
        # Calculate starting position for centered indicators
        total_width = (self.total_maps - 1) * self.indicator_spacing
        start_x = SCREEN_W//2 - total_width//2
        
        for i in range(self.total_maps):
            x = start_x + i * self.indicator_spacing
            y = self.indicator_y
            
            # Draw indicator circle
            if i == self.current_map:
                pygame.draw.circle(surface, WHITE, (x, y), self.indicator_radius)
            else:
                pygame.draw.circle(surface, GRAY, (x, y), self.indicator_radius)
                pygame.draw.circle(surface, WHITE, (x, y), self.indicator_radius, 2)

    def update(self):
        # Handle slide animation
        if self.is_sliding:
            if self.slide_direction == 1:  # Sliding right
                self.slide_offset -= SCREEN_W * self.transition_speed
                if self.slide_offset <= -SCREEN_W:
                    self.slide_offset = 0
                    self.is_sliding = False
                    self.current_map = (self.current_map + 1) % self.total_maps
            else:  # Sliding left
                self.slide_offset += SCREEN_W * self.transition_speed
                if self.slide_offset >= SCREEN_W:
                    self.slide_offset = 0
                    self.is_sliding = False
                    self.current_map = (self.current_map - 1) % self.total_maps
        
        # Handle auto-slide
        if self.is_auto_sliding and not self.is_sliding:
            self.auto_slide_timer += 16  # Assuming 60 FPS
            if self.auto_slide_timer >= self.auto_slide_delay:
                self.next_slide()
                self.auto_slide_timer = 0
        
        return True

    def next_slide(self):
        if not self.is_sliding:
            self.is_sliding = True
            self.slide_direction = 1
            self.slide_offset = 0

    def prev_slide(self):
        if not self.is_sliding:
            self.is_sliding = True
            self.slide_direction = -1
            self.slide_offset = 0

    def go_to_slide(self, index):
        if not self.is_sliding and index != self.current_map:
            self.current_map = index
            self.slide_offset = 0

    def toggle_auto_slide(self):
        self.is_auto_sliding = not self.is_auto_sliding
        self.auto_slide_timer = 0
        self.auto_button.text = "AUTO: ON" if self.is_auto_sliding else "AUTO: OFF"
        self.auto_button.color = RED if self.is_auto_sliding else GREEN

    def go_back(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.screen_manager.set_screen("menu")

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Back button
            if self.back_button.hit(event.pos):
                self.go_back()
            
            # Navigation buttons
            elif self.prev_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.prev_slide()
            
            elif self.next_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.next_slide()
            
            # Auto-slide toggle
            elif self.auto_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.toggle_auto_slide()
            
            # Indicator clicks
            else:
                self.handle_indicator_click(event.pos)
        
        # Keyboard controls
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.prev_slide()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.next_slide()
            elif event.key == pygame.K_SPACE:
                self.toggle_auto_slide()

    def handle_indicator_click(self, pos):
        # Check if click is on any indicator
        total_width = (self.total_maps - 1) * self.indicator_spacing
        start_x = SCREEN_W//2 - total_width//2
        
        for i in range(self.total_maps):
            x = start_x + i * self.indicator_spacing
            y = self.indicator_y
            
            # Check if click is within indicator circle
            distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
            if distance <= self.indicator_radius + 5:  # Add some padding
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.go_to_slide(i)
                break

    def on_exit(self):
        pass