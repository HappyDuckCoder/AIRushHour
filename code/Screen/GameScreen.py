from Screen.BaseScreen import Screen
from Game.Map import Map
from UI.Button import Button
from UI.Text import Text, Font
from Graphic.Graphic import *
from Resource.Resource import ResourceManager
from Audio.Audio import AudioManager

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
        button_width = 140
        button_height = 45
        button_spacing = 15

        # Top navigation buttons (positioned at top)
        top_margin = 20
        self.back_btn = Button("Back", (20, top_margin), button_width, button_height)
        self.menu_btn = Button("Main Menu", (180, top_margin), button_width, button_height, GRAY)
        
        # Top-right corner buttons
        right_margin = 20
        self.next_level_btn = Button("Next Level", (SCREEN_W - button_width - right_margin, top_margin), button_width, button_height, GREEN)
        self.switch_audio = Button("Audio On/Off", (SCREEN_W - button_width - right_margin, top_margin + button_height + 15), button_width, button_height, GREEN)
        
        # Bottom-left corner buttons
        bottom_margin = 20
        left_margin = 20
        
        # Start button (bottom-left)
        self.start_btn = Button("Start", (left_margin, SCREEN_H - button_height - bottom_margin), button_width, button_height, GREEN)
        
        # Algorithm selection buttons (stacked vertically from bottom)
        algo_start_y = SCREEN_H - bottom_margin - button_height
        self.solve_bfs = Button("BFS", (left_margin, algo_start_y - (button_height + button_spacing) * 3), button_width, button_height, BLUE)
        self.solve_dfs = Button("DFS", (left_margin, algo_start_y - (button_height + button_spacing) * 2), button_width, button_height, ORANGE)
        self.solve_astar = Button("A*", (left_margin, algo_start_y - (button_height + button_spacing) * 1), button_width, button_height, PURPLE)
        self.solve_ucs = Button("UCS", (left_margin, algo_start_y), button_width, button_height, YELLOW)
        
        # Solving control buttons (positioned in bottom-left)
        self.reset_btn = Button("Reset", (left_margin, algo_start_y - (button_height + button_spacing) * 1), button_width, button_height, RED)
        self.pause_btn = Button("Pause", (left_margin, algo_start_y), button_width, button_height, RED)
        
        # Text elements for game information
        self.level_text = Text("Level: 1", WHITE, (SCREEN_W//2, 30), font=Font(32))
        self.algorithm_text = Text("", WHITE, (SCREEN_W//2, 70), font=Font(24))
        self.status_text = Text("Click Start to begin", WHITE, (SCREEN_W//2, SCREEN_H - 50), font=Font(20))
        self.instruction_text = Text("Select an algorithm:", WHITE, (left_margin + button_width + 20, algo_start_y - 60), font=Font(18), center=False)
        
    def load_level(self, level_num):
        self.map.load_level_data_from_file(level_num)
        self.ui_state = "start"  # Reset UI state when loading new level
        
        # Update level text
        self.level_text.set_text(f"Level: {level_num}")
        self.algorithm_text.set_text("")
        self.status_text.set_text("Click Start to begin")

    def update(self):
        for button in self.get_visible_buttons():
            button.update()

        self.map.update()
        self.map.update_solving()
        
        # Update status text based on current state
        if self.ui_state == "start":
            if hasattr(self.map, 'is_solved') and self.map.is_solved:
                self.status_text.set_text("Level Complete! Click Next Level")
            else:
                self.status_text.set_text("Click Start to begin")
        elif self.ui_state == "algorithm_select":
            self.status_text.set_text("Choose solving algorithm")
        elif self.ui_state == "solving":
            if self.is_paused:
                self.status_text.set_text("Paused - Click Continue to resume")
            else:
                if hasattr(self.map, 'current_algorithm'):
                    self.status_text.set_text(f"Solving using {self.map.current_algorithm}...")
                else:
                    self.status_text.set_text("Solving...")
        
        return True
    
    def draw_game_background(self, surface):
        """Draw game screen background"""
        self.draw_background(surface, "game")

    def get_visible_buttons(self):
        """Return list of buttons that should be visible based on current UI state"""
        # Always visible buttons
        visible_buttons = [self.back_btn, self.next_level_btn, self.menu_btn, self.switch_audio]
        
        if self.ui_state == "start":
            visible_buttons.append(self.start_btn)
        elif self.ui_state == "algorithm_select":
            visible_buttons.extend([self.solve_bfs, self.solve_dfs, self.solve_astar, self.solve_ucs])
        elif self.ui_state == "solving":
            visible_buttons.extend([self.reset_btn, self.pause_btn])
            
        return visible_buttons

    def get_visible_texts(self):
        """Return list of text elements that should be visible based on current UI state"""
        visible_texts = [self.level_text, self.status_text]
        
        if self.algorithm_text.text:  # Only show if algorithm is selected
            visible_texts.append(self.algorithm_text)
            
        if self.ui_state == "algorithm_select":
            visible_texts.append(self.instruction_text)
            
        return visible_texts

    def draw_game_screen(self, surface, buttons, texts):
        """Draw complete game screen"""
        self.draw_game_background(surface)
        
        # Draw map
        self.map.draw(surface)
        
        # Draw UI buttons
        for button in buttons:
            button.draw(surface)
            
        # Draw text elements
        for text in texts:
            text.draw(surface)

    def draw(self, surface):
        visible_buttons = self.get_visible_buttons()
        visible_texts = self.get_visible_texts()
        self.draw_game_screen(surface, visible_buttons, visible_texts)

    def handle_event(self, event):
        AudioManager().play_background_music('game', fade_in=False)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ui_state == "start":
                if self.start_btn.hit(event.pos):
                    self.ui_state = "algorithm_select"
                    
            elif self.ui_state == "algorithm_select":
                if self.solve_bfs.hit(event.pos):
                    self.map.start_solving("BFS")
                    self.algorithm_text.set_text("Algorithm: BFS")
                    self.ui_state = "solving"
                elif self.solve_dfs.hit(event.pos):
                    self.map.start_solving("DFS")
                    self.algorithm_text.set_text("Algorithm: DFS")
                    self.ui_state = "solving"
                elif self.solve_astar.hit(event.pos):
                    self.map.start_solving("A*")
                    self.algorithm_text.set_text("Algorithm: A*")
                    self.ui_state = "solving"
                elif self.solve_ucs.hit(event.pos):
                    self.map.start_solving("UCS")
                    self.algorithm_text.set_text("Algorithm: UCS")
                    self.ui_state = "solving"
                    
            elif self.ui_state == "solving":
                if self.reset_btn.hit(event.pos):
                    self.map.reset()
                    self.ui_state = "start"
                    self.algorithm_text.set_text("")
                elif self.pause_btn.hit(event.pos):
                    pause_result = self.map.handle_pause()
                    
                    if pause_result:  # Có sự thay đổi của các xe
                        self.ui_state = "start"
                        self.is_paused = False
                        self.pause_btn.set_text("Pause")
                        self.algorithm_text.set_text("")
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
            elif self.switch_audio.hit(event.pos):
                AudioManager().toggle_music()
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