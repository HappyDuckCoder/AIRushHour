import pygame
import sys
from constants import *
from Screen.BaseScreen import *
from Screen.SupportScreen import *
from Screen.GameScreen import *

# ===============================
# Program Class
# ===============================
class Program:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Rush Hour Puzzle")
        self.clock = pygame.time.Clock()
        self.buffer = pygame.Surface((SCREEN_W, SCREEN_H))
        
        # Initialize screen manager
        self.screen_manager = ScreenManager()
        
        # Create screens
        menu_screen = MenuScreen(self.screen_manager)
        level_select_screen = LevelSelectScreen(self.screen_manager)
        game_screen = GameScreen(self.screen_manager)
        
        # Add screens to manager
        self.screen_manager.add_screen('menu', menu_screen)
        self.screen_manager.add_screen('level_select', level_select_screen)
        self.screen_manager.add_screen('game', game_screen)
        
        # Start with menu screen
        self.screen_manager.set_screen('menu')

    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if self.screen_manager.current_screen:
                        self.screen_manager.current_screen.handle_event(event)
            
            # Update current screen
            if not self.screen_manager.update():
                running = False
            
            # Clear buffer
            self.buffer.fill(BLACK)
            
            # Draw current screen to buffer
            self.screen_manager.draw(self.buffer)
            
            # Blit buffer to screen (double buffering)
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