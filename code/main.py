import pygame
import sys
from constants import *
from Screen.SupportScreen import IntroScreen, MenuScreen, LevelSelectScreen
from Screen.GameScreen import GameScreen
from Screen.BaseScreen import ScreenManager
from Resource.Resource import ResourceManager

# ===============================
# Program Class - Singleton
# ===============================
class Program:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Program, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Chỉ init lần đầu
        if hasattr(self, '_initialized') and self._initialized:
            return

        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Rush Hour Puzzle")
        self.clock = pygame.time.Clock()
        self.buffer = pygame.Surface((SCREEN_W, SCREEN_H))

        # Initialize screen manager
        self.screen_manager = ScreenManager()

        # Upload all resources
        ResourceManager().upload_all()

        # Create screens
        intro_screen = IntroScreen(self.screen_manager)
        menu_screen = MenuScreen(self.screen_manager)
        level_select_screen = LevelSelectScreen(self.screen_manager)
        game_screen = GameScreen(self.screen_manager)

        # Add screens to manager
        self.screen_manager.add_screen('intro', intro_screen)
        self.screen_manager.add_screen('menu', menu_screen)
        self.screen_manager.add_screen('level_select', level_select_screen)
        self.screen_manager.add_screen('game', game_screen)

        # Start with intro screen
        self.screen_manager.set_screen('intro')

        # Đánh dấu đã init rồi
        self._initialized = True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if self.screen_manager.current_screen:
                        self.screen_manager.current_screen.handle_event(event)

            if not self.screen_manager.update():
                running = False

            self.buffer.fill(BLACK)
            self.screen_manager.draw(self.buffer)
            self.screen.blit(self.buffer, (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    Program().run()
