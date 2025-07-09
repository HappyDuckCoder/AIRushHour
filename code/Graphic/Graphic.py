import pygame
from constants import *

class Graphics:
    def __init__(self, screen_width, screen_height, map_size, tile_size):
        self.SCREEN_W = screen_width
        self.SCREEN_H = screen_height
        self.MAP_N = map_size
        self.TILE = tile_size
    
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