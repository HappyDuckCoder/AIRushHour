from Screen.BaseScreen import Screen
from Game.Map import Map
from UI.Button import Button
from Graphic.Graphic import *
from Resource.Resource import ResourceManager
from Audio.audio import play_background_music, AudioManager

# ===============================
# Game Screen
# ===============================
class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.map = Map()
        
        # Buttons
        self.reset_btn = Button("Reset", (50, SCREEN_H - 100), 120, 40)
        self.back_btn = Button("Menu", (50, 50), 120, 40)
        self.solve_dfs = Button("Solve With DFS", (50, SCREEN_H - 150), 120, 40, ORANGE)
        self.solve_bfs = Button("Solve With BFS", (50, SCREEN_H - 200), 120, 40, BLUE)
        self.switch_audio = Button("On/Off", (50, 100), 120, 40, GREEN)
        
    def load_level(self, level_num):
        self.map.load_level(level_num)

    def update(self):
        self.map.update_solving()
        return True
    
    def draw_game_background(self, surface):
        """Draw game screen background"""
        background = ResourceManager().get_image('background')
        if background:
            surface.blit(background, (0, 0))
        else:
            surface.fill((40, 40, 80))


    def draw_game_screen(self, surface, buttons):
        """Draw complete game screen"""
        self.draw_game_background(surface)
        
        # Draw map
        self.map.draw(surface)
        
        # Draw UI buttons
        for button in buttons:
            gfx.draw_button(surface, button)

    def draw(self, surface):
        self.draw_game_screen(surface, [self.reset_btn, self.back_btn, self.solve_dfs, self.solve_bfs, self.switch_audio])

    def handle_event(self, event):
        play_background_music('game', fade_in=False)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.reset_btn.hit(event.pos):
                self.map.reset()
            elif self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            elif self.solve_dfs.hit(event.pos):
                self.map.start_solving("DFS")
            elif self.solve_bfs.hit(event.pos):
                self.map.start_solving("BFS")
            elif self.switch_audio.hit(event.pos):
                AudioManager().toggle_music()
            else:
                self.map.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.map.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.map.handle_mouse_motion(event.pos)