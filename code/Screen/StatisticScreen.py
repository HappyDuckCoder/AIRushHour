from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Audio.AudioManager import AudioManager
from constants import *
import pygame

# ===============================
# Statistic Screen
# ===============================
class StatisticScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.updating_text = Text("Updating", WHITE, (SCREEN_W//2, SCREEN_H//2), font=Font(48))
        
        self.back_button = Button("BACK", (30, SCREEN_H - 80), 120, 50, BLUE)

    def draw(self, surface):
        self.draw_background(surface)
        self.updating_text.draw(surface)        
        self.back_button.draw(surface)

    def update(self):
        return True

    def go_back(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.screen_manager.set_screen("menu")

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        # Xử lý click button Back
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.hit(event.pos):
                self.go_back()

    def on_exit(self):
        pass