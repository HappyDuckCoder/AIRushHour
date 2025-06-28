import pygame
import sys
from collections import deque
import time

# Constants
MAP_N = 6
TILE = 70
SCREEN_W = 1200
SCREEN_H = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 200, 100)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Offset để căn giữa game board trong màn hình
BOARD_OFFSET_X = (SCREEN_W - MAP_N * TILE) // 2
BOARD_OFFSET_Y = (SCREEN_H - MAP_N * TILE) // 2

# ===============================
# Vehicle Class
# ===============================
class Vehicle:
    def __init__(self, image_key, orientation, length, x, y, is_target=False, images=None):
        self.image_key = image_key
        self.orient = orientation
        self.len = length
        self.x = x
        self.y = y
        self.is_target = is_target
        self.images = images
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def get_image(self):
        if self.images:
            if self.image_key.startswith('v2'):
                return self.images.get(f'v2_{self.orient}')
            elif self.image_key.startswith('v3'):
                return self.images.get(f'v3_{self.orient}')
            return self.images.get(self.image_key)
        return None

    def positions(self):
        if self.orient == 'h':
            return [(self.x + i, self.y) for i in range(self.len)]
        else:
            return [(self.x, self.y + i) for i in range(self.len)]

    def contains_point(self, mouse_x, mouse_y):
        board_x = (mouse_x - BOARD_OFFSET_X) // TILE
        board_y = (mouse_y - BOARD_OFFSET_Y) // TILE
        return (board_x, board_y) in self.positions()

    def draw(self, surf, pos_override=None):
        if pos_override:
            draw_x, draw_y = pos_override
        else:
            draw_x, draw_y = self.x, self.y
            
        image = self.get_image()
        if image:
            screen_x = BOARD_OFFSET_X + draw_x * TILE
            screen_y = BOARD_OFFSET_Y + draw_y * TILE
            surf.blit(image, (screen_x, screen_y))

    def copy(self):
        return Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.is_target, self.images)

# ===============================
# DFS Solver
# ===============================
class DFSSolver:
    def __init__(self, map_obj):
        self.map = map_obj
        self.visited = set()
        self.solution = []
        
    def get_state_key(self, vehicles):
        """Create a unique key for the current state"""
        return tuple((v.x, v.y) for v in vehicles)
    
    def is_solved(self, vehicles):
        """Check if the puzzle is solved"""
        for vehicle in vehicles:
            if vehicle.is_target:
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False
    
    def get_possible_moves(self, vehicles):
        """Get all possible moves for current state"""
        moves = []
        
        for i, vehicle in enumerate(vehicles):
            if vehicle.orient == 'h':
                # Try moving left
                for new_x in range(vehicle.x - 1, -1, -1):
                    if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                        moves.append((i, new_x - vehicle.x, 0))
                    else:
                        break
                
                # Try moving right
                for new_x in range(vehicle.x + 1, MAP_N):
                    if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                        moves.append((i, new_x - vehicle.x, 0))
                    else:
                        break
            else:  # vertical
                # Try moving up
                for new_y in range(vehicle.y - 1, -1, -1):
                    if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                        moves.append((i, 0, new_y - vehicle.y))
                    else:
                        break
                
                # Try moving down
                for new_y in range(vehicle.y + 1, MAP_N):
                    if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                        moves.append((i, 0, new_y - vehicle.y))
                    else:
                        break
        
        return moves
    
    def is_valid_move_for_state(self, vehicles, vehicle_index, new_x, new_y):
        """Check if a move is valid for given state"""
        vehicle = vehicles[vehicle_index]
        
        # Check bounds
        test_positions = []
        if vehicle.orient == 'h':
            test_positions = [(new_x + i, new_y) for i in range(vehicle.len)]
        else:
            test_positions = [(new_x, new_y + i) for i in range(vehicle.len)]
        
        for x, y in test_positions:
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False
        
        # Check collisions with other vehicles
        for j, other_vehicle in enumerate(vehicles):
            if j == vehicle_index:
                continue
            
            other_positions = set(other_vehicle.positions())
            if any(pos in other_positions for pos in test_positions):
                return False
        
        return True
    
    def apply_move(self, vehicles, move):
        """Apply a move to the vehicles and return new state"""
        new_vehicles = [v.copy() for v in vehicles]
        vehicle_index, dx, dy = move
        new_vehicles[vehicle_index].x += dx
        new_vehicles[vehicle_index].y += dy
        return new_vehicles
    
    def dfs(self, vehicles, path, depth=0, max_depth=50):
        """DFS search for solution"""
        if depth > max_depth:
            return False
            
        state_key = self.get_state_key(vehicles)
        if state_key in self.visited:
            return False
        
        self.visited.add(state_key)
        
        if self.is_solved(vehicles):
            self.solution = path[:]
            return True
        
        moves = self.get_possible_moves(vehicles)
        
        for move in moves:
            new_vehicles = self.apply_move(vehicles, move)
            path.append(move)
            
            if self.dfs(new_vehicles, path, depth + 1, max_depth):
                return True
            
            path.pop()
        
        return False
    
    def solve(self):
        """Solve the puzzle and return list of moves"""
        self.visited.clear()
        self.solution.clear()
        
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        
        if self.dfs(initial_vehicles, [], 0, 50):
            return self.solution
        else:
            return None

