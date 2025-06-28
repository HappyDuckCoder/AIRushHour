from Screen.BaseScreen import *
from Game.Map import *
from UI.Button import *

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