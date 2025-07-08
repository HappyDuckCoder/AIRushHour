from SolverAlgorithms.Solver import PuzzleSolver
from SolverAlgorithms.SolverFactory import StrategyFactory
from Game.Vehicle import Vehicle
from constants import *
import time
from Graphic.Graphic import gfx, pygame
from Resource.Resource import ResourceManager

# ===============================
# Map Class
# ===============================
class Map:
    def __init__(self, map_file_path="map.txt"):
        self.map_file_path = map_file_path
        self.initial_vehicles = []
        self.vehicles = []
        self.current_level = 1
        self.level_data = self.load_level_data_from_file()
        self.load_level(1)
        self.selected_vehicle = None
        
        self.solver = None
        self.solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_timer = 0
        self.move_delay = 0.5  # seconds between moves
        self.list_solver = []
        
        # Victory animation
        self.game_won = False
        self.victory_animation_started = False

    def load_level_data_from_file(self):
        """Load level data from map.txt file"""
        levels = {}
        
        try:
            with open(self.map_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            current_level = None
            vehicle_data = []
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check if line is a level number
                if line.isdigit():
                    # Save previous level if exists
                    if current_level is not None and vehicle_data:
                        levels[current_level] = vehicle_data
                    
                    # Start new level
                    current_level = int(line)
                    vehicle_data = []
                else:
                    # Parse vehicle data
                    vehicle = self.parse_vehicle_line(line)
                    if vehicle:
                        vehicle_data.append(vehicle)
            
            # Save last level
            if current_level is not None and vehicle_data:
                levels[current_level] = vehicle_data
                
        except FileNotFoundError:
            print(f"Map file '{self.map_file_path}' not found. Using default levels.")
            return self.create_default_level_data()
        except Exception as e:
            print(f"Error loading map file: {e}. Using default levels.")
            return self.create_default_level_data()
        
        return levels

    def parse_vehicle_line(self, line):
        """Parse a single vehicle line from the map file"""
        try:
            # Split by comma and strip whitespace
            parts = [part.strip() for part in line.split(',')]
            
            if len(parts) != 6:
                print(f"Invalid vehicle line format: {line}")
                return None
            
            name = parts[0]
            orient = parts[1]
            length = int(parts[2])
            x = int(parts[3])
            y = int(parts[4])
            image_key = parts[5]
            
            # Validate orientation
            if orient not in ['h', 'v']:
                print(f"Invalid orientation '{orient}' for vehicle {name}")
                return None
            
            # Create and return vehicle
            return Vehicle(name, orient, length, x, y, image_key)
            
        except ValueError as e:
            print(f"Error parsing vehicle line '{line}': {e}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing vehicle line '{line}': {e}")
            return None

    def create_default_level_data(self):
        """Create default level configurations (fallback)"""
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

    def reload_map_file(self):
        """Reload the map file and update levels"""
        self.level_data = self.load_level_data_from_file()
        if self.current_level in self.level_data:
            self.load_level(self.current_level)
        else:
            # If current level doesn't exist, load level 1
            if 1 in self.level_data:
                self.load_level(1)
            else:
                print("No valid levels found in map file!")

    def get_available_levels(self):
        """Get list of available levels"""
        return sorted(self.level_data.keys())

    def load_level(self, level_num):
        """Load a specific level"""
        if level_num in self.level_data:
            self.current_level = level_num
            self.initial_vehicles = self.level_data[level_num]
            self.reset()
            print(f"Level {level_num} loaded successfully!")
        else:
            print(f"Level {level_num} not found!")

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

    def update(self):
        """Update game state - OPTIMIZED"""
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

            # Chọn chiến lược phù hợp
            if nameAlgo.lower() == "dfs":
                strategy = StrategyFactory.create_dfs(self)
            elif nameAlgo.lower() == "bfs":
                strategy = StrategyFactory.create_bfs(self)
            elif nameAlgo.lower() == "ucs":
                strategy = StrategyFactory.create_ucs(self)
            else:
                print(f"Unknown algorithm: {nameAlgo}")
                return
            
            self.reset_victory_animation()

            self.solver = PuzzleSolver(self, strategy) 
            solution = self.solver.solve()

            if solution:
                print(f"Solution found with {len(solution)} moves!")
                self.solution_moves = solution
                self.current_move_index = 0
                self.solving = True
                self.move_timer = time.time()
                
                self.list_solver = solution
                self.print_solution(solution)
            else:
                print("No solution found!")

    def print_solution(self, solution):
        """In ra các bước giải"""
        for i, move in enumerate(solution):
            print(f"Move {i+1}: ({move['name']}, {move['dx']}, {move['dy']})")

    def update_solving(self):
        """Cập nhật quá trình giải puzzle tự động"""
        if self.solving and self.solution_moves:
            current_time = time.time()
            if current_time - self.move_timer >= self.move_delay:
                if self.current_move_index < len(self.solution_moves):
                    move = self.solution_moves[self.current_move_index]
                    
                    # Extract move information from the dictionary format
                    vehicle_index = move['index']
                    dx = move['dx']
                    dy = move['dy']
                    
                    # Apply the move
                    self.vehicles[vehicle_index].x += dx
                    self.vehicles[vehicle_index].y += dy
                                        
                    self.current_move_index += 1
                    self.move_timer = current_time
                else:
                    # Solving complete
                    self.solving = False

                    for vehicle in self.vehicles:
                        if vehicle.is_target:
                            vehicle.play_victory_animation()

                    print("Solving complete!")
        elif self.solving and not self.solution_moves:
            # No solution found
            self.solving = False
            
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
        exit_rect = pygame.Rect(
            BOARD_OFFSET_X + MAP_N * TILE, 
            BOARD_OFFSET_Y + 2 * TILE, 
            20, 
            TILE
        )
        pygame.draw.rect(surface, (255, 200, 200), exit_rect)

    def draw_all_vehicles(self, surface):
        """Vẽ tất cả vehicles"""
        for vehicle in self.vehicles:
            vehicle.draw(surface)

    def draw(self, surf):
        """Vẽ toàn bộ map"""
        self.draw_map_overlay(surf)
        self.draw_exit(surf)
        self.draw_all_vehicles(surf)

    def print_current_level_info(self):
        """In thông tin về level hiện tại"""
        print(f"Current Level: {self.current_level}")
        print(f"Number of vehicles: {len(self.vehicles)}")
        for i, vehicle in enumerate(self.vehicles):
            print(f"  Vehicle {i+1}: {vehicle.name} ({vehicle.orient}, {vehicle.len}) at ({vehicle.x}, {vehicle.y}) - Image: {vehicle.image_key}")

    def save_current_level_to_file(self, filename):
        """Lưu level hiện tại ra file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"{self.current_level}\n")
                for vehicle in self.vehicles:
                    file.write(f"{vehicle.name}, {vehicle.orient}, {vehicle.len}, {vehicle.x}, {vehicle.y}, {vehicle.image_key}\n")
            print(f"Level {self.current_level} saved to {filename}")
        except Exception as e:
            print(f"Error saving level to file: {e}")