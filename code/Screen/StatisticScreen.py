from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Graphic.Graphic import gfx, pygame
from Audio.AudioManager import AudioManager
from constants import *

# ===============================
# Statistic Screen
# ===============================
class StatisticScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        # Tạo Text object cho chữ "Updating"
        self.updating_text = Text("Updating", WHITE, (SCREEN_W//2, SCREEN_H//2), font=Font(48))
        
        # Tạo button Back
        self.back_button = Button(
            "BACK", 
            (30, SCREEN_H - 80), 
            120, 50,
            BLUE
        )

    def draw(self, surface):
        """Vẽ toàn bộ statistic screen"""
        # Vẽ background đen
        self.draw_background(surface)
        
        # Vẽ chữ "Updating"
        self.updating_text.draw(surface)
        
        # Vẽ button Back
        self.back_button.draw(surface)

    def update(self):
        """Cập nhật logic của statistic screen"""
        return True

    def go_back(self):
        """Quay về menu chính"""
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.screen_manager.set_screen("menu")

    def on_enter(self):
        """Được gọi khi vào statistic screen"""
        # Phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        """Xử lý sự kiện input"""
        # Xử lý click button Back
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.hit(event.pos):
                self.go_back()
        
        # Xử lý phím ESC để quay về
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()

    def on_exit(self):
        """Được gọi khi rời khỏi statistic screen"""
        pass