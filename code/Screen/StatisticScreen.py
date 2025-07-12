from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Audio.AudioManager import AudioManager
from Resource.Resource import ResourceManager
from constants import *
import pygame


class StatisticScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.current_map = 0  
        self.total_maps = 10
        self.transition_speed = 0.1
        self.auto_slide_timer = 0
        self.auto_slide_delay = 3000  
        self.is_auto_sliding = False
        
        self.map_title = Text("Map 1 Statistics", WHITE, (SCREEN_W//2, 100), font=Font(32))
        self.back_button = Button("BACK", (30, SCREEN_H - 80), 120, 50, BLUE)
        
        self.prev_button = Button("◀", (100, SCREEN_H//2), 60, 60, GRAY)
        self.next_button = Button("▶", (SCREEN_W - 160, SCREEN_H//2), 60, 60, GRAY)
        
        self.auto_button = Button("AUTO: OFF", (SCREEN_W//2 - 80, SCREEN_H - 80), 160, 50, GREEN)
        
        self.indicator_radius = 8
        self.indicator_spacing = 25
        self.indicator_y = SCREEN_H - 150
        
        self.map_statistics = []
        for i in range(1, 11):  
            try:
                img = ResourceManager().get_image(f'map_{i}_statistic')
                self.map_statistics.append(img)
            except:
                placeholder = pygame.Surface((600, 400))
                placeholder.fill(GRAY)
                placeholder_text = Font(24).render(f"Map {i} Statistics", True, WHITE)
                placeholder.blit(placeholder_text, (300 - placeholder_text.get_width()//2, 200))
                self.map_statistics.append(placeholder)
        
        self.slide_offset = 0
        self.is_sliding = False
        self.slide_direction = 0 

    def draw(self, surface):
        self.draw_background(surface)
        
        current_img = self.map_statistics[self.current_map]
        img_rect = current_img.get_rect()
        img_rect.center = (SCREEN_W//2 + self.slide_offset, SCREEN_H//2)
        surface.blit(current_img, img_rect)
        
        if self.is_sliding:
            if self.slide_direction == 1: 
                next_index = (self.current_map + 1) % self.total_maps
                next_img = self.map_statistics[next_index]
                next_rect = next_img.get_rect()
                next_rect.center = (SCREEN_W//2 + self.slide_offset - SCREEN_W, SCREEN_H//2)
                surface.blit(next_img, next_rect)
            else:  
                prev_index = (self.current_map - 1) % self.total_maps
                prev_img = self.map_statistics[prev_index]
                prev_rect = prev_img.get_rect()
                prev_rect.center = (SCREEN_W//2 + self.slide_offset + SCREEN_W, SCREEN_H//2)
                surface.blit(prev_img, prev_rect)
        
        self.map_title.set_text(f"Map {self.current_map + 1} Statistics")
        self.map_title.draw(surface)
        
        self.prev_button.draw(surface)
        self.next_button.draw(surface)
        
        self.draw_indicators(surface)
        
        self.back_button.draw(surface)
        self.auto_button.draw(surface)
        
        map_info = Text(f"{self.current_map + 1} / {self.total_maps}", WHITE, 
                       (SCREEN_W//2, self.indicator_y + 40), font=Font(20))
        map_info.draw(surface)

    def draw_indicators(self, surface):
        total_width = (self.total_maps - 1) * self.indicator_spacing
        start_x = SCREEN_W//2 - total_width//2
        
        for i in range(self.total_maps):
            x = start_x + i * self.indicator_spacing
            y = self.indicator_y
            
            if i == self.current_map:
                pygame.draw.circle(surface, WHITE, (x, y), self.indicator_radius)
            else:
                pygame.draw.circle(surface, GRAY, (x, y), self.indicator_radius)
                pygame.draw.circle(surface, WHITE, (x, y), self.indicator_radius, 2)

    def update(self):
        if self.is_sliding:
            if self.slide_direction == 1:  
                self.slide_offset -= SCREEN_W * self.transition_speed
                if self.slide_offset <= -SCREEN_W:
                    self.slide_offset = 0
                    self.is_sliding = False
                    self.current_map = (self.current_map + 1) % self.total_maps
            else:  
                self.slide_offset += SCREEN_W * self.transition_speed
                if self.slide_offset >= SCREEN_W:
                    self.slide_offset = 0
                    self.is_sliding = False
                    self.current_map = (self.current_map - 1) % self.total_maps
        
        if self.is_auto_sliding and not self.is_sliding:
            self.auto_slide_timer += 16  
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
            if self.back_button.hit(event.pos):
                self.go_back()
            
            elif self.prev_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.prev_slide()
            
            elif self.next_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.next_slide()
            
            elif self.auto_button.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.toggle_auto_slide()
            
            else:
                self.handle_indicator_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.prev_slide()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.next_slide()
            elif event.key == pygame.K_SPACE:
                self.toggle_auto_slide()

    def handle_indicator_click(self, pos):
        total_width = (self.total_maps - 1) * self.indicator_spacing
        start_x = SCREEN_W//2 - total_width//2
        
        for i in range(self.total_maps):
            x = start_x + i * self.indicator_spacing
            y = self.indicator_y
            
            distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
            if distance <= self.indicator_radius + 5:  
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.go_to_slide(i)
                break

    def on_exit(self):
        pass