# ===============================
# Map Class
# ===============================
class Map:
    def __init__(self, images):
        self.images = images
        self.initial_vehicles = []
        self.vehicles = []
        self.current_level = 1
        self.level_data = self.create_level_data()
        self.load_level(1)
        self.selected_vehicle = None
        self.solver = DFSSolver(self)
        self.solving = False
        self.solution_moves = []
        self.current_move_index = 0
        self.move_timer = 0
        self.move_delay = 0.5  # seconds between moves

    def create_level_data(self):
        """Create 2 different level configurations"""
        levels = {
            1: [  # Level 1
                Vehicle('target', 'h', 2, 0, 2, True, self.images),    
                Vehicle('v2', 'h', 2, 0, 0, False, self.images),       
                Vehicle('v2', 'h', 2, 3, 1, False, self.images),       
                Vehicle('v3', 'v', 3, 2, 0, False, self.images),     
                Vehicle('v2', 'h', 2, 0, 4, False, self.images),       
                Vehicle('v2', 'v', 2, 4, 3, False, self.images),
            ],
            2: [  # Level 2
                Vehicle('target', 'h', 2, 1, 2, True, self.images),
                Vehicle('v2', 'v', 2, 0, 0, False, self.images),
                Vehicle('v3', 'h', 3, 2, 0, False, self.images),
                Vehicle('v2', 'v', 2, 3, 1, False, self.images),
                Vehicle('v2', 'h', 2, 1, 4, False, self.images),
            ]
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

    def start_solving(self):
        """Start the DFS solving process"""
        if not self.solving:
            print("Starting DFS solver...")
            solution = self.solver.solve()
            if solution:
                print(f"Solution found with {len(solution)} moves!")
                self.solution_moves = solution
                self.current_move_index = 0
                self.solving = True
                self.move_timer = time.time()
            else:
                print("No solution found!")

    def update_solving(self):
        """Update the solving animation"""
        if self.solving and self.solution_moves:
            current_time = time.time()
            if current_time - self.move_timer >= self.move_delay:
                if self.current_move_index < len(self.solution_moves):
                    move = self.solution_moves[self.current_move_index]
                    vehicle_index, dx, dy = move
                    
                    # Apply the move
                    self.vehicles[vehicle_index].x += dx
                    self.vehicles[vehicle_index].y += dy
                    
                    print(f"Applied move {self.current_move_index + 1}/{len(self.solution_moves)}: Vehicle {vehicle_index} moved by ({dx}, {dy})")
                    
                    self.current_move_index += 1
                    self.move_timer = current_time
                else:
                    # Solving complete
                    self.solving = False
                    print("Solving complete!")

    def get_grid(self):
        grid = [[0] * MAP_N for _ in range(MAP_N)]
        for i, vehicle in enumerate(self.vehicles):
            for x, y in vehicle.positions():
                if 0 <= x < MAP_N and 0 <= y < MAP_N:
                    grid[y][x] = i + 1
        return grid

    def is_valid_move(self, vehicle, new_x, new_y):
        # Check bounds
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.is_target, self.images).positions():
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False
        
        # Check collisions
        grid = self.get_grid()
        vehicle_index = self.vehicles.index(vehicle)
        
        for x, y in Vehicle(vehicle.image_key, vehicle.orient, vehicle.len, new_x, new_y, vehicle.is_target, self.images).positions():
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

    def draw(self, surf):
        # Draw map overlay
        if 'map' in self.images and self.images['map']:
            surf.blit(self.images['map'], (BOARD_OFFSET_X, BOARD_OFFSET_Y))

        # Draw exit
        exit_rect = pygame.Rect(BOARD_OFFSET_X + MAP_N * TILE, BOARD_OFFSET_Y + 2 * TILE, 20, TILE)
        pygame.draw.rect(surf, (255, 200, 200), exit_rect)

        # Draw vehicles
        for vehicle in self.vehicles:
            vehicle.draw(surf)

    def is_solved(self):
        for vehicle in self.vehicles:
            if vehicle.is_target:
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False

# ===============================
# Button Class
# ===============================
class Button:
    def __init__(self, text, pos, width=120, height=40, color=GREEN):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.SysFont(None, 24)
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 2)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def hit(self, mpos):
        return self.rect.collidepoint(mpos)

# ===============================
# Screen Management
# ===============================
class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None
        
    def add_screen(self, name, screen):
        self.screens[name] = screen
        
    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = self.screens[name]
            if hasattr(self.current_screen, 'on_enter'):
                self.current_screen.on_enter()
                
    def update(self):
        if self.current_screen:
            return self.current_screen.update()
        return True
        
    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)

# ===============================
# Base Screen Class
# ===============================
class Screen:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        
    def update(self):
        return True
        
    def draw(self, surface):
        surface.fill(BLACK)
        
    def handle_event(self, event):
        pass
        
    def on_enter(self):
        pass

