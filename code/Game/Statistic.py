import pygame
import time
from constants import *

class Statistic:
    def __init__(self, time_executed=0, node_expand=None, total_node=0, total_cost=0):
        self.time_executed = time_executed
        self.node_expand = node_expand if node_expand is not None else []
        self.total_node = total_node
        self.total_cost = total_cost
        
        # UI properties
        self.font = None
        self.small_font = None
        self.init_fonts()
        
        # Display properties
        self.panel_width = 300
        self.panel_height = 200
        self.panel_x = SCREEN_W - self.panel_width - 20  
        self.panel_y = 20
        self.background_color = (240, 240, 240)
        self.border_color = (100, 100, 100)
        self.text_color = (50, 50, 50)
        self.header_color = (30, 30, 30)
        
        # Animation properties
        self.visible = True
        self.alpha = 255
        self.fade_speed = 5
        
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 20)
    
    def set_time_executed(self, time_value):
        """Cập nhật thời gian thực hiện"""
        self.time_executed = time_value
    
    def set_node_expand(self, node_list):
        """Cập nhật danh sách nodes đã expand"""
        self.node_expand = node_list if node_list is not None else []
    
    def set_total_node(self, total):
        """Cập nhật tổng số nodes"""
        self.total_node = total
    
    def set_total_cost(self, cost):
        """Cập nhật tổng chi phí"""
        self.total_cost = cost
    
    def add_expanded_node(self, node):
        """Thêm một node vào danh sách expanded"""
        self.node_expand.append(node)
        self.total_node += 1
    
    def reset_statistics(self):
        """Reset tất cả thống kê"""
        self.time_executed = 0
        self.node_expand = []
        self.total_node = 0
        self.total_cost = 0
    
    def format_time(self, seconds):
        """Format thời gian thành string dễ đọc"""
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
    
    def get_statistics_summary(self):
        """Lấy tóm tắt thống kê"""
        return {
            'time_executed': self.time_executed,
            'nodes_expanded': len(self.node_expand),
            'total_nodes': self.total_node,
            'total_cost': self.total_cost,
            'efficiency': self.calculate_efficiency()
        }
    
    def calculate_efficiency(self):
        """Tính toán hiệu suất thuật toán"""
        if self.total_node == 0:
            return 0
        return (self.total_cost / self.total_node) if self.total_node > 0 else 0
    
    def toggle_visibility(self):
        """Bật/tắt hiển thị panel"""
        self.visible = not self.visible
    
    def update(self, dt):
        """Cập nhật animation"""
        if self.visible and self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed * dt * 100)
        elif not self.visible and self.alpha > 0:
            self.alpha = max(0, self.alpha - self.fade_speed * dt * 100)
    
    def draw_panel_background(self, surface):
        """Vẽ background của panel"""
        # Tạo surface với alpha
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(self.alpha)
        
        # Vẽ background
        panel_surface.fill(self.background_color)
        
        # Vẽ border
        pygame.draw.rect(panel_surface, self.border_color, 
                        (0, 0, self.panel_width, self.panel_height), 2)
        
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
    
    def draw_statistics_text(self, surface):
        """Vẽ text thống kê"""
        if self.alpha <= 0:
            return
            
        y_offset = self.panel_y + 10
        x_offset = self.panel_x + 10
        line_height = 25
        
        # Header
        header_text = self.font.render("Algorithm Statistics", True, self.header_color)
        header_surface = pygame.Surface(header_text.get_size())
        header_surface.set_alpha(self.alpha)
        header_surface.blit(header_text, (0, 0))
        surface.blit(header_surface, (x_offset, y_offset))
        y_offset += line_height + 5
        
        # Statistics data
        stats_data = [
            f"Time: {self.format_time(self.time_executed)}",
            f"Nodes Expanded: {len(self.node_expand)}",
            f"Total Nodes: {self.total_node}",
            f"Solution Cost: {self.total_cost}",
            f"Efficiency: {self.calculate_efficiency():.2f}"
        ]
        
        for stat in stats_data:
            text_surface = self.small_font.render(stat, True, self.text_color)
            alpha_surface = pygame.Surface(text_surface.get_size())
            alpha_surface.set_alpha(self.alpha)
            alpha_surface.blit(text_surface, (0, 0))
            surface.blit(alpha_surface, (x_offset, y_offset))
            y_offset += line_height - 5
    
    def draw(self, surface):
        """Vẽ panel thống kê"""
        if self.alpha <= 0:
            return
            
        self.draw_panel_background(surface)
        self.draw_statistics_text(surface)
    
    def handle_click(self, pos):
        """Xử lý click vào panel"""
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                self.panel_width, self.panel_height)
        return panel_rect.collidepoint(pos)


