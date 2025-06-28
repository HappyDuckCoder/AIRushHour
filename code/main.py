import pygame
import sys
from collections import deque
import copy

# Constants
MAP_N = 6
TILE = 70
SCREEN_W = 1200
SCREEN_H = 800  # Tăng chiều cao để có không gian cho animation
FPS = 60

# Offset để căn giữa game board trong màn hình
BOARD_OFFSET_X = (SCREEN_W - MAP_N * TILE) // 2
BOARD_OFFSET_Y = (SCREEN_H - MAP_N * TILE) // 2 

# ===============================
# Program
# ===============================
class Program:
    def __init__(self):
        self.game = Game()

    def run(self):
        self.game.run()

# ===============================
# Game
# ===============================
class Game:
    def __init__(self):
        pygame.init()
        # Double buffering được bật mặc định trong pygame
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF)
        pygame.display.set_caption("Rush Hour - BFS Solver")
        self.clock = pygame.time.Clock()
        
        # Load tất cả hình ảnh trước
        self.load_images()
        
        self.map = Map(self.images)
        self.search = SearchAlgorithm()
        self.solved_moves = []
        self.show_solution = False
        self.solution_speed = 0
        self.move_delay = 30  # frames between moves
        self.current_move_index = 0  # Chỉ số move hiện tại trong animation

        # Animation variables
        self.animating = False
        self.animation_progress = 0
        self.animation_speed = 0.1

        # Buttons
        self.solve_bfs_btn = Button("Solve BFS", (50, SCREEN_H - 100))
        self.solve_dfs_btn = Button("Solve DFS", (170, SCREEN_H - 100))
        self.reset_btn = Button("Reset", (290, SCREEN_H - 100))
        
        # Current algorithm being used
        self.current_algorithm = "None"

    def load_images(self):
        """Load tất cả hình ảnh cần thiết"""
        self.images = {}
        
        # Background chính
        self.images['background'] = pygame.image.load("bg.png")
        self.images['background'] = pygame.transform.scale(self.images['background'], (SCREEN_W, SCREEN_H))
        
        # Map overlay
        self.images['map'] = pygame.image.load("map.png")
        self.images['map'] = pygame.transform.scale(self.images['map'], (MAP_N * TILE, MAP_N * TILE))
        
        # Vehicle images
        # Target car (horizontal 2 tiles)
        target_img = pygame.image.load("target.png")
        self.images['target'] = pygame.transform.scale(target_img, (TILE * 2, TILE))
        
        # v2 car (horizontal 2 tiles)
        v2_img = pygame.image.load("vh2h.png")
        self.images['v2'] = pygame.transform.scale(v2_img, (TILE * 2, TILE))
        
        # v3 car - FIX: Load và scale đúng cách cho cả horizontal và vertical
        v3_img = pygame.image.load("vh3h.png")
        self.images['v3_h'] = pygame.transform.scale(v3_img, (TILE * 3, TILE))  # Horizontal
        
        # FIX: Rotate trước rồi mới scale để tránh méo hình
        v3_rotated = pygame.transform.rotate(v3_img, 90)
        self.images['v3_v'] = pygame.transform.scale(v3_rotated, (TILE, TILE * 3))  # Vertical
        
        print("All images loaded successfully!")

    def print_solution_steps(self, moves, algorithm_name):
        """In các bước giải trong terminal"""
        print("\n" + "="*60)
        print(f"{algorithm_name} SOLUTION STEPS:")
        print("="*60)
        
        if not moves:
            print("No solution found!")
            return
                    
        for i, (vid, dx, dy) in enumerate(moves, 1):
            print(f"Step {i:2d}: ({vid}, {dx:2d}, {dy:2d})")
        
        print("="*60)
        print(f"Total steps ({algorithm_name}): {len(moves)}")
        print("="*60 + "\n")

    def run(self):
        running = True
        # Tạo surface cho double buffering
        buffer_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        
        while running:
            self.clock.tick(FPS)
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if self.solve_bfs_btn.hit(e.pos):
                        print("Solving with BFS...")
                        self.current_algorithm = "BFS"
                        solution = self.search.solve_bfs(self.map.get_state())
                        if solution:
                            print(f"BFS Solution found with {len(solution)} moves!")
                            # Lưu solution và in ra terminal
                            self.solved_moves = solution.copy()  # Giữ nguyên list gốc
                            self.print_solution_steps(solution, "BFS")
                            self.show_solution = True
                            self.solution_speed = 0
                            self.current_move_index = 0  # Reset chỉ số
                        else:
                            print("No BFS solution found!")
                    elif self.solve_dfs_btn.hit(e.pos):
                        print("Solving with DFS...")
                        self.current_algorithm = "DFS"
                        solution = self.search.solve_dfs(self.map.get_state())
                        if solution:
                            print(f"DFS Solution found with {len(solution)} moves!")
                            # Lưu solution và in ra terminal
                            self.solved_moves = solution.copy()  # Giữ nguyên list gốc
                            self.print_solution_steps(solution, "DFS")
                            self.show_solution = True
                            self.solution_speed = 0
                            self.current_move_index = 0  # Reset chỉ số
                        else:
                            print("No DFS solution found!")
                    elif self.reset_btn.hit(e.pos):
                        self.map.reset()
                        self.show_solution = False
                        self.solved_moves = []
                        self.current_move_index = 0
                        self.animating = False
                        self.current_algorithm = "None"

            # REMOVED: Manual keyboard controls - only automatic solution playback
            if self.show_solution:
                # Play solution automatically with animation
                if self.solved_moves and not self.animating and self.current_move_index < len(self.solved_moves):
                    self.solution_speed += 1
                    if self.solution_speed >= self.move_delay:
                        # Lấy move hiện tại từ list (không pop)
                        move = self.solved_moves[self.current_move_index]
                        self.start_animation(move)
                        self.current_move_index += 1
                        self.solution_speed = 0
                        
                        # Nếu hết moves thì dừng animation
                        if self.current_move_index >= len(self.solved_moves):
                            self.show_solution = False

            # Update animation
            self.update_animation()

            # Vẽ tất cả lên buffer trước
            self.draw_all(buffer_surface)
            
            # Sau đó blit buffer lên screen (double buffering)
            self.screen.blit(buffer_surface, (0, 0))
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

    def start_animation(self, move):
        """Bắt đầu animation cho move"""
        self.animating = True
        self.animation_progress = 0
        self.current_move = move
        vid, dx, dy = move
        self.start_pos = (self.map.vehicles[vid].x, self.map.vehicles[vid].y)
        self.end_pos = (self.start_pos[0] + dx, self.start_pos[1] + dy)

    def update_animation(self):
        """Update animation progress"""
        if self.animating:
            self.animation_progress += self.animation_speed
            if self.animation_progress >= 1.0:
                # Animation complete
                self.animating = False
                self.animation_progress = 0
                # Apply the actual move
                self.map.apply_move(self.current_move)

    def get_animated_position(self, vid):
        """Lấy vị trí hiện tại của vehicle trong animation"""
        if self.animating and vid == self.current_move[0]:
            # Interpolate between start and end position
            progress = min(1.0, self.animation_progress)
            current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
            current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
            return (current_x, current_y)
        else:
            return (self.map.vehicles[vid].x, self.map.vehicles[vid].y)

    def draw_all(self, surface):
        """Vẽ tất cả lên surface được chỉ định"""
        # Draw background
        surface.blit(self.images['background'], (0, 0))
        
        # Draw map với animation
        self.map.draw(surface, self.get_animated_position if self.animating else None)
        
        # Draw UI
        self.solve_bfs_btn.draw(surface)
        self.solve_dfs_btn.draw(surface)
        self.reset_btn.draw(surface)
        
        # Draw instructions và game status - UPDATED instructions
        font = pygame.font.SysFont(None, 24)
        instructions = [
            "Rush Hour Puzzle Solver",
            "Click 'Solve BFS' or 'Solve DFS' to watch AI solve", 
            "Click 'Reset' to return to initial state",
            "Goal: Get RED car to exit →",
            f"Algorithm: {self.current_algorithm}",
            f"Status: {'Solving...' if self.show_solution else 'Ready to solve'}",
            f"Solved: {'YES!' if self.map.is_solved() else 'Not yet'}",
            f"Animation: {self.current_move_index}/{len(self.solved_moves)} moves" if self.show_solution else "Choose BFS (optimal) or DFS (faster search)"
        ]
        for i, text in enumerate(instructions):
            color = (255, 255, 100) if i == 0 else (255, 255, 255)
            if "Solved: YES!" in text:
                color = (100, 255, 100)
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (50, 50 + i * 25))

    # REMOVED: handle_keys method completely - no manual control

