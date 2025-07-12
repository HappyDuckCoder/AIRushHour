from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Audio.AudioManager import AudioManager
from constants import *
import pygame


class AboutUsScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.animation_start_time = 0
        self.animation_duration = 1000  
        self.current_member_index = 0
        self.member_display_time = 2000  
        self.member_start_time = 0
        self.fade_alpha = 0
        self.max_alpha = 255
        
        self.team_members = [
            {
                "name": "TRAN HAI DUC",
                "role": "Leader, Project Manager",
                "description": "Design entire game system and manage team",
            },
            {
                "name": "HUYNH MINH DOAN", 
                "role": "Graphics Artist",
                "description": "Design game graphics and animations",
            },
            {
                "name": "TRAN THAI BAO",
                "role": "Sound Designer",
                "description": "Design game sound effects and music",
            },
            {
                "name": "TRAN SO VINH",
                "role": "QA Tester & Quality Assurance",
                "description": "Test and ensure game quality",
            }
        ]
        
        self.title = Text("ABOUT US", WHITE, (SCREEN_W//2, 100), font=Font(48))
        self.subtitle = Text("Meet Our Team", GRAY, (SCREEN_W//2, 150), font=Font(24))
        
        self.back_button = Button("BACK", (30, SCREEN_H - 80), 120, 50, BLUE)
        
        self.member_name = Text("", WHITE, (SCREEN_W//2, 300), font=Font(36))
        self.member_role = Text("", YELLOW, (SCREEN_W//2, 350), font=Font(24))
        self.member_desc = Text("", GRAY, (SCREEN_W//2, 400), font=Font(18))
        
        self.fade_surface = pygame.Surface((SCREEN_W, SCREEN_H))

    def draw_background_(self, surface):
        self.draw_background(surface)        
        self.draw_decorative_elements(surface)

    def draw_decorative_elements(self, surface):
        pygame.draw.rect(surface, BLUE, (50, 50, SCREEN_W-100, SCREEN_H-100), 2)
        pygame.draw.rect(surface, BLUE, (60, 60, SCREEN_W-120, SCREEN_H-120), 1)
        
        for i in range(5):
            x = 100 + i * 150
            y = 200
            pygame.draw.circle(surface, BLUE, (x, y), 3)

    def update_member_info(self):
        if self.current_member_index < len(self.team_members):
            member = self.team_members[self.current_member_index]
            
            self.member_name = Text(member["name"], WHITE, (SCREEN_W//2, 300), font=Font(36))
            self.member_role = Text(member["role"], YELLOW, (SCREEN_W//2, 350), font=Font(24))
            self.member_desc = Text(member["description"], GRAY, (SCREEN_W//2, 400), font=Font(18))

    def update_fade_effect(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.member_start_time
        
        if elapsed < 500: 
            self.fade_alpha = int((elapsed / 500) * self.max_alpha)
        elif elapsed > self.member_display_time - 500:  
            fade_out_progress = (elapsed - (self.member_display_time - 500)) / 500
            self.fade_alpha = int(self.max_alpha * (1 - fade_out_progress))
        else:
            self.fade_alpha = self.max_alpha

    def draw_member_info(self, surface):
        if self.current_member_index < len(self.team_members):
            member = self.team_members[self.current_member_index]
            
            temp_surface = pygame.Surface((SCREEN_W, SCREEN_H))
            temp_surface.set_alpha(self.fade_alpha)
            temp_surface.fill((0, 0, 0))
            
            self.member_name.draw(temp_surface)
            self.member_role.draw(temp_surface)
            self.member_desc.draw(temp_surface)
            
            surface.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

    def draw(self, surface):
        self.draw_background_(surface)        
        self.title.draw(surface)
        self.subtitle.draw(surface)        
        self.draw_member_info(surface)        
        self.draw_progress_indicator(surface)        
        self.back_button.draw(surface)

    def draw_progress_indicator(self, surface):
        indicator_y = SCREEN_H - 150
        indicator_width = 200
        indicator_height = 8
        indicator_x = SCREEN_W//2 - indicator_width//2
        
        pygame.draw.rect(surface, GRAY, (indicator_x, indicator_y, indicator_width, indicator_height))
        
        if len(self.team_members) > 0:
            segment_width = indicator_width // len(self.team_members)
            for i in range(len(self.team_members)):
                x = indicator_x + i * segment_width
                color = BLUE if i <= self.current_member_index else GRAY
                pygame.draw.rect(surface, color, (x, indicator_y, segment_width-2, indicator_height))

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.member_start_time >= self.member_display_time:
            self.next_member()
        
        self.update_fade_effect()
        
        return True

    def next_member(self):
        self.current_member_index += 1
        if self.current_member_index >= len(self.team_members):
            self.go_back()
        else:
            self.member_start_time = pygame.time.get_ticks()
            self.update_member_info()

    def go_back(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.screen_manager.set_screen("menu")

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')  
        
        self.current_member_index = 0
        self.member_start_time = pygame.time.get_ticks()
        self.animation_start_time = pygame.time.get_ticks()
        self.fade_alpha = 0
        
        self.update_member_info()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.hit(event.pos):
                self.go_back()
            else:
                self.next_member()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_member()
            elif event.key == pygame.K_s:
                self.skip_intro()

    def on_exit(self):
        pass