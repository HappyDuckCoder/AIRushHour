from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
from constants import *
import pygame


class IntroScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.timer = 0
        self.duration = 2000  
        self.start_time = pygame.time.get_ticks()
        self.title_y = SCREEN_H
        self.target_y = SCREEN_H // 2
        self.intro_title = Text("RUSHRELIC", WHITE, (SCREEN_W//2, self.title_y), font=Font(64))

    def draw_intro_background(self, surface):
        self.draw_background(surface, "intro")
        
    def draw_intro(self, surface):
        self.draw_intro_background(surface)
        elapsed = pygame.time.get_ticks() - self.start_time

        if elapsed < self.duration:
            progress = elapsed / self.duration
            current_y = self.title_y - (self.title_y - self.target_y) * progress
            self.intro_title.rect.centery = int(current_y)
            self.intro_title.draw(surface)
        else:
            self.screen_manager.set_screen("menu")

    def draw(self, surface):
        self.draw_intro(surface)

    def update(self):
        return True

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('intro')
        
        self.start_time = pygame.time.get_ticks()
        self.intro_title.rect.centery = self.title_y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            audio_manager = AudioManager.get_instance()
            audio_manager.play_sound_effect('button_click')
            self.screen_manager.set_screen("menu")