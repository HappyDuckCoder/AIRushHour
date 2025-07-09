from constants import *
from UI.Button import Button
from UI.Text import Text, Font
from Screen.BaseScreen import Screen
from Graphic.Graphic import gfx, pygame
from Audio.Audio import AudioManager

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 50), 200, 60, BLUE)
        self.title = Text("RUSHRELIC", WHITE, (SCREEN_W//2, 200), font = Font(64))
        
    def draw_menu_background(self, surface):
        self.draw_background(surface, "menu")

    def draw_menu_screen(self, surface, play_button):
        """Draw complete menu screen"""
        self.draw_menu_background(surface)

        self.title.draw(surface)

        play_button.draw(surface)    

    def draw(self, surface):        
        self.draw_menu_screen(surface, self.play_btn)

    def update(self):
        """Update animations"""
        self.play_btn.update()
        return True

    def on_enter(self):
        """Called when entering menu screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')

    def handle_event(self, event):
        # QUAN TRỌNG: Gọi handle_event của button để xử lý hover/click
        self.play_btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.hit(event.pos):
                # Sử dụng AudioManager singleton để phát hiệu ứng âm thanh
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')

                self.screen_manager.set_screen('level_select')

# ===============================
# Level Select Screen
# ===============================
class LevelSelectScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.back_btn = Button("BACK", (50, 50), 120, 50)
        self.level_buttons = []
        
        # Tạo Text object cho title
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
        """Draw level select screen background"""
        self.draw_background(surface, "level_select")

    def draw_level_select_screen(self, surface, level_buttons, back_button):
        """Draw complete level select screen"""
        self.draw_level_select_background(surface)
        
        # Sử dụng Text object thay vì gfx.draw_title
        self.select_level_title.draw(surface)
        
        for btn in level_buttons:
            btn.draw(surface)
        
        back_button.draw(surface)

    def draw(self, surface):
        self.draw_level_select_screen(surface, self.level_buttons, self.back_btn)

    def update(self):
        """Update animations"""
        self.back_btn.update()
        for btn in self.level_buttons:
            btn.update()
        return True

    def on_enter(self):
        """Called when entering level select screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('level_select')
        
    def handle_event(self, event):
        self.back_btn.handle_event(event)
        for btn in self.level_buttons:
            btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Lấy instance của AudioManager
            audio_manager = AudioManager.get_instance()
            
            if self.back_btn.hit(event.pos):
                # Phát hiệu ứng âm thanh khi click back
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen('menu')
            else:
                for i, btn in enumerate(self.level_buttons):
                    if btn.hit(event.pos):
                        # Phát hiệu ứng âm thanh khi chọn level
                        audio_manager.play_sound_effect('level_select')
                        
                        # Load level và chuyển màn hình
                        game_screen = self.screen_manager.screens['game']
                        game_screen.load_level(i + 1)
                        self.screen_manager.set_screen('game')
                        break

# ===============================
# Intro Screen
# ===============================
class IntroScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.timer = 0
        self.duration = 2000  # milliseconds
        self.start_time = pygame.time.get_ticks()
        self.title_y = SCREEN_H
        self.target_y = SCREEN_H // 2
        
        # Tạo Text object cho title intro
        self.intro_title = Text("RUSHRELIC", WHITE, (SCREEN_W//2, self.title_y), font=Font(64))

    def draw_intro_background(self, surface):
        self.draw_background(surface, "intro")
        
    def draw_intro(self, surface):
        self.draw_intro_background(surface)
        elapsed = pygame.time.get_ticks() - self.start_time

        if elapsed < self.duration:
            # Animate the title moving up
            progress = elapsed / self.duration
            current_y = self.title_y - (self.title_y - self.target_y) * progress
            
            # Cập nhật vị trí của Text object
            self.intro_title.rect.centery = int(current_y)
            self.intro_title.draw(surface)
        else:
            self.screen_manager.set_screen("menu")

    def draw(self, surface):
        self.draw_intro(surface)

    def update(self):
        """Update intro animation"""
        return True

    def on_enter(self):
        """Called when entering intro screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền intro
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('intro')
        
        # Reset thời gian bắt đầu và vị trí title
        self.start_time = pygame.time.get_ticks()
        self.intro_title.rect.centery = self.title_y

    def handle_event(self, event):
        # Cho phép skip intro bằng cách click hoặc nhấn phím
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            audio_manager = AudioManager.get_instance()
            audio_manager.play_sound_effect('button_click')
            self.screen_manager.set_screen("menu")