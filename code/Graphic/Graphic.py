import pygame
from constants import *

class Graphics:
    def __init__(self, screen_width, screen_height, map_size, tile_size):
        self.SCREEN_W = screen_width
        self.SCREEN_H = screen_height
        self.MAP_N = map_size
        self.TILE = tile_size
        
        # Load images
        self.images = {}
        self.load_images()
    
    def load_images(self):
        """Load all necessary images"""
        try:
            # Background
            self.images['background'] = pygame.image.load("bg.png")
            self.images['background'] = pygame.transform.scale(self.images['background'], (self.SCREEN_W, self.SCREEN_H))
            
            # Map overlay
            self.images['map'] = pygame.image.load("map.png")
            self.images['map'] = pygame.transform.scale(self.images['map'], (self.MAP_N * self.TILE, self.MAP_N * self.TILE))
            
            # Vehicle images
            target_img = pygame.image.load("target.png")
            self.images['target'] = pygame.transform.scale(target_img, (self.TILE * 2, self.TILE))
            
            v2_img = pygame.image.load("vh2h.png")
            self.images['v2_h'] = pygame.transform.scale(v2_img, (self.TILE * 2, self.TILE))
            v2_rotated = pygame.transform.rotate(v2_img, 90)
            self.images['v2_v'] = pygame.transform.scale(v2_rotated, (self.TILE, self.TILE * 2))
            
            v3_img = pygame.image.load("vh3h.png")
            self.images['v3_h'] = pygame.transform.scale(v3_img, (self.TILE * 3, self.TILE))
            v3_rotated = pygame.transform.rotate(v3_img, 90)
            self.images['v3_v'] = pygame.transform.scale(v3_rotated, (self.TILE, self.TILE * 3))
            
            print("All images loaded successfully!")
        except pygame.error as e:
            print(f"Could not load images: {e}")
            self.images = {}
    
    def draw_button(self, surface, button):
        """Draw a button"""
        pygame.draw.rect(surface, button.color, button.rect)
        pygame.draw.rect(surface, WHITE, button.rect, 2)
        text_surf = button.font.render(button.text, True, BLACK)
        text_rect = text_surf.get_rect(center=button.rect.center)
        surface.blit(text_surf, text_rect)
    
    def draw_title(self, surface, title_text, pos, font_size=96, color=None):
        """Draw title text"""
        if color is None:
            color = YELLOW
        font = pygame.font.SysFont(None, font_size)
        title = font.render(title_text, True, color)
        title_rect = title.get_rect(center=pos)
        surface.blit(title, title_rect)
    
    def draw_subtitle(self, surface, subtitle_text, pos, font_size=36, color=None):
        """Draw subtitle text"""
        if color is None:
            color = WHITE
        font = pygame.font.SysFont(None, font_size)
        subtitle = font.render(subtitle_text, True, color)
        subtitle_rect = subtitle.get_rect(center=pos)
        surface.blit(subtitle, subtitle_rect)
    
    def draw_text(self, surface, text, pos, font_size=24, color=None):
        """Draw general text"""
        if color is None:
            color = WHITE
        font = pygame.font.SysFont(None, font_size)
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, pos)
    
    def draw_grid_debug(self, surface, grid):
        """Draw debug grid (optional debugging function)"""
        for y in range(self.MAP_N):
            for x in range(self.MAP_N):
                rect = pygame.Rect(
                    self.BOARD_OFFSET_X + x * self.TILE,
                    self.BOARD_OFFSET_Y + y * self.TILE,
                    self.TILE,
                    self.TILE
                )
                pygame.draw.rect(surface, self.GRAY, rect, 1)
                
                # Draw grid numbers for debugging
                if grid[y][x] != 0:
                    font = pygame.font.SysFont(None, 16)
                    text = font.render(str(grid[y][x]), True, self.RED)
                    surface.blit(text, (rect.x + 5, rect.y + 5))
    
    def clear_screen(self, surface, color=None):
        """Clear screen with specified color"""
        if color is None:
            color = BLACK
        surface.fill(color)
    
    def get_board_position(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        board_x = (mouse_pos[0] - self.BOARD_OFFSET_X) // self.TILE
        board_y = (mouse_pos[1] - self.BOARD_OFFSET_Y) // self.TILE
        return board_x, board_y
    
    def get_screen_position(self, board_x, board_y):
        """Convert board coordinates to screen position"""
        screen_x = self.BOARD_OFFSET_X + board_x * self.TILE
        screen_y = self.BOARD_OFFSET_Y + board_y * self.TILE
        return screen_x, screen_y
    
gfx = Graphics(SCREEN_W, SCREEN_H, MAP_N, TILE)