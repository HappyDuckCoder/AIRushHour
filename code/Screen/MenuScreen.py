from Screen.BaseScreen import Screen
from UI.Button import Button
from UI.Text import Text, Font
from Graphic.Graphic import gfx, pygame
from Audio.Audio import AudioManager
from constants import *

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 50), 200, 60, BLUE)
        self.setting_btn = Button("SETTINGS", (SCREEN_W//2 - 100, SCREEN_H//2 + 30), 200, 60, BLUE)
        self.title = Text("RUSHRELIC", WHITE, (SCREEN_W//2, 200), font = Font(64))
        
    def draw_menu_background(self, surface):
        self.draw_background(surface, "menu")

    def draw_menu_screen(self, surface, play_button, setting_button):
        """Draw complete menu screen"""
        self.draw_menu_background(surface)

        self.title.draw(surface)

        play_button.draw(surface)    
        setting_button.draw(surface)

    def draw(self, surface):        
        self.draw_menu_screen(surface, self.play_btn, self.setting_btn)

    def update(self):
        """Update animations"""
        self.play_btn.update()
        self.setting_btn.update()
        return True

    def on_enter(self):
        """Called when entering menu screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        # QUAN TRỌNG: Gọi handle_event của button để xử lý hover/click
        self.play_btn.handle_event(event)
        self.setting_btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.hit(event.pos):
                # Sử dụng AudioManager singleton để phát hiệu ứng âm thanh
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')

                self.screen_manager.set_screen('level_select')
            
            elif self.setting_btn.hit(event.pos):
                # Chuyển đến màn hình setting
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                
                self.screen_manager.set_screen('setting')