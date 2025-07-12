from Screen.BaseScreen import Screen
from Game.Map import Map
from UI.Button import Button
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
import time
from constants import *
import pygame


class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.map = Map()
        self.is_paused = False
        
        self.ui_state = "start"  
        
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        
        self.no_solution_timer = 0
        self.no_solution_duration = 3.0  
        
        self.audio_manager = AudioManager()
        
        self.previous_move_index = 0
        self.previous_solving_state = False
        
        button_width = 140
        button_height = 45
        button_spacing = 15

        top_margin = 20
        self.back_btn = Button("Back", (20, top_margin), button_width, button_height)
        self.menu_btn = Button("Main Menu", (180, top_margin), button_width, button_height, GRAY)
        
        right_margin = 20
        self.next_level_btn = Button("Next Level", (SCREEN_W - button_width - right_margin, top_margin), button_width, button_height, GREEN)
        
        bottom_margin = 20
        left_margin = 20
        
        self.start_btn = Button("Start", (left_margin, SCREEN_H - button_height - bottom_margin), button_width, button_height, GREEN)
        
        algo_start_y = SCREEN_H - bottom_margin - button_height
        self.solve_bfs = Button("BFS", (left_margin, algo_start_y - (button_height + button_spacing) * 3), button_width, button_height, BLUE)
        self.solve_dfs = Button("DFS", (left_margin, algo_start_y - (button_height + button_spacing) * 2), button_width, button_height, ORANGE)
        self.solve_astar = Button("A*", (left_margin, algo_start_y - (button_height + button_spacing) * 1), button_width, button_height, PURPLE)
        self.solve_ucs = Button("UCS", (left_margin, algo_start_y), button_width, button_height, PINK)
        
        self.reset_btn = Button("Reset", (left_margin, algo_start_y - (button_height + button_spacing) * 1), button_width, button_height, RED)
        self.pause_btn = Button("Pause", (left_margin, algo_start_y), button_width, button_height, RED)
        
        self.try_again_btn = Button("Try Again", (left_margin, algo_start_y), button_width, button_height, ORANGE)
        
        self.all_buttons = [
            self.back_btn, self.menu_btn, self.next_level_btn,
            self.start_btn, self.solve_bfs, self.solve_dfs, self.solve_astar,
            self.solve_ucs, self.reset_btn, self.pause_btn, self.try_again_btn
        ]
        
        self.level_text = Text("Level: 1", WHITE, (SCREEN_W//2, 30), font=Font(32)) 
        self.algorithm_text = Text("", WHITE, (SCREEN_W//2, 70), font=Font(24))  
        self.status_text = Text("Click Start to begin", WHITE, (SCREEN_W//2, SCREEN_H - 50), font=Font(20)) 
        self.instruction_text = Text("Select an algorithm:", (255, 255, 100), (left_margin + button_width + 20, algo_start_y - 60), font=Font(22), center=False)  
        
        self.no_solution_text = Text("No solution found for this puzzle!", (255, 100, 100), (SCREEN_W//2, SCREEN_H//2), font=Font(100))  
        
        info_panel_x = 20
        info_panel_y = 120
        info_spacing = 50
        
        self.info_title = Text("Algorithm Info", (100, 200, 255), (info_panel_x, info_panel_y), font=Font(40), center=False)  
        self.total_moves_text = Text("Total Moves: 0", (100, 255, 100), (info_panel_x, info_panel_y + info_spacing), font=Font(30), center=False) 
        self.current_move_text = Text("Current Move: 0", (255, 200, 100), (info_panel_x, info_panel_y + info_spacing * 2), font=Font(30), center=False)
        self.nodes_expanded_text = Text("Nodes Expanded: 0", (200, 150, 255), (info_panel_x, info_panel_y + info_spacing * 3), font=Font(30), center=False)  
        self.total_cost_text = Text("Total Cost (g(n)): 0", (255, 150, 200), (info_panel_x, info_panel_y + info_spacing * 4), font=Font(30), center=False)  

        
    def load_level(self, level_num):
        self.map.load_level_data_from_file(level_num)
        self.ui_state = "start"  
        
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        self.no_solution_timer = 0
        self.is_paused = False
        
        self.previous_move_index = 0
        self.previous_solving_state = False
        
        self.update_algorithm_info()
        
        self.level_text.set_text(f"Level: {level_num}")
        self.algorithm_text.set_text("")
        self.status_text.set_text("Click Start to begin")

    def update_algorithm_info(self):
        if self.ui_state == "solving" and self.map.solving:
            total_moves = len(self.map.solution_moves) if self.map.solution_moves else 0
            self.total_moves_text.set_text(f"Total Moves: {total_moves}")
            
            current_move = self.map.current_move_index if self.map.current_move_index < total_moves else total_moves
            self.current_move_text.set_text(f"Current Move: {current_move}")

            nodes_expanded = self.map.nodes_expanded if self.map.nodes_expanded else 0
            self.nodes_expanded_text.set_text(f"Nodes Expanded: {nodes_expanded}")

            total_cost = self.map.total_cost if self.map.total_cost else 0
            self.total_cost_text.set_text(f"Total Cost (g(n)): {total_cost}")
        else:
            self.total_moves_text.set_text("Total Moves: 0")
            self.current_move_text.set_text("Current Move: 0")
            self.nodes_expanded_text.set_text("Nodes Expanded: 0")
            self.total_cost_text.set_text("Total Cost (g(n)): 0")

    def check_and_play_move_sound(self):
        if self.ui_state == "solving" and self.map.solving and not self.is_paused:
            current_move_index = getattr(self.map, 'current_move_index', 0)
            if current_move_index != self.previous_move_index:
                self.audio_manager.play_car_move()
                self.previous_move_index = current_move_index
            
            if not self.previous_solving_state and self.map.solving:
                self.audio_manager.play_car_move()
            
            self.previous_solving_state = self.map.solving
        elif self.ui_state == "start":
            self.previous_move_index = 0
            self.previous_solving_state = False

    def handle_no_solution(self):
        self.ui_state = "no_solution"
        self.no_solution_timer = time.time()
        self.algorithm_text.set_text(f"Algorithm: {self.map.current_algorithm} - No Solution")
        self.is_paused = False 
        self.map.solving_failed = False  

    def reset_to_start(self):
        self.ui_state = "start"
        self.algorithm_text.set_text("")
        self.algorithm_start_time = 0
        self.current_execution_time = 0
        self.no_solution_timer = 0
        self.is_paused = False
        self.pause_btn.set_text("Pause")
        
        self.previous_move_index = 0
        self.previous_solving_state = False
        
        if hasattr(self.map, 'reset'):
            self.map.reset()

    def check_offscreen(self):
        for v in self.map.vehicles:
            if v.is_target and v.is_offscreen:
                self.screen_manager.set_screen('winning')

    def update(self):
        if self.ui_state == "no_solution" and self.no_solution_timer > 0:
            current_time = time.time()
            if current_time - self.no_solution_timer >= self.no_solution_duration:
                print("No solution timer expired, returning to start")  
                self.reset_to_start()

        visible_buttons = self.get_visible_buttons()
        for button in visible_buttons:
            button.update()

        if not self.is_paused:
            self.map.update()
            self.map.update_solving()

        self.check_and_play_move_sound()

        if hasattr(self.map, 'solving_failed') and self.map.solving_failed:
            print("Map solving failed, handling no solution")  
            self.handle_no_solution()

        self.update_algorithm_info()

        self.check_offscreen()
        
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
        visible_texts = [self.level_text, self.status_text] 
            
        if self.ui_state == "algorithm_select":
            visible_texts.append(self.instruction_text) 
        elif self.ui_state == "no_solution":
            visible_texts.append(self.no_solution_text) 
        elif self.ui_state in ["solving", "algorithm_select", "no_solution"]: 
            visible_texts.extend([
                self.info_title,
                self.total_moves_text,
                self.current_move_text,
                self.nodes_expanded_text,
                self.total_cost_text,
            ])
            
        return visible_texts

    def draw_game_screen(self, surface, buttons, texts):
        """Draw complete game screen"""
        self.draw_game_background(surface)
        
        self.map.draw(surface)
        
        for button in buttons:
            button.draw(surface)
            
        for text in texts:
            text.draw(surface)

    def draw(self, surface):
        visible_buttons = self.get_visible_buttons()
        visible_texts = self.get_visible_texts()
        self.draw_game_screen(surface, visible_buttons, visible_texts)

    def handle_event(self, event):
        AudioManager().play_background_music('game', fade_in=False)

        visible_buttons = self.get_visible_buttons()
        for button in visible_buttons:
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:            
            if self.ui_state == "start":
                if self.start_btn.hit(event.pos):
                    self.ui_state = "algorithm_select"
            elif self.ui_state == "algorithm_select":
                if self.solve_bfs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("BFS")
                    self.algorithm_text.set_text("Algorithm: BFS")
                    self.ui_state = "solving"
                    self.is_paused = False
                    self.previous_move_index = 0
                    self.previous_solving_state = False
                elif self.solve_dfs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("DFS")
                    self.algorithm_text.set_text("Algorithm: DFS")
                    self.ui_state = "solving"
                    self.is_paused = False
                    self.previous_move_index = 0
                    self.previous_solving_state = False
                elif self.solve_astar.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("A*")
                    self.algorithm_text.set_text("Algorithm: A*")
                    self.ui_state = "solving"
                    self.is_paused = False
                    self.previous_move_index = 0
                    self.previous_solving_state = False
                elif self.solve_ucs.hit(event.pos):
                    self.algorithm_start_time = time.time()
                    self.map.start_solving("UCS")
                    self.algorithm_text.set_text("Algorithm: UCS")
                    self.ui_state = "solving"
                    self.is_paused = False
                    self.previous_move_index = 0
                    self.previous_solving_state = False                 
            elif self.ui_state == "solving":
                if self.reset_btn.hit(event.pos):
                    self.reset_to_start()
                elif self.pause_btn.hit(event.pos):
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.pause_btn.set_text("Continue")
                        if hasattr(self.map, 'pause_solving'):
                            self.map.pause_solving()
                    else:
                        self.pause_btn.set_text("Pause")
                        if hasattr(self.map, 'resume_solving'):
                            self.map.resume_solving()  
            elif self.ui_state == "no_solution":
                if self.try_again_btn.hit(event.pos):
                    self.ui_state = "algorithm_select"
                    self.algorithm_text.set_text("")
                    self.algorithm_start_time = 0
                    self.current_execution_time = 0
                    self.no_solution_timer = 0  
                    self.is_paused = False
                    self.previous_move_index = 0
                    self.previous_solving_state = False
            
            if self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('level_select')
            elif self.next_level_btn.hit(event.pos):
                self.next_level()
            elif self.menu_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            else:
                if self.ui_state == "start":
                    old_positions = {}
                    if hasattr(self.map, 'vehicles'):
                        for vehicle in self.map.vehicles:
                            old_positions[id(vehicle)] = (vehicle.x, vehicle.y)
                    
                    self.map.handle_mouse_down(event.pos)
                    
                    if hasattr(self.map, 'vehicles'):
                        for vehicle in self.map.vehicles:
                            vehicle_id = id(vehicle)
                            if vehicle_id in old_positions:
                                old_x, old_y = old_positions[vehicle_id]
                                if vehicle.x != old_x or vehicle.y != old_y:
                                    self.audio_manager.play_car_move()
                                    break
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.ui_state == "start":
                old_positions = {}
                if hasattr(self.map, 'vehicles'):
                    for vehicle in self.map.vehicles:
                        old_positions[id(vehicle)] = (vehicle.x, vehicle.y)
                
                self.map.handle_mouse_up(event.pos)
                
                if hasattr(self.map, 'vehicles'):
                    for vehicle in self.map.vehicles:
                        vehicle_id = id(vehicle)
                        if vehicle_id in old_positions:
                            old_x, old_y = old_positions[vehicle_id]
                            if vehicle.x != old_x or vehicle.y != old_y:
                                self.audio_manager.play_car_move()
                                break
                                
        elif event.type == pygame.MOUSEMOTION:
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