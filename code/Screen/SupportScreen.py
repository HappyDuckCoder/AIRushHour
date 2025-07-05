from constants import *
from UI.Button import Button
from Screen.BaseScreen import Screen
from Graphic.Graphic import *

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 50), 200, 60)
        
    def draw_menu_background(self, surface):
        """Draw menu screen background"""
        surface.fill((30, 30, 60))

    def draw_menu_screen(self, surface, play_button):
        """Draw complete menu screen"""
        self.draw_menu_background(surface)

        # self.title.draw(surface)

        gfx.draw_title(surface, "RUSH HOUR", (SCREEN_W//2, 200))
        gfx.draw_subtitle(surface, "Puzzle Game", (SCREEN_W//2, 250))

        # self.button.draw(surface)
        gfx.draw_button(surface, play_button)    

    def draw(self, surface):        
        self.draw_menu_screen(surface, self.play_btn)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_btn.hit(event.pos):

                # bật sound nhấn nút

                self.screen_manager.set_screen('level_select')

# ===============================
# Level Select Screen
# ===============================
class LevelSelectScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.back_btn = Button("BACK", (50, 50), 120, 50)
        self.level_buttons = []
        
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
        surface.fill((25, 35, 50))

    def draw_level_select_screen(self, surface, level_buttons, back_button):
        """Draw complete level select screen"""
        self.draw_level_select_background(surface)
        gfx.draw_title(surface, "SELECT LEVEL", (SCREEN_W//2, 150), 64, WHITE)
        
        for btn in level_buttons:
            gfx.draw_button(surface, btn)
        
        gfx.draw_button(surface, back_button)

    def draw(self, surface):
        self.draw_level_select_screen(surface, self.level_buttons, self.back_btn)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            else:
                for i, btn in enumerate(self.level_buttons):
                    if btn.hit(event.pos):
                        game_screen = self.screen_manager.screens['game']
                        game_screen.load_level(i + 1)
                        self.screen_manager.set_screen('game')

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

    def draw_intro_background(self, surface):
        surface.fill((10, 10, 30))
        
    def draw_intro(self, surface):
        self.draw_intro_background(surface)
        elapsed = pygame.time.get_ticks() - self.start_time

        if elapsed < self.duration:
            # Animate the title moving up
            progress = elapsed / self.duration
            current_y = self.title_y - (self.title_y - self.target_y) * progress
            gfx.draw_title(surface, "RUSH HOUR", (SCREEN_W // 2, int(current_y)))
        else:
            self.screen_manager.set_screen("menu")

    def draw(self, surface):
        self.draw_intro(surface)

    def handle_event(self, event):
        pass  # No interaction
