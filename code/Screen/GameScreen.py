from Screen.BaseScreen import Screen
from Game.Map import Map
from UI.Button import Button
from Graphic.Graphic import *
from Resource.Resource import ResourceManager

# ===============================
# Game Screen
# ===============================
class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.map = Map()
        self.is_paused = False
        
        # UI State management
        self.ui_state = "start"  # "start", "algorithm_select", "solving"
        
        # Button dimensions
        button_x = 50
        button_width = 120
        button_height = 40
        button_spacing = 10

        # Always visible buttons (top-right corner)
        right_x = SCREEN_W - button_width - 50
        self.back_btn = Button("Back", (50, 50), button_width, button_height)
        self.next_level_btn = Button("Next Level", (right_x, 50), button_width, button_height, GREEN)
        self.menu_btn = Button("Main Menu", (right_x, 100), button_width, button_height, GRAY)
        
        # Start button (bottom corner)
        self.start_btn = Button("Start", (button_x, SCREEN_H - 50), button_width, button_height, GREEN)
        
        # Algorithm selection buttons (hidden initially)
        self.solve_bfs = Button("BFS", (button_x, SCREEN_H - 200), button_width, button_height, BLUE)
        self.solve_dfs = Button("DFS", (button_x, SCREEN_H - 150), button_width, button_height, ORANGE)
        self.solve_astar = Button("A*", (button_x, SCREEN_H - 100), button_width, button_height, PURPLE)
        self.solve_ucs = Button("UCS", (button_x, SCREEN_H - 50), button_width, button_height, YELLOW)
        
        # Solving control buttons (hidden initially)
        self.reset_btn = Button("Reset", (button_x, SCREEN_H - 150), button_width, button_height, RED)
        self.pause_btn = Button("Pause", (button_x, SCREEN_H - 100), button_width, button_height, RED)
        
    def load_level(self, level_num):
        self.map.load_level_data_from_file(level_num)
        self.ui_state = "start"  # Reset UI state when loading new level

    def update(self):
        self.map.update()
        self.map.update_solving()
        return True
    
    def draw_game_background(self, surface):
        """Draw game screen background"""
        background = ResourceManager().get_image('background')
        if background:
            surface.blit(background, (0, 0))
        else:
            surface.fill((40, 40, 80))

    def get_visible_buttons(self):
        """Return list of buttons that should be visible based on current UI state"""
        # Always visible buttons
        visible_buttons = [self.back_btn, self.next_level_btn, self.menu_btn]
        
        if self.ui_state == "start":
            visible_buttons.append(self.start_btn)
        elif self.ui_state == "algorithm_select":
            visible_buttons.extend([self.solve_bfs, self.solve_dfs, self.solve_astar, self.solve_ucs])
        elif self.ui_state == "solving":
            visible_buttons.extend([self.reset_btn, self.pause_btn])
            
        return visible_buttons

    def draw_game_screen(self, surface, buttons):
        """Draw complete game screen"""
        self.draw_game_background(surface)
        
        # Draw map
        self.map.draw(surface)
        
        # Draw UI buttons
        for button in buttons:
            gfx.draw_button(surface, button)

    def draw(self, surface):
        visible_buttons = self.get_visible_buttons()
        self.draw_game_screen(surface, visible_buttons)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ui_state == "start":
                if self.start_btn.hit(event.pos):
                    self.ui_state = "algorithm_select"
                    
            elif self.ui_state == "algorithm_select":
                if self.solve_bfs.hit(event.pos):
                    self.map.start_solving("BFS")
                    self.ui_state = "solving"
                elif self.solve_dfs.hit(event.pos):
                    self.map.start_solving("DFS")
                    self.ui_state = "solving"
                elif self.solve_astar.hit(event.pos):
                    self.map.start_solving("A*")
                    self.ui_state = "solving"
                elif self.solve_ucs.hit(event.pos):
                    self.map.start_solving("UCS")
                    self.ui_state = "solving"
                    
            elif self.ui_state == "solving":
                if self.reset_btn.hit(event.pos):
                    self.map.reset()
                    self.ui_state = "start"
                elif self.pause_btn.hit(event.pos):
                    pause_result = self.map.handle_pause()
                    
                    if pause_result:  # Có sự thay đổi của các xe
                        self.ui_state = "start"
                        self.is_paused = False
                        self.pause_btn.set_text("Pause")
                    else:  # Không có sự thay đổi
                        self.is_paused = not self.is_paused
                        new_text = "Continue" if self.is_paused else "Pause"
                        self.pause_btn.set_text(new_text)
            
            # Always check these buttons regardless of UI state
            if self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('level_select')
            elif self.next_level_btn.hit(event.pos):
                self.next_level()
            elif self.menu_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            else:
                # Only handle map interactions in start state
                if self.ui_state == "start":
                    self.map.handle_mouse_down(event.pos)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.ui_state == "start":
                self.map.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.ui_state == "start":
                self.map.handle_mouse_motion(event.pos)

    def next_level(self):
        """Load next level"""
        next_level_num = self.map.current_level + 1
        try:
            self.load_level(next_level_num)
        except:
            print(f"Level {next_level_num} not found, staying at current level")
            pass