# ===============================
# Button
# ===============================
class Button:
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.font = pygame.font.SysFont(None, 28)  # Slightly smaller font
        text_surface = self.font.render(text, True, (0, 0, 0))
        button_width = max(100, text_surface.get_width() + 20)  # Dynamic width
        self.rect = pygame.Rect(pos[0], pos[1], button_width, 40)

    def draw(self, surf):
        pygame.draw.rect(surf, (100, 200, 100), self.rect)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)

# ===============================
# Vehicle
# ===============================
class Vehicle:
    def __init__(self, image_key, orientation, length, x, y, is_target=False, images=None):
        self.image_key = image_key
        self.orient = orientation  # 'h' or 'v'
        self.len = length
        self.x = x
        self.y = y
        self.is_target = is_target
        self.images = images

    def get_image(self):
        """Lấy hình ảnh phù hợp dựa trên orientation"""
        if self.image_key == 'v3':
            return self.images[f'v3_{self.orient}']
        return self.images[self.image_key]

    def positions(self):
        if self.orient == 'h':
            return [(self.x + i, self.y) for i in range(self.len)]
        else:
            return [(self.x, self.y + i) for i in range(self.len)]

    def draw(self, surf, pos_override=None):
        """Vẽ vehicle bằng hình ảnh với khả năng override position cho animation"""
        if pos_override:
            draw_x, draw_y = pos_override
        else:
            draw_x, draw_y = self.x, self.y
            
        if self.images and self.image_key in self.images:
            image = self.get_image()
            screen_x = BOARD_OFFSET_X + draw_x * TILE
            screen_y = BOARD_OFFSET_Y + draw_y * TILE
            surf.blit(image, (screen_x, screen_y))
        else:
            # Fallback drawing nếu không có hình
            for i in range(self.len):
                if self.orient == 'h':
                    tile_x, tile_y = draw_x + i, draw_y
                else:
                    tile_x, tile_y = draw_x, draw_y + i
                    
                screen_x = BOARD_OFFSET_X + tile_x * TILE
                screen_y = BOARD_OFFSET_Y + tile_y * TILE
                rect = pygame.Rect(screen_x + 2, screen_y + 2, TILE - 4, TILE - 4)
                color = (255, 100, 100) if self.is_target else (100, 100, 255)
                pygame.draw.rect(surf, color, rect)
                pygame.draw.rect(surf, (0, 0, 0), rect, 2)

    def copy(self):
        return Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.is_target, self.images)

