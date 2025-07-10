from Screen.BaseScreen import Screen
from UI.Button import Button
from UI.Text import Text, Font
from Graphic.Graphic import gfx, pygame
from Audio.AudioManager import AudioManager
from constants import *
import sys

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        # Điều chỉnh vị trí các nút để có không gian cho 4 nút
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 80), 200, 60, BLUE)
        self.setting_btn = Button("SETTINGS", (SCREEN_W//2 - 100, SCREEN_H//2 - 10), 200, 60, BLUE)
        self.statistic_btn = Button("STATISTIC", (SCREEN_W//2 - 100, SCREEN_H//2 + 60), 200, 60, BLUE)
        self.about_us_btn = Button("ABOUT US", (SCREEN_W//2 - 100, SCREEN_H//2 + 130), 200, 60, BLUE)
        self.exit_btn = Button("EXIT", (SCREEN_W//2 - 100, SCREEN_H//2 + 200), 200, 60, RED)
        
        self.title = Text("RUSHRELIC", WHITE, (SCREEN_W//2, 200), font = Font(64))
        
    def draw_menu_background(self, surface):
        self.draw_background(surface, "menu")

    def draw_menu_screen(self, surface, play_button, setting_button, statistic_button, exit_button, about_us_button):
        """Draw complete menu screen"""
        self.draw_menu_background(surface)

        self.title.draw(surface)

        play_button.draw(surface)    
        setting_button.draw(surface)
        statistic_button.draw(surface)
        exit_button.draw(surface)
        about_us_button.draw(surface)

    def draw(self, surface):        
        self.draw_menu_screen(surface, self.play_btn, self.setting_btn, self.statistic_btn, self.exit_btn, self.about_us_btn)

    def update(self):
        """Update animations"""
        self.play_btn.update()
        self.setting_btn.update()
        self.statistic_btn.update()
        self.about_us_btn.update()
        self.exit_btn.update()
        return True

    def on_enter(self):
        """Called when entering menu screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        self.play_btn.handle_event(event)
        self.setting_btn.handle_event(event)
        self.statistic_btn.handle_event(event)
        self.about_us_btn.handle_event(event)
        self.exit_btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.hit(event.pos):
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')

                self.screen_manager.set_screen('level_select')
            
            elif self.setting_btn.hit(event.pos):
                # Chuyển đến màn hình setting
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                
                self.screen_manager.set_screen('setting')
            
            elif self.statistic_btn.hit(event.pos):
                # Chuyển đến màn hình statistic
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                
                self.screen_manager.set_screen('statistic')

            elif self.about_us_btn.hit(event.pos):
                # Chuyển đến màn hình about us
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                
                self.screen_manager.set_screen('about_us')
            
            elif self.exit_btn.hit(event.pos):
                # Thoát game
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                
                # Có thể thêm hiệu ứng fade out hoặc confirmation dialog
                pygame.quit()
                sys.exit()