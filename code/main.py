import pygame
import sys
from constants import *
from Screen.IntroScreen import IntroScreen
from Screen.MenuScreen import MenuScreen
from Screen.LevelSelectScreen import LevelSelectScreen
from Screen.GameScreen import GameScreen
from Screen.WinningScreen import WinningScreen
from Screen.SettingScreen import SettingScreen
from Screen.AboutUsScreen import AboutUsScreen
from Screen.BaseScreen import ScreenManager
from Screen.StatisticScreen import StatisticScreen
from Resource.Resource import ResourceManager
from UI.Mouse import Mouse
from UI.Text import Font

# ===============================
# Program Class - Singleton
# ===============================
class Program:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Program, cls).__new__(cls)
        return cls._instance

    def create_window(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("RushRelic")
        self.clock = pygame.time.Clock()
        self.buffer = pygame.Surface((SCREEN_W, SCREEN_H))

    def create_all_screens(self):
        # Create screens
        intro_screen = IntroScreen(self.screen_manager)
        menu_screen = MenuScreen(self.screen_manager)
        level_select_screen = LevelSelectScreen(self.screen_manager)
        game_screen = GameScreen(self.screen_manager)
        setting_screen = SettingScreen(self.screen_manager)
        winning_screen = WinningScreen(self.screen_manager)
        about_us_screen = AboutUsScreen(self.screen_manager)
        statistic_screen = StatisticScreen(self.screen_manager)

        # Add screens to manager
        self.screen_manager.add_screen('intro', intro_screen)
        self.screen_manager.add_screen('menu', menu_screen)
        self.screen_manager.add_screen('level_select', level_select_screen)
        self.screen_manager.add_screen('game', game_screen)
        self.screen_manager.add_screen('setting', setting_screen)
        self.screen_manager.add_screen('winning', winning_screen)
        self.screen_manager.add_screen('about_us', about_us_screen)
        self.screen_manager.add_screen('statistic', statistic_screen)


    def __init__(self):
        # Chỉ init lần đầu
        if hasattr(self, '_initialized') and self._initialized:
            return

        pygame.init()
        pygame.mouse.set_visible(False)

        # Create window
        self.create_window()        

        # Upload all resources
        ResourceManager().upload_all()

        # Create mouse and font
        self.mouse = Mouse()
        self.MainFont = Font(24)
        
        # Initialize screen manager
        self.screen_manager = ScreenManager()

        # Create all screens
        self.create_all_screens()

        # Start with intro screen
        # self.screen_manager.set_screen('intro')

        # quick test in game
        game_screen = self.screen_manager.screens['game']
        game_screen.load_level(1)
        self.screen_manager.set_screen('game')

        # Mark as initialized
        self._initialized = True

    def run(self):
        running = True
        while running:
            # RECEIVE EVENT
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if self.screen_manager.current_screen:
                        self.screen_manager.current_screen.handle_event(event)

            # UPDATE NEW STATUS
            if not self.screen_manager.update():
                running = False

            # DRAW ALL IN THE BACK BUFFER
            self.buffer.fill(BLACK)
            self.screen_manager.draw(self.buffer)
            self.mouse.draw(self.buffer)
            self.screen.blit(self.buffer, (0, 0))
            
            # FLIP TO THE FRONT BUFFER
            pygame.display.flip()
            
            # WAITING TIME TILL NEXT FRAME
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    Program().run()
