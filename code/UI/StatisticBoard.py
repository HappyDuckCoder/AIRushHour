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
        self.title_font = Font(32)
        self.stats_font = Font(24)
        self.title_text = None
        self.stats_texts = []
        self.rating_text = None
        self.load_statistics()
    
    def load_statistics(self):
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
        if not self.statistics:
            return
        self.title_text = Text(
            "PUZZLE SOLVED!",
            GOLD,
            (0, 0),
            self.title_font,
            center=True
        )
        self.stats_texts = []
        algorithm_time = self.statistics.get('algorithm_solve_time', 0)
        if algorithm_time == 0:
            algorithm_time = self.statistics.get('time_executed', 0)
        stats_data = [
            ("Level:", str(self.statistics.get('level', 'N/A'))),
            ("Algorithm:", self.statistics.get('algorithm', 'N/A')),
            ("Time:", f"{algorithm_time:.3f}s"),
            ("Solution Length:", str(self.statistics.get('solution_length', 0))),
            ("Status:", "SOLVED" if self.statistics.get('solved', False) else "FAILED")
        ]
        for label, value in stats_data:
            label_text = Text(
                label,
                (80, 80, 80),
                (0, 0),
                self.stats_font,
                center=False
            )
            value_color = (40, 40, 40)
            if label == "Status:":
                value_color = (60, 179, 113) if value == "SOLVED" else (220, 20, 60)
            elif label == "Algorithm:":
                value_color = (70, 130, 180)
            elif label == "Time:":
                value_color = (255, 140, 0)
            value_text = Text(
                value,
                value_color,
                (0, 0),
                self.stats_font,
                center=False
            )
            self.stats_texts.append((label_text, value_text))
        if self.statistics.get('solved', False):
            nodes_expanded = self.statistics.get('nodes_expanded', 0)
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
                (0, 0),
                self.stats_font,
                center=True
            )
    
    def set_alpha(self, alpha):
        self.panel_alpha = alpha
    
    def update_alpha(self, target_alpha, speed=3):
        self.target_alpha = target_alpha
        self.fade_speed = speed
        if self.panel_alpha < self.target_alpha:
            self.panel_alpha = min(self.target_alpha, self.panel_alpha + self.fade_speed)
        elif self.panel_alpha > self.target_alpha:
            self.panel_alpha = max(self.target_alpha, self.panel_alpha - self.fade_speed)
    
    def draw(self, surface, x=None, y=None):
        if not self.statistics or self.panel_alpha <= 0:
            return
        panel_width = 400
        panel_height = 280
        panel_x = x if x is not None else (SCREEN_W - panel_width) // 2
        panel_y = y if y is not None else (SCREEN_H - panel_height) // 2 + 50
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(self.panel_alpha)
        for i in range(panel_height):
            color_intensity = 240 - int(i * 0.3)
            color = (color_intensity, color_intensity, color_intensity + 10)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))
        pygame.draw.rect(panel_surface, GOLD, (0, 0, panel_width, panel_height), 3)
        pygame.draw.rect(panel_surface, (200, 200, 200), (3, 3, panel_width-6, panel_height-6), 1)
        if self.title_text:
            self.title_text.set_position((panel_width//2, 25))
            self.title_text.draw(panel_surface)
        y_offset = 60
        line_height = 28
        for label_text, value_text in self.stats_texts:
            label_text.set_position((20, y_offset))
            value_text.set_position((180, y_offset))
            label_text.draw(panel_surface)
            value_text.draw(panel_surface)
            y_offset += line_height
        if self.rating_text:
            self.rating_text.set_position((panel_width//2, panel_height - 25))
            self.rating_text.draw(panel_surface)
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def get_statistics(self):
        return self.statistics
    
    def has_statistics(self):
        return self.statistics is not None
    
    def reload_statistics(self):
        self.load_statistics()