# ===============================
# Menu Screen
# ===============================
class MenuScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.play_btn = Button("PLAY", (SCREEN_W//2 - 100, SCREEN_H//2 - 50), 200, 60)
        
    def draw(self, surface):
        surface.fill((30, 30, 60))
        
        # Title
        font = pygame.font.SysFont(None, 96)
        title = font.render("RUSH HOUR", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_W//2, 200))
        surface.blit(title, title_rect)
        
        # Subtitle
        small_font = pygame.font.SysFont(None, 36)
        subtitle = small_font.render("Puzzle Game", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_W//2, 250))
        surface.blit(subtitle, subtitle_rect)
        
        # Button
        self.play_btn.draw(surface)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_btn.hit(event.pos):
                self.screen_manager.set_screen('level_select')

# ===============================
# Level Select Screen
# ===============================
class LevelSelectScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.back_btn = Button("BACK", (50, 50), 120, 50)
        self.level_buttons = []
        
        # Create 2 level buttons
        button_width = 120
        button_height = 80
        start_x = SCREEN_W//2 - button_width - 10
        start_y = 300
        
        for i in range(2):
            x = start_x + i * (button_width + 20)
            y = start_y
            self.level_buttons.append(Button(f"Level {i+1}", (x, y), button_width, button_height))
            
    def draw(self, surface):
        surface.fill((25, 35, 50))
        
        # Title
        font = pygame.font.SysFont(None, 64)
        title = font.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_W//2, 150))
        surface.blit(title, title_rect)
        
        # Level buttons
        for btn in self.level_buttons:
            btn.draw(surface)
            
        # Back button
        self.back_btn.draw(surface)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            else:
                for i, btn in enumerate(self.level_buttons):
                    if btn.hit(event.pos):
                        game_screen = self.screen_manager.screens['game']
                        game_screen.load_level(i + 1)
                        self.screen_manager.set_screen('game')

# ===============================
# Game Screen
# ===============================
class GameScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        self.load_images()
        self.map = Map(self.images)
        
        # Buttons
        self.reset_btn = Button("Reset", (50, SCREEN_H - 100), 120, 40)
        self.back_btn = Button("Menu", (50, 50), 120, 40)
        self.solve_btn = Button("Solve DFS", (50, SCREEN_H - 150), 120, 40, ORANGE)

    def load_images(self):
        """Load all necessary images"""
        self.images = {}
        
        try:
            # Background
            self.images['background'] = pygame.image.load("bg.png")
            self.images['background'] = pygame.transform.scale(self.images['background'], (SCREEN_W, SCREEN_H))
            
            # Map overlay
            self.images['map'] = pygame.image.load("map.png")
            self.images['map'] = pygame.transform.scale(self.images['map'], (MAP_N * TILE, MAP_N * TILE))
            
            # Vehicle images
            target_img = pygame.image.load("target.png")
            self.images['target'] = pygame.transform.scale(target_img, (TILE * 2, TILE))
            
            v2_img = pygame.image.load("vh2h.png")
            self.images['v2_h'] = pygame.transform.scale(v2_img, (TILE * 2, TILE))
            v2_rotated = pygame.transform.rotate(v2_img, 90)
            self.images['v2_v'] = pygame.transform.scale(v2_rotated, (TILE, TILE * 2))
            
            v3_img = pygame.image.load("vh3h.png")
            self.images['v3_h'] = pygame.transform.scale(v3_img, (TILE * 3, TILE))
            v3_rotated = pygame.transform.rotate(v3_img, 90)
            self.images['v3_v'] = pygame.transform.scale(v3_rotated, (TILE, TILE * 3))
            
            print("All images loaded successfully!")
        except pygame.error as e:
            print(f"Could not load images: {e}")
            self.images = {}

    def load_level(self, level_num):
        """Load a specific level"""
        self.map.load_level(level_num)

    def update(self):
        """Update the game screen"""
        self.map.update_solving()
        return True

    def draw(self, surface):
        # Draw background
        if 'background' in self.images:
            surface.blit(self.images['background'], (0, 0))
        else:
            surface.fill((40, 40, 80))
        
        # Draw map
        self.map.draw(surface)
        
        # Draw UI
        self.reset_btn.draw(surface)
        self.back_btn.draw(surface)
        self.solve_btn.draw(surface)
        
        # Draw instructions
        font = pygame.font.SysFont(None, 24)
        instructions = [
            f"Level {self.map.current_level}",
            "Drag vehicles to move them",
            "Get RED car to exit →",
            f"Status: {'SOLVED!' if self.map.is_solved() else 'Playing...'}"
        ]
        
        if self.map.solving:
            instructions.append(f"Solving... {self.map.current_move_index}/{len(self.map.solution_moves)}")
        
        for i, text in enumerate(instructions):
            color = GREEN if "SOLVED!" in text else (YELLOW if "Solving..." in text else WHITE)
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (50, 150 + i * 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.reset_btn.hit(event.pos):
                self.map.reset()
            elif self.back_btn.hit(event.pos):
                self.screen_manager.set_screen('menu')
            elif self.solve_btn.hit(event.pos):
                self.map.start_solving()
            else:
                self.map.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.map.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.map.handle_mouse_motion(event.pos)

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