import pygame
import json
import os
from constants import *
from UI.Text import Text, Font

class StatisticBoard:
    def __init__(self):
        self.statistics = None
        self.panel_alpha = 0
        self.target_alpha = 255
        self.fade_speed = 3
        
        # Initialize fonts
        self.title_font = Font(32)
        self.stats_font = Font(24)
        
        # Initialize text objects (will be updated when statistics are loaded)
        self.title_text = None
        self.stats_texts = []
        self.rating_text = None
        
        self.load_statistics()
    
    def load_statistics(self):
        """Load statistics from file"""
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            stats_file = os.path.join(base_path, 'statistic.txt')
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.statistics = json.load(f)
                print(f"Loaded statistics: {self.statistics}")
                self._create_text_objects()
            else:
                print("No statistics file found")
                self.statistics = None
        except Exception as e:
            print(f"Error loading statistics: {e}")
            self.statistics = None
    
    def _create_text_objects(self):
        """Create text objects for statistics display"""
        if not self.statistics:
            return
            
        # Create title text
        self.title_text = Text(
            "PUZZLE SOLVED!",
            GOLD,
            (0, 0),  # Position will be set in draw method
            self.title_font,
            center=True
        )
        
        # Create statistics text objects
        self.stats_texts = []
        
        # Take algorithm solve time or fallback to time_executed
        algorithm_time = self.statistics.get('algorithm_solve_time', 0)
        if algorithm_time == 0:
            # Fallback to time_executed if algorithm_solve_time is not available
            algorithm_time = self.statistics.get('time_executed', 0)
        
        stats_data = [
            ("Level:", str(self.statistics.get('level', 'N/A'))),
            ("Algorithm:", self.statistics.get('algorithm', 'N/A')),
            ("Time:", f"{algorithm_time:.3f}s"),
            ("Solution Length:", str(self.statistics.get('solution_length', 0))),
            ("Status:", "SOLVED" if self.statistics.get('solved', False) else "FAILED")
        ]
        
        for label, value in stats_data:
            # Label text
            label_text = Text(
                label,
                (80, 80, 80),
                (0, 0),  # Position will be set in draw method
                self.stats_font,
                center=False
            )
            
            # Value text with appropriate color
            value_color = (40, 40, 40)
            if label == "Status:":
                value_color = (60, 179, 113) if value == "SOLVED" else (220, 20, 60)
            elif label == "Algorithm:":
                value_color = (70, 130, 180)
            elif label == "Time:":
                value_color = (255, 140, 0)  # Orange for time to highlight
            
            value_text = Text(
                value,
                value_color,
                (0, 0),  # Position will be set in draw method
                self.stats_font,
                center=False
            )
            
            self.stats_texts.append((label_text, value_text))
        
        # Create performance rating text
        if self.statistics.get('solved', False):
            nodes_expanded = self.statistics.get('nodes_expanded', 0)
            
            # Simple rating system based on algorithm performance
            if algorithm_time < 0.1 and nodes_expanded < 100:
                rating = "EXCELLENT"
                rating_color = GOLD
            elif algorithm_time < 0.5 and nodes_expanded < 500:
                rating = "GOOD"
                rating_color = (70, 130, 180)
            else:
                rating = "COMPLETED"
                rating_color = (128, 128, 128)
            
            self.rating_text = Text(
                rating,
                rating_color,
                (0, 0),  # Position will be set in draw method
                self.stats_font,
                center=True
            )
    
    def set_alpha(self, alpha):
        """Set the alpha value for the statistics panel"""
        self.panel_alpha = alpha
    
    def update_alpha(self, target_alpha, speed=3):
        """Update alpha towards target with fade effect"""
        self.target_alpha = target_alpha
        self.fade_speed = speed
        
        if self.panel_alpha < self.target_alpha:
            self.panel_alpha = min(self.target_alpha, self.panel_alpha + self.fade_speed)
        elif self.panel_alpha > self.target_alpha:
            self.panel_alpha = max(self.target_alpha, self.panel_alpha - self.fade_speed)
    
    def draw(self, surface, x=None, y=None):
        """Draw the statistics panel"""
        if not self.statistics or self.panel_alpha <= 0:
            return
            
        # Panel dimensions and position
        panel_width = 400
        panel_height = 280

        panel_x = x if x is not None else (SCREEN_W - panel_width) // 2
        panel_y = y if y is not None else (SCREEN_H - panel_height) // 2 + 50
        
        # Create panel surface
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(self.panel_alpha)
        
        # Background with gradient effect
        for i in range(panel_height):
            color_intensity = 240 - int(i * 0.3)
            color = (color_intensity, color_intensity, color_intensity + 10)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))
        
        # Border
        pygame.draw.rect(panel_surface, GOLD, (0, 0, panel_width, panel_height), 3)
        pygame.draw.rect(panel_surface, (200, 200, 200), (3, 3, panel_width-6, panel_height-6), 1)
        
        # Draw title
        if self.title_text:
            self.title_text.set_position((panel_width//2, 25))
            self.title_text.draw(panel_surface)
        
        # Draw statistics
        y_offset = 60
        line_height = 28
        
        for label_text, value_text in self.stats_texts:
            # Set positions for label and value
            label_text.set_position((20, y_offset))
            value_text.set_position((180, y_offset))
            
            # Draw texts
            label_text.draw(panel_surface)
            value_text.draw(panel_surface)
            
            y_offset += line_height
        
        # Draw performance rating
        if self.rating_text:
            self.rating_text.set_position((panel_width//2, panel_height - 25))
            self.rating_text.draw(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def get_statistics(self):
        """Get the loaded statistics"""
        return self.statistics
    
    def has_statistics(self):
        """Check if statistics are loaded"""
        return self.statistics is not None
    
    def reload_statistics(self):
        """Reload statistics from file"""
        self.load_statistics()