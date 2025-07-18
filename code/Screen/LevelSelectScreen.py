from constants import *
from UI.Button import Button
from UI.Text import Text, Font
from Screen.BaseScreen import Screen
from Audio.AudioManager import AudioManager
import pygame


class LevelSelectScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.back_btn = Button("BACK", (50, 50), 120, 50)
        self.level_buttons = []
        
        self.select_level_title = Text("SELECT LEVEL", WHITE, (SCREEN_W//2, 150), font=Font(64))
        
        button_width = 140
        button_height = 60
        cols = 3
        padding_x = 40
        padding_y = 30
        start_x = SCREEN_W // 2 - ((button_width + padding_x) * cols // 2) + padding_x // 2
        start_y = 250

        for i in range(NUMBER_OF_MAP):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_width + padding_x)
            y = start_y + row * (button_height + padding_y)
            self.level_buttons.append(Button(f"Level {i+1}", (x, y), button_width, button_height))

    def draw_level_select_background(self, surface):
        self.draw_background(surface, "level_select")

    def draw_level_select_screen(self, surface, level_buttons, back_button):
        self.draw_level_select_background(surface)
        
        self.select_level_title.draw(surface)
        
        for btn in level_buttons:
            btn.draw(surface)
        
        back_button.draw(surface)

    def draw(self, surface):
        self.draw_level_select_screen(surface, self.level_buttons, self.back_btn)

    def update(self):
        self.back_btn.update()
        for btn in self.level_buttons:
            btn.update()
        return True

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('level_select')
        
    def handle_event(self, event):
        self.back_btn.handle_event(event)
        for btn in self.level_buttons:
            btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            audio_manager = AudioManager.get_instance()            
            if self.back_btn.hit(event.pos):
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen('menu')
            else:
                for i, btn in enumerate(self.level_buttons):
                    if btn.hit(event.pos):
                        audio_manager.play_sound_effect('level_select')                        
                        game_screen = self.screen_manager.screens['game']
                        game_screen.load_level(i + 1)
                        self.screen_manager.set_screen('game')
                        break

