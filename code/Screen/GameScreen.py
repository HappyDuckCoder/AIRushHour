from Screen.BaseScreen import Screen
from Game.Map import Map
from UI.Button import Button
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
import time
from constants import *
import pygame

# ===============================
# Game Screen
# ===============================
class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.map = Map()
        self.is_paused = False
        
        # UI State management
        self.ui_state = "start"  # "start", "algorithm_select", "solving", "no_solution"
        
        # Algorithm info tracking
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        
        # No solution message timer
        self.no_solution_timer = 0
        self.no_solution_duration = 3.0  # Show message for 3 seconds
        
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
        self.solve_ucs = Button("UCS", (left_margin, algo_start_y), button_width, button_height, PINK)
        
        # Solving control buttons (positioned in bottom-left)
        self.reset_btn = Button("Reset", (left_margin, algo_start_y - (button_height + button_spacing) * 1), button_width, button_height, RED)
        self.pause_btn = Button("Pause", (left_margin, algo_start_y), button_width, button_height, RED)
        
        # Try Again button for no solution state
        self.try_again_btn = Button("Try Again", (left_margin, algo_start_y), button_width, button_height, ORANGE)
        
        # Store all buttons for easy access
        self.all_buttons = [
            self.back_btn, self.menu_btn, self.next_level_btn,
            self.start_btn, self.solve_bfs, self.solve_dfs, self.solve_astar,
            self.solve_ucs, self.reset_btn, self.pause_btn, self.try_again_btn
        ]
        
        # Text elements for game information - INCREASED FONT SIZES BY 5x
        self.level_text = Text("Level: 1", WHITE, (SCREEN_W//2, 30), font=Font(32)) 
        self.algorithm_text = Text("", WHITE, (SCREEN_W//2, 70), font=Font(24))  
        self.status_text = Text("Click Start to begin", WHITE, (SCREEN_W//2, SCREEN_H - 50), font=Font(20)) 
        self.instruction_text = Text("Select an algorithm:", (255, 255, 100), (left_margin + button_width + 20, algo_start_y - 60), font=Font(22), center=False)  
        
        # No solution message
        self.no_solution_text = Text("No solution found for this puzzle!", (255, 100, 100), (SCREEN_W//2, SCREEN_H//2), font=Font(100))  
        
        # Algorithm info panel - positioned on the left side (simplified) 
        info_panel_x = 20
        info_panel_y = 120
        info_spacing = 50
        
        # Only show total moves and current move
        self.info_title = Text("Algorithm Info", (100, 200, 255), (info_panel_x, info_panel_y), font=Font(40), center=False)  
        self.total_moves_text = Text("Total Moves: 0", (100, 255, 100), (info_panel_x, info_panel_y + info_spacing), font=Font(30), center=False) 
        self.current_move_text = Text("Current Move: 0", (255, 200, 100), (info_panel_x, info_panel_y + info_spacing * 2), font=Font(30), center=False)  
        
    def load_level(self, level_num):
        self.map.load_level_data_from_file(level_num)
        self.ui_state = "start"  # Reset UI state when loading new level
        
        # Reset algorithm info
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        self.no_solution_timer = 0
        self.is_paused = False
        self.update_algorithm_info()
        
        # Update level text
        self.level_text.set_text(f"Level: {level_num}")
        self.algorithm_text.set_text("")
        self.status_text.set_text("Click Start to begin")

    def update_algorithm_info(self):
        """Update algorithm information display - simplified version"""
        if self.ui_state == "solving" and self.map.solving:
            # Update total moves
            total_moves = len(self.map.solution_moves) if self.map.solution_moves else 0
            self.total_moves_text.set_text(f"Total Moves: {total_moves}")
            
            # Update current move
            current_move = self.map.current_move_index if self.map.current_move_index < total_moves else total_moves
            self.current_move_text.set_text(f"Current Move: {current_move}")
        else:
            # Reset display when not solving
            self.total_moves_text.set_text("Total Moves: 0")
            self.current_move_text.set_text("Current Move: 0")

    def handle_no_solution(self):
        """Handle when no solution is found"""
        self.ui_state = "no_solution"
        self.no_solution_timer = time.time()
        self.algorithm_text.set_text(f"Algorithm: {self.map.current_algorithm} - No Solution")
        self.is_paused = False  # Reset pause state
        # Reset map solving state
        self.map.solving_failed = False  # Reset the flag to prevent repeated calls

    def reset_to_start(self):
        """Reset game to start state"""
        self.ui_state = "start"
        self.algorithm_text.set_text("")
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        self.no_solution_timer = 0
        self.is_paused = False
        self.pause_btn.set_text("Pause")
        # Reset map state
        if hasattr(self.map, 'reset'):
            self.map.reset()

    def check_offscreen(self):
        for v in self.map.vehicles:
            if v.is_target and v.is_offscreen:
                self.screen_manager.set_screen('winning')

    def update(self):
        # Handle no solution timer - FIXED: Only auto-reset if timer is active
        if self.ui_state == "no_solution" and self.no_solution_timer > 0:
            current_time = time.time()
            if current_time - self.no_solution_timer >= self.no_solution_duration:
                print("No solution timer expired, returning to start")  # Debug
                self.reset_to_start()

        # Update visible buttons (including hover state)
        visible_buttons = self.get_visible_buttons()
        for button in visible_buttons:
            button.update()

        # Only update map if not paused
        if not self.is_paused:
            self.map.update()
            self.map.update_solving()

        # FIXED: Check for solving failure
        if hasattr(self.map, 'solving_failed') and self.map.solving_failed:
            print("Map solving failed, handling no solution")  # Debug
            self.handle_no_solution()

        # Update algorithm info
        self.update_algorithm_info()

        self.check_offscreen()
        
        # Update status text based on current state
        if self.ui_state == "start":
            if getattr(self.map, 'is_solved', False):
                self.status_text.set_text("Level Complete! Click Next Level")
            else:
                self.status_text.set_text("Click Start to begin")
        elif self.ui_state == "algorithm_select":
            self.status_text.set_text("Choose solving algorithm")
        elif self.ui_state == "solving":
            if self.is_paused:
                self.status_text.set_text("Paused - Click Continue to resume")
            else:
                current_algorithm = getattr(self.map, 'current_algorithm', 'Unknown')
                self.status_text.set_text(f"Solving using {current_algorithm}...")
        elif self.ui_state == "no_solution":
            self.status_text.set_text("No solution found! Click Try Again or wait for auto-reset.")
        
        return True
    
    def draw_game_background(self, surface):
        """Draw game screen background"""
        self.draw_background(surface, "game")

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
        elif self.ui_state == "no_solution":
            visible_buttons.append(self.try_again_btn)
            
        return visible_buttons

    def get_visible_texts(self):
        """Return list of text elements that should be visible based on current UI state"""
        visible_texts = [self.level_text, self.status_text]
        
        if self.algorithm_text.text:  # Only show if algorithm is selected
            visible_texts.append(self.algorithm_text)
            
        if self.ui_state == "algorithm_select":
            visible_texts.append(self.instruction_text)
        elif self.ui_state == "no_solution":
            visible_texts.append(self.no_solution_text)
        
        # Show simplified algorithm info panel when solving, no solution, or algorithm is selected
        if self.ui_state in ["solving", "algorithm_select", "no_solution"] or (self.ui_state == "start" and self.algorithm_text.text):
            visible_texts.extend([
                self.info_title,
                self.total_moves_text,
                self.current_move_text
            ])
            
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

        # Handle hover effects for all buttons
        visible_buttons = self.get_visible_buttons()
        for button in visible_buttons:
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at {event.pos}, current UI state: {self.ui_state}")  # Debug
            
            if self.ui_state == "start":
                if self.start_btn.hit(event.pos):
                    print("Start button clicked")  # Debug
                    self.ui_state = "algorithm_select"
                    
            elif self.ui_state == "algorithm_select":
                if self.solve_bfs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("BFS")
                    self.algorithm_text.set_text("Algorithm: BFS")
                    self.ui_state = "solving"
                    self.is_paused = False
                elif self.solve_dfs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("DFS")
                    self.algorithm_text.set_text("Algorithm: DFS")
                    self.ui_state = "solving"
                    self.is_paused = False
                elif self.solve_astar.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("A*")
                    self.algorithm_text.set_text("Algorithm: A*")
                    self.ui_state = "solving"
                    self.is_paused = False
                elif self.solve_ucs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("UCS")
                    self.algorithm_text.set_text("Algorithm: UCS")
                    self.ui_state = "solving"
                    self.is_paused = False
                    
            elif self.ui_state == "solving":
                if self.reset_btn.hit(event.pos):
                    print("Reset button clicked")  # Debug
                    self.reset_to_start()
                elif self.pause_btn.hit(event.pos):
                    # FIXED: Simplified pause logic - just toggle pause state
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.pause_btn.set_text("Continue")
                        # Optionally pause the map solving process
                        if hasattr(self.map, 'pause_solving'):
                            self.map.pause_solving()
                    else:
                        self.pause_btn.set_text("Pause")
                        # Optionally resume the map solving process
                        if hasattr(self.map, 'resume_solving'):
                            self.map.resume_solving()
            
            elif self.ui_state == "no_solution":
                if self.try_again_btn.hit(event.pos):
                    print("Try Again button clicked")  # Debug
                    self.ui_state = "algorithm_select"
                    self.algorithm_text.set_text("")
                    self.algorithm_start_time = 0
                    self.current_execution_time = 0
                    self.no_solution_timer = 0  # Reset timer
                    self.is_paused = False
            
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
            # Handle hover effects for mouse motion
            visible_buttons = self.get_visible_buttons()
            for button in visible_buttons:
                button.handle_event(event)
                
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