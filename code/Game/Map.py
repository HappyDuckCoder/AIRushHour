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
        self.move_delay = 0.5  # seconds between moves
        self.list_solver = []

    def create_level_data(self):
        """Create 2 different level configurations"""
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

    def reset(self):
        self.vehicles = [v.copy() for v in self.initial_vehicles]
        self.selected_vehicle = None
        self.solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_timer = 0

    def start_solving(self, nameAlgo: str):
        if not self.solving:
            print(f"Starting {nameAlgo} solver...")

            # Chọn chiến lược phù hợp
            if nameAlgo.lower() == "dfs":
                strategy = StrategyFactory.create_dfs(self)
            elif nameAlgo.lower() == "bfs":
                strategy = StrategyFactory.create_bfs(self)
            else:
                print(f"Unknown algorithm: {nameAlgo}")
                return
            
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
        for move in solution:
            print(f"Move: {move}")

    def update_solving(self):
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
                    print("Solving complete!")
        elif self.solving and not self.solution_moves:
            # No solution found
            self.solving = False
            print("No solution found!")

    def get_grid(self):
        grid = [[0] * MAP_N for _ in range(MAP_N)]
        for i, vehicle in enumerate(self.vehicles):
            for x, y in vehicle.positions():
                if 0 <= x < MAP_N and 0 <= y < MAP_N:
                    grid[y][x] = i + 1
        return grid

    def is_valid_move(self, vehicle, new_x, new_y):
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
        if self.selected_vehicle:
            self.selected_vehicle.dragging = False
            self.selected_vehicle = None

    def handle_mouse_motion(self, pos):
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
        """Draw map overlay"""
        map_image = ResourceManager().get_image('map')
        if map_image:
            surface.blit(map_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    def draw_exit(self, surface):
        """Draw exit area"""
        exit_rect = pygame.Rect(
            BOARD_OFFSET_X + MAP_N * TILE, 
            BOARD_OFFSET_Y + 2 * TILE, 
            20, 
            TILE
        )
        pygame.draw.rect(surface, (255, 200, 200), exit_rect)

    def get_vehicle_image(self, vehicle):
        """Get appropriate image for vehicle"""
        if vehicle.image_key.startswith('v2'):
            return self.images.get(f'v2_{vehicle.orient}')
        elif vehicle.image_key.startswith('v3'):
            return self.images.get(f'v3_{vehicle.orient}')
        return self.images.get(vehicle.image_key)

    def draw_all_vehicles(self, surface, vehicles):
        """Draw all vehicles"""
        for vehicle in vehicles:
            vehicle.draw(surface)

    def draw(self, surf):
        self.draw_map_overlay(surf)
        self.draw_exit(surf)
        self.draw_all_vehicles(surf, self.vehicles)

    def is_solved(self):
        for vehicle in self.vehicles:
            if vehicle.is_target:
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False