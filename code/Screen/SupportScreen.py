from constants import *
from UI.Button import *
from Screen.BaseScreen import *

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 50), 200, 60)
        
    def draw(self, surface):
        surface.fill((30, 30, 60))
        
        # Title
        font = pygame.font.SysFont(None, 96)
        title = font.render("RUSH HOUR", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_W//2, 200))
        surface.blit(title, title_rect)
        
        # Subtitle
        small_font = pygame.font.SysFont(None, 36)
        subtitle = small_font.render("Puzzle Game", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_W//2, 250))
        surface.blit(subtitle, subtitle_rect)
        
        # Button
        self.play_btn.draw(surface)
        
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
            
    def draw(self, surface):
        surface.fill((25, 35, 50))
        
        # Title
        font = pygame.font.SysFont(None, 64)
        title = font.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_W//2, 150))
        surface.blit(title, title_rect)
        
        # Level buttons
        for btn in self.level_buttons:
            btn.draw(surface)
            
        # Back button
        self.back_btn.draw(surface)
        
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