# ===============================
# Map
# ===============================
class Map:
    def __init__(self, images):
        self.images = images
        self.initial_vehicles = []
        self.vehicles = []
        self.load_vehicles()

    def load_vehicles(self):
        """Tạo các vehicle với layout phù hợp với hình ảnh"""
        self.initial_vehicles = [
            Vehicle('target', 'h', 2, 0, 2, True, self.images),    # Target car (đỏ) - row 3
            Vehicle('v2', 'h', 2, 0, 0, False, self.images),       # Top-left horizontal
            Vehicle('v2', 'h', 2, 3, 1, False, self.images),       # Top-right horizontal  
            Vehicle('v3_v', 'v', 3, 2, 0, False, self.images),       # Center vertical
            Vehicle('v2', 'h', 2, 0, 4, False, self.images),       # Bottom-left horizontal
            Vehicle('v2', 'h', 2, 4, 3, False, self.images),       # Right vertical
        ]
        self.reset()

    def reset(self):
        self.vehicles = [v.copy() for v in self.initial_vehicles]

    def get_grid(self):
        grid = [[0] * MAP_N for _ in range(MAP_N)]
        for i, vehicle in enumerate(self.vehicles):
            for x, y in vehicle.positions():
                if 0 <= x < MAP_N and 0 <= y < MAP_N:
                    grid[y][x] = i + 1
        return grid

    def get_state(self):
        return [(v.x, v.y) for v in self.vehicles]

    def set_state(self, state):
        for i, (x, y) in enumerate(state):
            if i < len(self.vehicles):
                self.vehicles[i].x = x
                self.vehicles[i].y = y

    def is_valid_move(self, vid, dx, dy):
        if vid >= len(self.vehicles):
            return False
            
        vehicle = self.vehicles[vid]
        new_x, new_y = vehicle.x + dx, vehicle.y + dy
        
        # Check movement direction constraint
        if vehicle.orient == 'h' and dy != 0:
            return False  # Horizontal vehicles can only move left/right
        if vehicle.orient == 'v' and dx != 0:
            return False  # Vertical vehicles can only move up/down
        
        # Check if new position is within bounds
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.is_target, self.images).positions():
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False
        
        # Check for collisions with other vehicles
        grid = self.get_grid()
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.is_target, self.images).positions():
            if grid[y][x] != 0 and grid[y][x] != vid + 1:
                return False
        
        return True

    def move_vehicle(self, vid, dx, dy):
        if self.is_valid_move(vid, dx, dy):
            self.vehicles[vid].x += dx
            self.vehicles[vid].y += dy
            return True
        return False

    def apply_move(self, move):
        vid, dx, dy = move
        self.move_vehicle(vid, dx, dy)

    def draw(self, surf, pos_func=None):
        """Vẽ map và vehicles với support cho animation"""
        # Draw map overlay
        if 'map' in self.images:
            surf.blit(self.images['map'], (BOARD_OFFSET_X, BOARD_OFFSET_Y))
        else:
            # Fallback grid
            for y in range(MAP_N):
                for x in range(MAP_N):
                    screen_x = BOARD_OFFSET_X + x * TILE
                    screen_y = BOARD_OFFSET_Y + y * TILE
                    rect = pygame.Rect(screen_x, screen_y, TILE, TILE)
                    pygame.draw.rect(surf, (200, 200, 200), rect, 1)

        # Draw exit
        exit_rect = pygame.Rect(BOARD_OFFSET_X + MAP_N * TILE, BOARD_OFFSET_Y + 2 * TILE, 20, TILE)
        pygame.draw.rect(surf, (255, 200, 200), exit_rect)

        # Draw vehicles với animation support
        for i, vehicle in enumerate(self.vehicles):
            if pos_func:
                pos = pos_func(i)
                vehicle.draw(surf, pos)
            else:
                vehicle.draw(surf)

    def is_solved(self):
        # Check if target vehicle reaches the right edge
        for vehicle in self.vehicles:
            if vehicle.is_target:
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False