class Instruction:
    def __init__(self):
        self.font = None
        self.init_fonts()
        
        # UI properties
        self.panel_width = 400
        self.panel_height = 300
        self.panel_x = 20
        self.panel_y = SCREEN_H - self.panel_height - 20  # Sử dụng SCREEN_H thay vì SCREEN_HEIGHT
        self.background_color = (250, 250, 250)
        self.border_color = (80, 80, 80)
        self.text_color = (40, 40, 40)
        self.header_color = (20, 20, 20)
        
        # Visibility
        self.visible = True
        self.alpha = 255
        
        # Instructions content
        self.instructions = [
            "Game Controls:",
            "• Click and drag vehicles to move them",
            "• Target vehicle (with characters) must reach exit",
            "• Press SPACE to auto-solve with current algorithm",
            "• Press P to pause/resume auto-solving",
            "• Press R to reset current level",
            "• Press N for next level",
            "• Press B for previous level",
            "",
            "Algorithm Selection:",
            "• Press 1 for BFS",
            "• Press 2 for DFS", 
            "• Press 3 for A*",
            "• Press 4 for Greedy Best-First"
        ]
    
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 20)
            self.header_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('Arial', 20)
            self.header_font = pygame.font.SysFont('Arial', 24)
    
    def toggle_visibility(self):
        """Bật/tắt hiển thị"""
        self.visible = not self.visible
    
    def draw(self, surface):
        """Vẽ panel hướng dẫn"""
        if not self.visible or self.alpha <= 0:
            return
            
        # Vẽ background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(self.alpha)
        panel_surface.fill(self.background_color)
        
        # Vẽ border
        pygame.draw.rect(panel_surface, self.border_color,
                        (0, 0, self.panel_width, self.panel_height), 2)
        
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Vẽ instructions
        y_offset = self.panel_y + 10
        x_offset = self.panel_x + 10
        line_height = 18
        
        for instruction in self.instructions:
            if instruction == "":
                y_offset += line_height // 2
                continue
                
            if instruction.endswith(":"):
                # Header
                text_surface = self.header_font.render(instruction, True, self.header_color)
            else:
                # Regular instruction
                text_surface = self.font.render(instruction, True, self.text_color)
            
            alpha_surface = pygame.Surface(text_surface.get_size())
            alpha_surface.set_alpha(self.alpha)
            alpha_surface.blit(text_surface, (0, 0))
            surface.blit(alpha_surface, (x_offset, y_offset))
            y_offset += line_height


class Notification:
    def __init__(self):
        self.font = None
        self.init_fonts()
        
        # Notification properties
        self.messages = []
        self.max_messages = 5
        self.message_duration = 3.0  # seconds
        self.fade_duration = 0.5    # seconds
        
        # UI properties
        self.panel_width = 350
        self.panel_x = (SCREEN_W - self.panel_width) // 2  
        self.panel_y = 50
        self.background_color = (240, 240, 240)
        self.border_color = (100, 100, 100)
        self.text_color = (50, 50, 50)
        
        # Message types and colors
        self.message_colors = {
            'info': (70, 130, 180),
            'success': (60, 179, 113),
            'warning': (255, 165, 0),
            'error': (220, 20, 60)
        }
    
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 22)
        except:
            self.font = pygame.font.SysFont('Arial', 22)
    
    def add_message(self, text, msg_type='info', duration=None):
        """Thêm thông báo mới"""
        if duration is None:
            duration = self.message_duration
            
        message = {
            'text': text,
            'type': msg_type,
            'start_time': time.time(),
            'duration': duration,
            'alpha': 255
        }
        
        self.messages.append(message)
        
        # Giữ số lượng messages trong giới hạn
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def update(self, dt):
        """Cập nhật thông báo"""
        current_time = time.time()
        messages_to_remove = []
        
        for message in self.messages:
            elapsed = current_time - message['start_time']
            
            if elapsed > message['duration']:
                messages_to_remove.append(message)
            elif elapsed > message['duration'] - self.fade_duration:
                # Fade out
                fade_progress = (elapsed - (message['duration'] - self.fade_duration)) / self.fade_duration
                message['alpha'] = int(255 * (1 - fade_progress))
        
        # Xóa messages đã hết hạn
        for message in messages_to_remove:
            if message in self.messages:
                self.messages.remove(message)
    
    def draw(self, surface):
        """Vẽ thông báo"""
        if not self.messages:
            return
            
        y_offset = self.panel_y
        
        for message in self.messages:
            if message['alpha'] <= 0:
                continue
                
            # Tính kích thước message
            text_surface = self.font.render(message['text'], True, self.text_color)
            msg_width = text_surface.get_width() + 20
            msg_height = text_surface.get_height() + 10
            
            # Vẽ background
            bg_surface = pygame.Surface((msg_width, msg_height))
            bg_surface.set_alpha(message['alpha'])
            bg_surface.fill(self.background_color)
            
            # Vẽ border với màu theo type
            border_color = self.message_colors.get(message['type'], self.border_color)
            pygame.draw.rect(bg_surface, border_color, (0, 0, msg_width, msg_height), 2)
            
            # Vẽ message
            msg_x = (SCREEN_W - msg_width) // 2  # Sử dụng SCREEN_W thay vì SCREEN_WIDTH
            surface.blit(bg_surface, (msg_x, y_offset))
            
            # Vẽ text
            text_alpha_surface = pygame.Surface(text_surface.get_size())
            text_alpha_surface.set_alpha(message['alpha'])
            text_alpha_surface.blit(text_surface, (0, 0))
            surface.blit(text_alpha_surface, (msg_x + 10, y_offset + 5))
            
            y_offset += msg_height + 5
    
    def show_algorithm_info(self, algorithm_name, time_taken, nodes_expanded, solution_length):
        """Hiển thị thông tin thuật toán"""
        info_text = f"{algorithm_name}: {time_taken:.2f}s, {nodes_expanded} nodes, {solution_length} moves"
        self.add_message(info_text, 'info', 4.0)
    
    def show_level_complete(self, level_num):
        """Hiển thị hoàn thành level"""
        self.add_message(f"Level {level_num} Complete!", 'success', 3.0)
    
    def show_no_solution(self):
        """Hiển thị không có giải pháp"""
        self.add_message("No solution found!", 'error', 3.0)
    
    def show_algorithm_selected(self, algorithm_name):
        """Hiển thị thuật toán được chọn"""
        self.add_message(f"Algorithm: {algorithm_name}", 'info', 2.0)