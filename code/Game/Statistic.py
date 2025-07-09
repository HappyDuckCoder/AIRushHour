import pygame
import time
import json
import os
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
        self.panel_width = 320
        self.panel_height = 240
        self.panel_x = SCREEN_W - self.panel_width - 20
        self.panel_y = 20
        self.background_color = (245, 245, 250)
        self.border_color = (70, 130, 180)
        self.text_color = (40, 40, 40)
        self.header_color = (20, 20, 20)
        self.accent_color = (70, 130, 180)
        
        # Animation properties
        self.visible = True
        self.alpha = 255
        self.fade_speed = 5
        
        # Enhanced visual effects
        self.glow_alpha = 0
        self.glow_direction = 1
        self.panel_shadow_offset = 3
        
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 26)
            self.small_font = pygame.font.Font(None, 22)
            self.header_font = pygame.font.Font(None, 28)
        except:
            self.font = pygame.font.SysFont('Arial', 26)
            self.small_font = pygame.font.SysFont('Arial', 22)
            self.header_font = pygame.font.SysFont('Arial', 28)
    
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
        if seconds < 0.001:
            return f"{seconds*1000000:.0f}μs"
        elif seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.3f}s"
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
    
    def get_performance_rating(self):
        """Đánh giá hiệu suất"""
        if self.time_executed < 0.01 and len(self.node_expand) < 50:
            return "★★★ EXCELLENT", (255, 215, 0)
        elif self.time_executed < 0.1 and len(self.node_expand) < 200:
            return "★★☆ GOOD", (70, 130, 180)
        elif self.time_executed < 1.0 and len(self.node_expand) < 1000:
            return "★☆☆ AVERAGE", (255, 165, 0)
        else:
            return "☆☆☆ SLOW", (220, 20, 60)
    
    def toggle_visibility(self):
        """Bật/tắt hiển thị panel"""
        self.visible = not self.visible
    
    def update(self, dt):
        """Cập nhật animation"""
        if self.visible and self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed * dt * 100)
        elif not self.visible and self.alpha > 0:
            self.alpha = max(0, self.alpha - self.fade_speed * dt * 100)
        
        # Glow effect animation
        self.glow_alpha += self.glow_direction * 2
        if self.glow_alpha >= 30:
            self.glow_direction = -1
        elif self.glow_alpha <= 0:
            self.glow_direction = 1
    
    def draw_panel_background(self, surface):
        """Vẽ background của panel với hiệu ứng đẹp"""
        if self.alpha <= 0:
            return
        
        # Shadow effect
        shadow_surface = pygame.Surface((self.panel_width, self.panel_height))
        shadow_surface.fill((0, 0, 0))
        shadow_surface.set_alpha(int(self.alpha * 0.3))
        surface.blit(shadow_surface, (self.panel_x + self.panel_shadow_offset, 
                                     self.panel_y + self.panel_shadow_offset))
        
        # Main panel surface
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(self.alpha)
        
        # Gradient background
        for i in range(self.panel_height):
            color_intensity = 245 - int(i * 0.1)
            color = (color_intensity, color_intensity, color_intensity + 5)
            pygame.draw.line(panel_surface, color, (0, i), (self.panel_width, i))
        
        # Glow border effect
        glow_color = (*self.accent_color, int(self.glow_alpha))
        pygame.draw.rect(panel_surface, self.accent_color, 
                        (0, 0, self.panel_width, self.panel_height), 3)
        pygame.draw.rect(panel_surface, (200, 200, 200), 
                        (3, 3, self.panel_width-6, self.panel_height-6), 1)
        
        # Header background
        header_rect = pygame.Rect(5, 5, self.panel_width-10, 35)
        pygame.draw.rect(panel_surface, self.accent_color, header_rect)
        pygame.draw.rect(panel_surface, (255, 255, 255), header_rect, 1)
        
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
    
    def draw_statistics_text(self, surface):
        """Vẽ text thống kê với styling đẹp"""
        if self.alpha <= 0:
            return
            
        y_offset = self.panel_y + 12
        x_offset = self.panel_x + 15
        line_height = 24
        
        # Header
        header_text = self.header_font.render("ALGORITHM STATS", True, (255, 255, 255))
        header_surface = pygame.Surface(header_text.get_size())
        header_surface.set_alpha(self.alpha)
        header_surface.blit(header_text, (0, 0))
        surface.blit(header_surface, (x_offset, y_offset))
        y_offset += 35
        
        # Statistics data with icons/symbols
        stats_data = [
            ("⏱️ Time:", self.format_time(self.time_executed), (70, 130, 180)),
            ("🔍 Nodes:", f"{len(self.node_expand)}", (60, 179, 113)),
            ("📊 Total:", f"{self.total_node}", (255, 140, 0)),
            ("💰 Cost:", f"{self.total_cost}", (238, 130, 238)),
            ("⚡ Efficiency:", f"{self.calculate_efficiency():.2f}", (220, 20, 60))
        ]
        
        for label, value, color in stats_data:
            # Label
            label_text = self.small_font.render(label, True, self.text_color)
            label_surface = pygame.Surface(label_text.get_size())
            label_surface.set_alpha(self.alpha)
            label_surface.blit(label_text, (0, 0))
            surface.blit(label_surface, (x_offset, y_offset))
            
            # Value with color
            value_text = self.small_font.render(value, True, color)
            value_surface = pygame.Surface(value_text.get_size())
            value_surface.set_alpha(self.alpha)
            value_surface.blit(value_text, (0, 0))
            surface.blit(value_surface, (x_offset + 120, y_offset))
            
            y_offset += line_height
        
        # Performance rating
        if self.total_node > 0:
            rating_text, rating_color = self.get_performance_rating()
            rating_surface = self.small_font.render(rating_text, True, rating_color)
            rating_alpha_surface = pygame.Surface(rating_surface.get_size())
            rating_alpha_surface.set_alpha(self.alpha)
            rating_alpha_surface.blit(rating_surface, (0, 0))
            
            # Center the rating
            rating_x = self.panel_x + (self.panel_width - rating_surface.get_width()) // 2
            surface.blit(rating_alpha_surface, (rating_x, y_offset + 5))
    
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
        
        # UI properties - Enhanced styling
        self.panel_width = 420
        self.panel_height = 320
        self.panel_x = 20
        self.panel_y = SCREEN_H - self.panel_height - 20
        self.background_color = (245, 245, 250)
        self.border_color = (70, 130, 180)
        self.text_color = (40, 40, 40)
        self.header_color = (255, 255, 255)
        self.accent_color = (70, 130, 180)
        
        # Visibility and animation
        self.visible = True
        self.alpha = 255
        self.glow_alpha = 0
        self.glow_direction = 1
        self.panel_shadow_offset = 3
        
        # Enhanced instructions content
        self.instructions = [
            "🎮 GAME CONTROLS:",
            "• 🖱️ Click and drag vehicles to move them",
            "• 🎯 Get target vehicle (with characters) to exit",
            "• ⏯️ SPACE: Auto-solve with current algorithm",
            "• ⏸️ P: Pause/resume auto-solving",
            "• 🔄 R: Reset current level",
            "• ➡️ N: Next level • ⬅️ B: Previous level",
            "",
            "🧠 ALGORITHM SELECTION:",
            "• 1️⃣ BFS (Breadth-First Search)",
            "• 2️⃣ DFS (Depth-First Search)", 
            "• 3️⃣ A* (A-Star Search)",
            "• 4️⃣ Greedy Best-First Search",
            "",
            "💡 TIPS:",
            "• Watch algorithm statistics in real-time",
            "• Different algorithms have different strengths",
            "• Try all algorithms to compare performance!"
        ]
    
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 20)
            self.header_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except:
            self.font = pygame.font.SysFont('Arial', 20)
            self.header_font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 18)
    
    def toggle_visibility(self):
        """Bật/tắt hiển thị"""
        self.visible = not self.visible
    
    def update(self, dt):
        """Cập nhật animation effects"""
        # Glow effect animation
        self.glow_alpha += self.glow_direction * 2
        if self.glow_alpha >= 30:
            self.glow_direction = -1
        elif self.glow_alpha <= 0:
            self.glow_direction = 1
    
    def draw(self, surface):
        """Vẽ panel hướng dẫn với styling đẹp"""
        if not self.visible or self.alpha <= 0:
            return
        
        # Shadow effect
        shadow_surface = pygame.Surface((self.panel_width, self.panel_height))
        shadow_surface.fill((0, 0, 0))
        shadow_surface.set_alpha(int(self.alpha * 0.3))
        surface.blit(shadow_surface, (self.panel_x + self.panel_shadow_offset, 
                                     self.panel_y + self.panel_shadow_offset))
        
        # Main panel surface
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(self.alpha)
        
        # Gradient background
        for i in range(self.panel_height):
            color_intensity = 245 - int(i * 0.1)
            color = (color_intensity, color_intensity, color_intensity + 5)
            pygame.draw.line(panel_surface, color, (0, i), (self.panel_width, i))
        
        # Border with glow effect
        pygame.draw.rect(panel_surface, self.border_color,
                        (0, 0, self.panel_width, self.panel_height), 3)
        pygame.draw.rect(panel_surface, (200, 200, 200),
                        (3, 3, self.panel_width-6, self.panel_height-6), 1)
        
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Draw instructions
        y_offset = self.panel_y + 15
        x_offset = self.panel_x + 15
        line_height = 18
        
        for instruction in self.instructions:
            if instruction == "":
                y_offset += line_height // 2
                continue
            
            # Color coding for different types
            color = self.text_color
            font = self.font
            
            if instruction.startswith("🎮") or instruction.startswith("🧠"):
                # Section headers
                color = self.accent_color
                font = self.header_font
                # Draw header background
                header_rect = pygame.Rect(self.panel_x + 5, y_offset - 2, 
                                        self.panel_width - 10, 22)
                header_surface = pygame.Surface((header_rect.width, header_rect.height))
                header_surface.set_alpha(50)
                header_surface.fill(self.accent_color)
                surface.blit(header_surface, (header_rect.x, header_rect.y))
                
            elif instruction.startswith("💡"):
                color = (255, 140, 0)  # Orange for tips
                font = self.header_font
            elif instruction.startswith("•"):
                color = (60, 60, 60)  # Darker for bullet points
                font = self.font
            
            text_surface = font.render(instruction, True, color)
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
        
        # UI properties - Enhanced styling
        self.panel_width = 380
        self.panel_x = (SCREEN_W - self.panel_width) // 2
        self.panel_y = 60
        self.background_color = (245, 245, 250)
        self.border_color = (70, 130, 180)
        self.text_color = (40, 40, 40)
        self.shadow_offset = 2
        
        # Message types and colors - Enhanced
        self.message_colors = {
            'info': (70, 130, 180),
            'success': (60, 179, 113),
            'warning': (255, 165, 0),
            'error': (220, 20, 60),
            'algorithm': (138, 43, 226)  # New type for algorithm info
        }
        
        # Message icons
        self.message_icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'algorithm': '🧠'
        }
    
    def init_fonts(self):
        """Khởi tạo fonts"""
        try:
            self.font = pygame.font.Font(None, 22)
            self.header_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('Arial', 22)
            self.header_font = pygame.font.SysFont('Arial', 24)
    
    def add_message(self, text, msg_type='info', duration=None):
        """Thêm thông báo mới với styling đẹp"""
        if duration is None:
            duration = self.message_duration
        
        # Add icon to message
        icon = self.message_icons.get(msg_type, '')
        display_text = f"{icon} {text}" if icon else text
        
        message = {
            'text': display_text,
            'type': msg_type,
            'start_time': time.time(),
            'duration': duration,
            'alpha': 255,
            'slide_offset': -50  # For slide-in animation
        }
        
        self.messages.append(message)
        
        # Giữ số lượng messages trong giới hạn
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def update(self, dt):
        """Cập nhật thông báo với animation"""
        current_time = time.time()
        messages_to_remove = []
        
        for message in self.messages:
            elapsed = current_time - message['start_time']
            
            # Slide-in animation
            if message['slide_offset'] < 0:
                message['slide_offset'] = min(0, message['slide_offset'] + 300 * dt)
            
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
        """Vẽ thông báo với styling đẹp"""
        if not self.messages:
            return
            
        y_offset = self.panel_y
        
        for message in self.messages:
            if message['alpha'] <= 0:
                continue
            
            # Calculate message dimensions
            text_surface = self.font.render(message['text'], True, self.text_color)
            msg_width = text_surface.get_width() + 30
            msg_height = text_surface.get_height() + 16
            
            # Message position with slide animation
            msg_x = (SCREEN_W - msg_width) // 2 + message['slide_offset']
            
            # Shadow effect
            shadow_surface = pygame.Surface((msg_width, msg_height))
            shadow_surface.fill((0, 0, 0))
            shadow_surface.set_alpha(int(message['alpha'] * 0.3))
            surface.blit(shadow_surface, (msg_x + self.shadow_offset, y_offset + self.shadow_offset))
            
            # Message background
            bg_surface = pygame.Surface((msg_width, msg_height))
            bg_surface.set_alpha(message['alpha'])
            
            # Gradient background
            for i in range(msg_height):
                color_intensity = 245 - int(i * 0.2)
                color = (color_intensity, color_intensity, color_intensity + 5)
                pygame.draw.line(bg_surface, color, (0, i), (msg_width, i))
            
            # Border with type color
            border_color = self.message_colors.get(message['type'], self.border_color)
            pygame.draw.rect(bg_surface, border_color, (0, 0, msg_width, msg_height), 2)
            
            surface.blit(bg_surface, (msg_x, y_offset))
            
            # Message text
            text_alpha_surface = pygame.Surface(text_surface.get_size())
            text_alpha_surface.set_alpha(message['alpha'])
            text_alpha_surface.blit(text_surface, (0, 0))
            surface.blit(text_alpha_surface, (msg_x + 15, y_offset + 8))
            
            y_offset += msg_height + 8
    
    def show_algorithm_info(self, algorithm_name, time_taken, nodes_expanded, solution_length):
        """Hiển thị thông tin thuật toán với styling đẹp"""
        if solution_length > 0:
            info_text = f"{algorithm_name}: {time_taken:.3f}s | {nodes_expanded} nodes | {solution_length} moves"
            self.add_message(info_text, 'algorithm', 5.0)
        else:
            self.add_message(f"{algorithm_name}: No solution found", 'error', 4.0)
    
    def show_level_complete(self, level_num):
        """Hiển thị hoàn thành level"""
        self.add_message(f"Level {level_num} Complete!", 'success', 3.0)
    
    def show_no_solution(self):
        """Hiển thị không có giải pháp"""
        self.add_message("No solution found!", 'error', 3.0)
    
    def show_algorithm_selected(self, algorithm_name):
        """Hiển thị thuật toán được chọn"""
        self.add_message(f"Algorithm selected: {algorithm_name}", 'algorithm', 2.5)
    
    def show_solving_started(self, algorithm_name):
        """Hiển thị bắt đầu giải"""
        self.add_message(f"Solving with {algorithm_name}...", 'info', 2.0)
    
    def show_solving_paused(self):
        """Hiển thị tạm dừng"""
        self.add_message("Solving paused", 'warning', 2.0)
    
    def show_solving_resumed(self):
        """Hiển thị tiếp tục"""
        self.add_message("Solving resumed", 'info', 2.0)
    
    def show_level_reset(self):
        """Hiển thị reset level"""
        self.add_message("Level reset", 'info', 2.0)