# ===============================
# SearchAlgorithm (BFS and DFS)
# ===============================
class SearchAlgorithm:
    def __init__(self):
        self.max_depth = 50  # Limit for DFS to prevent infinite search
    
    def solve_bfs(self, start_state):
        """Breadth-First Search - finds optimal solution"""
        queue = deque([(start_state, [])])
        visited = set()
        visited.add(tuple(tuple(pos) for pos in start_state))
        
        # Create a temporary map for testing moves
        temp_map = Map({})  # Empty images dict for temp map
        temp_map.vehicles = [v.copy() for v in temp_map.initial_vehicles]
        
        nodes_explored = 0
        
        while queue:
            current_state, path = queue.popleft()
            nodes_explored += 1
            
            # Set map to current state and check if solved
            temp_map.set_state(current_state)
            if temp_map.is_solved():
                print(f"BFS: Explored {nodes_explored} nodes, found optimal solution with {len(path)} moves")
                return path
            
            # Try all possible moves
            for vid in range(len(temp_map.vehicles)):
                vehicle = temp_map.vehicles[vid]
                
                # Determine possible move directions based on orientation
                if vehicle.orient == 'h':
                    moves = [(-1, 0), (1, 0)]  # Left, Right
                else:
                    moves = [(0, -1), (0, 1)]  # Up, Down
                
                for dx, dy in moves:
                    if temp_map.is_valid_move(vid, dx, dy):
                        # Create new state
                        new_state = [list(pos) for pos in current_state]
                        new_state[vid][0] += dx
                        new_state[vid][1] += dy
                        
                        # Convert to hashable format for visited check
                        state_key = tuple(tuple(pos) for pos in new_state)
                        
                        if state_key not in visited:
                            visited.add(state_key)
                            new_path = path + [(vid, dx, dy)]
                            queue.append((new_state, new_path))
        
        print(f"BFS: Explored {nodes_explored} nodes, no solution found")
        return []  # No solution found
    
    def solve_dfs(self, start_state):
        """Depth-First Search - may find longer solution but potentially faster"""
        visited = set()
        temp_map = Map({})  # Empty images dict for temp map
        temp_map.vehicles = [v.copy() for v in temp_map.initial_vehicles]
        
        self.nodes_explored = 0
        
        def dfs_recursive(current_state, path, depth):
            if depth > self.max_depth:
                return None
                
            self.nodes_explored += 1
            
            # Convert to hashable format for visited check
            state_key = tuple(tuple(pos) for pos in current_state)
            if state_key in visited:
                return None
                
            visited.add(state_key)
            
            # Set map to current state and check if solved
            temp_map.set_state(current_state)
            if temp_map.is_solved():
                return path
            
            # Try all possible moves
            for vid in range(len(temp_map.vehicles)):
                vehicle = temp_map.vehicles[vid]
                
                # Determine possible move directions based on orientation
                if vehicle.orient == 'h':
                    moves = [(-1, 0), (1, 0)]  # Left, Right
                else:
                    moves = [(0, -1), (0, 1)]  # Up, Down
                
                for dx, dy in moves:
                    if temp_map.is_valid_move(vid, dx, dy):
                        # Create new state
                        new_state = [list(pos) for pos in current_state]
                        new_state[vid][0] += dx
                        new_state[vid][1] += dy
                        
                        new_path = path + [(vid, dx, dy)]
                        result = dfs_recursive(new_state, new_path, depth + 1)
                        if result is not None:
                            return result
            
            visited.remove(state_key)  # Backtrack
            return None
        
        result = dfs_recursive(start_state, [], 0)
        if result:
            print(f"DFS: Explored {self.nodes_explored} nodes, found solution with {len(result)} moves")
        else:
            print(f"DFS: Explored {self.nodes_explored} nodes, no solution found (max depth: {self.max_depth})")
        return result if result else []

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    Program().run()