from SolverAlgorithms.Solver import PuzzleSolver
from SolverAlgorithms.SolverFactory import StrategyFactory
from Game.Vehicle import Vehicle
from constants import *
import time
import json
import os
from Graphic.Graphic import gfx, pygame
from Resource.Resource import ResourceManager
from typing import Dict

# ===============================
# Map Class
# ===============================
class Map:
    def __init__(self):
        self.initial_vehicles = []
        self.vehicles = []
        self.current_level = 1
        self.level_data = self.create_level_data()
        self.load_level(1)
        self.selected_vehicle = None
        
        self.solver = None
        self.solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_timer = 0
        self.move_delay = 0.5  
        self.list_solver = []
        self.current_algorithm = ""
        
        # Statistics tracking
        self.solve_start_time = 0
        self.current_algorithm = ""
        self.nodes_expanded = 0
        
        # Victory animation
        self.game_won = False
        self.victory_animation_started = False

        self.solving_failed = False

    def create_level_data(self): # for testing
        """Create 2 different level for testing"""
        levels = {
            1: [
                Vehicle('target', 'h', 2, 0, 2, 'A'),
                Vehicle('v2', 'h', 2, 0, 0, 'B'),
                Vehicle('v2', 'h', 2, 3, 1, 'C'),
                Vehicle('v3', 'v', 3, 2, 0, 'D'),
                Vehicle('v2', 'h', 2, 0, 4, 'E'),
                Vehicle('v2', 'v', 2, 4, 3, 'F'),
            ],
            2: [
                Vehicle('target', 'h', 2, 1, 2, 'A'),
                Vehicle('v2', 'v', 2, 0, 0, 'B'),
                Vehicle('v3', 'h', 3, 2, 0, 'C'),
                Vehicle('v2', 'v', 2, 3, 1, 'D'),
                Vehicle('v2', 'h', 2, 1, 4, 'E'),
            ],
        }
        return levels

    def load_level(self, level_num):
        """Load a specific level"""
        if level_num in self.level_data:
            self.current_level = level_num
            self.initial_vehicles = self.level_data[level_num]
            self.reset()

    def load_level_data_from_file(self, level_num):
        if level_num in range(NUMBER_OF_MAP + 1): 
            self.current_level = level_num

            name_map = f"{level_num}.txt"
            base_path = os.path.dirname(os.path.dirname(__file__))  # từ Game/ đi lên code/
            map_folder = os.path.join(base_path, 'Map')             # code/Map/
            full_path = os.path.join(map_folder, name_map)          # code/Map/1.txt

            vehicles = []

            with open(full_path, 'r', encoding='utf-8') as f:
                for line in f:
                    image_key, direction, length, row, col, name = line.strip().split()
                    vehicle = Vehicle(image_key, direction, int(length), int(row), int(col), name)
                    vehicles.append(vehicle)

            self.initial_vehicles = vehicles

            self.reset()

    def reset(self):
        """Reset game state"""
        self.vehicles = [v.copy() for v in self.initial_vehicles]
        self.selected_vehicle = None
        self.solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_timer = 0
        self.game_won = False
        self.victory_animation_started = False

        self.current_algorithm = ""
        
        # Reset statistics
        self.solve_start_time = 0
        self.current_algorithm = ""
        self.nodes_expanded = 0

    def update(self):
        """Update game state"""
        # Chỉ cập nhật solving animation khi đang solving
        if self.solving:
            self.update_solving()
        
        # Chỉ cập nhật vehicles khi cần thiết
        for vehicle in self.vehicles:
            if vehicle.is_target or vehicle.dragging:
                vehicle.update()

    def reset_victory_animation(self):
        # reset victory animation
        for vehicle in self.vehicles:
            if vehicle.is_target:
                vehicle.victory_animation_played = False
                for character in vehicle.characters:
                    character.is_performing_skill = False

    def start_solving(self, nameAlgo: str):
        """Bắt đầu giải puzzle"""
        if not self.solving:
            print(f"Starting {nameAlgo} solver...")
            self.current_algorithm = nameAlgo

            # Track solving start time and algorithm
            self.solve_start_time = time.time()
            self.current_algorithm = nameAlgo
            self.nodes_expanded = 0

            strategy = StrategyFactory.create_strategy(nameAlgo, self)
            
            self.reset_victory_animation()

            self.solver = PuzzleSolver(self, strategy) 
            
            # Initialize expanded_nodes list in solver for tracking
            if not hasattr(self.solver, 'expanded_nodes'):
                self.solver.expanded_nodes = []
            
            solution = self.solver.solve()

            if solution:
                self.solution_moves = solution
                self.current_move_index = 0
                self.solving = True
                self.move_timer = time.time()
                
                print(f"Solution found with {len(solution)} moves!")

                self.list_solver = solution
                self.print_solution(solution)
            else:
                print("No solution found!")
                self.save_statistics(0, False)  # Save with 0 moves, no solution

    def print_solution(self, solution):
        """In ra các bước giải"""
        # for i, move in enumerate(solution):
        #     print(f"Move {i+1}: ({move['name']}, {move['dx']}, {move['dy']})")

        for move in solution:
            print(move)

    def save_statistics(self, solution_length, solved=True):
        """Lưu thống kê vào file"""
        solve_time = time.time() - self.solve_start_time
        
        # Get nodes expanded from solver if available
        if self.solver and hasattr(self.solver, 'nodes_expanded'):
            self.nodes_expanded = self.solver.nodes_expanded
        
        statistics = {
            'level': self.current_level,
            'algorithm': self.current_algorithm,
            'time_executed': solve_time,
            'nodes_expanded': self.nodes_expanded,
            'solution_length': solution_length,
            'solved': solved,
            'timestamp': time.time()
        }
        
        # Ensure directory exists
        base_path = os.path.dirname(os.path.dirname(__file__))
        stats_file = os.path.join(base_path, 'statistic.txt')
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(statistics, f, indent=2)
            print(f"Statistics saved: {statistics}")
        except Exception as e:
            print(f"Error saving statistics: {e}")

    def update_solving(self):
        """Cập nhật quá trình giải puzzle tự động"""
        if self.solving and self.solution_moves:
            current_time = time.time()
            if current_time - self.move_timer >= self.move_delay:
                if self.current_move_index < len(self.solution_moves):
                    move = self.solution_moves[self.current_move_index]
                    
                    # Extract move information from the dictionary format

                    # move = {
                    #     'name': move_name,
                    #     'index': vehicle_index,
                    #     'dx': dx,
                    #     'dy': dy
                    # }
                
                    if isinstance(move, Dict):
                        vehicle_index = move['index']
                        dx = move['dx']
                        dy = move['dy']
                        
                        # Apply the move
                        self.vehicles[vehicle_index].x += dx
                        self.vehicles[vehicle_index].y += dy
                        
                        self.current_move_index += 1
                        self.move_timer = current_time

                    else:
                        # dạng tuple ('A', dx, dy)
                        vehicle_name, dx, dy = move

                        # tìm index của xe theo tên
                        for idx, v in enumerate(self.vehicles):
                            if v.name == vehicle_name:
                                v.x += dx
                                v.y += dy
                                break

                        self.current_move_index += 1
                        self.move_timer = current_time

                else:
                    # Solving complete
                    self.solving = False
                    
                    # Save statistics when solving is complete
                    self.save_statistics(len(self.solution_moves), True)

                    for vehicle in self.vehicles:
                        if vehicle.is_target:
                            vehicle.play_victory_animation()

                    print("Solving complete!")
        elif self.solving and not self.solution_moves:
            # No solution found
            self.solving_failed = True
            self.solving = False

            self.save_statistics(0, False)
            print("No solution found!")

    def get_grid(self):
        """Lấy grid hiện tại"""
        grid = [[0] * MAP_N for _ in range(MAP_N)]
        for i, vehicle in enumerate(self.vehicles):
            for x, y in vehicle.positions():
                if 0 <= x < MAP_N and 0 <= y < MAP_N:
                    grid[y][x] = i + 1
        return grid

    def is_valid_move(self, vehicle, new_x, new_y):
        """Kiểm tra xem nước đi có hợp lệ không"""
        # Check bounds
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.name).positions():
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False
        
        # Check collisions
        grid = self.get_grid()
        vehicle_index = self.vehicles.index(vehicle)
        
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.name).positions():
            if grid[y][x] != 0 and grid[y][x] != vehicle_index + 1:
                return False
        
        return True

    def handle_pause(self):
        self.solving = not self.solving
        return False  

    def handle_mouse_down(self, pos):
        """Xử lý click chuột"""
        if self.solving:
            return  # Don't allow manual moves while solving
            
        for vehicle in self.vehicles:
            if vehicle.contains_point(pos[0], pos[1]):
                self.selected_vehicle = vehicle
                vehicle.dragging = True
                board_x = (pos[0] - BOARD_OFFSET_X) // TILE
                board_y = (pos[1] - BOARD_OFFSET_Y) // TILE
                vehicle.drag_offset_x = board_x - vehicle.x
                vehicle.drag_offset_y = board_y - vehicle.y
                break

    def handle_mouse_up(self, pos):
        """Xử lý thả chuột"""
        if self.selected_vehicle:
            self.selected_vehicle.dragging = False
            self.selected_vehicle.reset_movement_state()
            self.selected_vehicle = None

    def handle_mouse_motion(self, pos):
        """Xử lý di chuyển chuột"""
        if self.solving:
            return  # Don't allow manual moves while solving
            
        if self.selected_vehicle and self.selected_vehicle.dragging:
            board_x = (pos[0] - BOARD_OFFSET_X) // TILE
            board_y = (pos[1] - BOARD_OFFSET_Y) // TILE
            
            new_x = board_x - self.selected_vehicle.drag_offset_x
            new_y = board_y - self.selected_vehicle.drag_offset_y
            
            # Constrain movement based on orientation
            if self.selected_vehicle.orient == 'h':
                new_y = self.selected_vehicle.y
            else:
                new_x = self.selected_vehicle.x
            
            if self.is_valid_move(self.selected_vehicle, new_x, new_y):
                self.selected_vehicle.x = new_x
                self.selected_vehicle.y = new_y
        
    def draw_map_overlay(self, surface):
        """Vẽ overlay của map"""
        map_image = ResourceManager().get_image('map')
        if map_image:
            surface.blit(map_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    def draw_exit(self, surface):
        """Vẽ vùng exit"""
        exit_image = ResourceManager().get_image('exit')
        if exit_image:
            for i in range(5):  # vẽ 5 lần
                x = BOARD_OFFSET_X + (MAP_N + i) * TILE  # MAP_N là cột bắt đầu
                y = BOARD_OFFSET_Y + 2 * TILE  # hàng cố định (hàng 2)
                surface.blit(exit_image, (x, y))

    def draw_all_vehicles(self, surface):
        """Vẽ tất cả vehicles"""
        for vehicle in self.vehicles:
            vehicle.draw(surface)

    def draw(self, surf):
        """Vẽ toàn bộ map"""
        self.draw_map_overlay(surf)
        self.draw_exit(surf)
        self.draw_all_vehicles(surf)