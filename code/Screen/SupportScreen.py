from constants import *
from UI.Button import *
from Screen.BaseScreen import *
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
        gfx.draw_title(surface, "RUSH HOUR", (SCREEN_W//2, 200))
        gfx.draw_subtitle(surface, "Puzzle Game", (SCREEN_W//2, 250))
        gfx.draw_button(surface, play_button)    

    def draw(self, surface):        
        self.draw_menu_screen(surface, self.play_btn)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_btn.hit(event.pos):
                self.screen_manager.set_screen('level_select')

# ===============================
# Level Select Screen
# ===============================
class LevelSelectScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.back_btn = Button("BACK", (50, 50), 120, 50)
        self.level_buttons = []
        
        # Create 2 level buttons
        button_width = 120
        button_height = 80
        start_x = SCREEN_W//2 - button_width - 10
        start_y = 300
        
        for i in range(2):
            x = start_x + i * (button_width + 20)
            y = start_y
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
