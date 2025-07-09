from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from Graphic.Graphic import gfx, pygame
from Audio.AudioManager import AudioManager
from Animation.CharacterAnimation import Warrior, Archer, Monk
from constants import *
import math
import random
import json
import os

# ===============================
# Winning Screen
# ===============================
class WinningScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.start_time = pygame.time.get_ticks()
        self.animation_phase = 0  # 0: characters enter, 1: celebration, 2: victory text, 3: exit
        self.phase_duration = [1500, 2000, 2500, 1000]  # Duration for each phase
        
        # Victory text elements
        self.victory_title = Text("VICTORY!", GOLD, (SCREEN_W//2, -100), font=Font(96))
        self.congratulations = Text("Congratulations!", WHITE, (SCREEN_W//2, SCREEN_H + 50), font=Font(48))
        self.continue_text = Text("Press any key to continue", WHITE, (SCREEN_W//2, SCREEN_H + 100), font=Font(24))
        
        # Character setup
        self.setup_characters()
        
        # Animation variables
        self.title_bounce_offset = 0
        self.text_fade_alpha = 0
        self.particles = []
        self.celebration_timer = 0
        
        # Victory march variables
        self.characters_entered = False
        self.march_start_time = 0
        self.march_speed = 2.0
        
        # Statistics
        self.statistics = None
        self.load_statistics()
        
        # Statistics display
        self.stats_panel_alpha = 0
        self.stats_panel_target_alpha = 255
        self.stats_fade_speed = 3

    def load_statistics(self):
        """Load statistics from file"""
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            stats_file = os.path.join(base_path, 'statistic.txt')
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.statistics = json.load(f)
                print(f"Loaded statistics: {self.statistics}")
            else:
                print("No statistics file found")
                self.statistics = None
        except Exception as e:
            print(f"Error loading statistics: {e}")
            self.statistics = None

    def setup_characters(self):
        """Thiết lập các character cho victory animation"""
        character_size = 2.0  # Larger size for victory screen
        
        # Starting positions (off-screen left)
        start_x = -150
        center_y = SCREEN_H // 2
        spacing = 120
        
        # Target positions (center of screen)
        target_x = SCREEN_W // 2 - 180
        
        # Create characters
        self.characters = [
            {
                'character': Archer(start_x, center_y - 60, character_size),
                'start_x': start_x,
                'target_x': target_x,
                'final_x': SCREEN_W + 150,
                'current_x': start_x,
                'y': center_y - 60,
                'delay': 0
            },
            {
                'character': Monk(start_x, center_y, character_size),
                'start_x': start_x,
                'target_x': target_x + spacing,
                'final_x': SCREEN_W + 150,
                'current_x': start_x,
                'y': center_y,
                'delay': 200
            },
            {
                'character': Warrior(start_x, center_y + 60, character_size),
                'start_x': start_x,
                'target_x': target_x + spacing * 2,
                'final_x': SCREEN_W + 150,
                'current_x': start_x,
                'y': center_y + 60,
                'delay': 400
            }
        ]
        
        # Initialize characters
        for char_data in self.characters:
            char = char_data['character']
            if hasattr(char, '_load_animations'):
                try:
                    char._load_animations()
                    char.set_state("run")
                except Exception as e:
                    print(f"Failed to load character animations: {e}")

    def update_characters(self):
        """Cập nhật vị trí và animation của characters"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        for char_data in self.characters:
            char = char_data['character']
            
            # Phase 0: Characters enter from left
            if self.animation_phase == 0:
                if elapsed > char_data['delay']:
                    progress = min(1.0, (elapsed - char_data['delay']) / (self.phase_duration[0] - char_data['delay']))
                    char_data['current_x'] = char_data['start_x'] + (char_data['target_x'] - char_data['start_x']) * self.ease_out(progress)
                    char.set_state("run")
            
            # Phase 1: Celebration at center
            elif self.animation_phase == 1:
                char_data['current_x'] = char_data['target_x']
                # Bounce effect
                bounce = math.sin(elapsed * 0.01) * 10
                char.y = char_data['y'] + bounce
                char.set_state("idle")
                
                # Periodic skill animations
                if elapsed % 1000 < 100:  # Every second, for 100ms
                    char.perform_skill()
            
            # Phase 2: Victory text appears, characters still celebrating
            elif self.animation_phase == 2:
                char_data['current_x'] = char_data['target_x']
                char.set_state("idle")
            
            # Phase 3: Characters exit to right
            elif self.animation_phase == 3:
                phase_elapsed = elapsed - sum(self.phase_duration[:3])
                progress = min(1.0, phase_elapsed / self.phase_duration[3])
                char_data['current_x'] = char_data['target_x'] + (char_data['final_x'] - char_data['target_x']) * self.ease_in(progress)
                char.set_state("run")
            
            # Update character position
            char.x = char_data['current_x']
            char.update()

    def ease_out(self, t):
        """Easing function for smooth animation"""
        return 1 - (1 - t) ** 3

    def ease_in(self, t):
        """Easing function for smooth animation"""
        return t ** 3

    def update_victory_text(self):
        """Cập nhật animation của victory text"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        # Phase 2: Victory text animation
        if self.animation_phase == 2:
            phase_elapsed = elapsed - sum(self.phase_duration[:2])
            
            # Title drops down
            if phase_elapsed < 500:
                progress = phase_elapsed / 500
                self.victory_title.rect.centery = -100 + (SCREEN_H // 2 - 200) * self.ease_out(progress)
            else:
                self.victory_title.rect.centery = SCREEN_H // 2 - 200
                
            # Congratulations text rises up
            if phase_elapsed > 300 and phase_elapsed < 800:
                progress = (phase_elapsed - 300) / 500
                self.congratulations.rect.centery = SCREEN_H + 50 - (SCREEN_H // 2 - 150) * self.ease_out(progress)
            elif phase_elapsed >= 800:
                self.congratulations.rect.centery = SCREEN_H // 2 - 150
                
            # Continue text fades in
            if phase_elapsed > 1000:
                self.text_fade_alpha = min(255, (phase_elapsed - 1000) / 500 * 255)
                
            # Statistics panel fades in
            if phase_elapsed > 1200:
                self.stats_panel_alpha = min(255, (phase_elapsed - 1200) / 800 * 255)
            
            # Bounce effect for title
            if phase_elapsed > 500:
                self.title_bounce_offset = math.sin((phase_elapsed - 500) * 0.008) * 5

    def create_particles(self):
        """Tạo hiệu ứng particle cho celebration"""
        if self.animation_phase == 1:
            # Create golden particles
            for _ in range(3):
                self.particles.append({
                    'x': SCREEN_W // 2 + (random.random() - 0.5) * 200,
                    'y': SCREEN_H // 2 + (random.random() - 0.5) * 100,
                    'vx': (random.random() - 0.5) * 4,
                    'vy': (random.random() - 0.5) * 4,
                    'life': 60,
                    'color': GOLD
                })
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        """Vẽ particle effects"""
        for particle in self.particles:
            alpha = int(255 * particle['life'] / 60)
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 3)

    def draw_victory_background(self, surface):
        """Vẽ background cho victory screen"""
        # Gradient background
        self.draw_background(surface, "winning")
        
        # Victory glow effect
        if self.animation_phase >= 2:
            glow_surface = pygame.Surface((SCREEN_W, SCREEN_H))
            glow_surface.set_alpha(30)
            glow_surface.fill(GOLD)
            surface.blit(glow_surface, (0, 0))

    def draw_statistics_panel(self, surface):
        """Vẽ panel thống kê"""
        if not self.statistics or self.stats_panel_alpha <= 0:
            return
            
        # Panel dimensions and position
        panel_width = 400
        panel_height = 280
        panel_x = (SCREEN_W - panel_width) // 2
        panel_y = SCREEN_H // 2 + 50
        
        # Create panel surface
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(self.stats_panel_alpha)
        
        # Background with gradient effect
        for i in range(panel_height):
            color_intensity = 240 - int(i * 0.3)
            color = (color_intensity, color_intensity, color_intensity + 10)
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))
        
        # Border
        pygame.draw.rect(panel_surface, GOLD, (0, 0, panel_width, panel_height), 3)
        pygame.draw.rect(panel_surface, (200, 200, 200), (3, 3, panel_width-6, panel_height-6), 1)
        
        # Title
        title_font = pygame.font.Font(None, 32)
        title_text = title_font.render("PUZZLE SOLVED!", True, GOLD)
        title_rect = title_text.get_rect(center=(panel_width//2, 25))
        panel_surface.blit(title_text, title_rect)
        
        # Statistics
        stats_font = pygame.font.Font(None, 24)
        y_offset = 60
        line_height = 28
        
        # Format statistics data
        stats_data = [
            ("Level:", str(self.statistics.get('level', 'N/A'))),
            ("Algorithm:", self.statistics.get('algorithm', 'N/A')),
            ("Time:", f"{self.statistics.get('time_executed', 0):.3f}s"),
            ("Nodes Expanded:", str(self.statistics.get('nodes_expanded', 0))),
            ("Solution Length:", str(self.statistics.get('solution_length', 0))),
            ("Status:", "SOLVED" if self.statistics.get('solved', False) else "FAILED")
        ]
        
        for label, value in stats_data:
            # Label
            label_text = stats_font.render(label, True, (80, 80, 80))
            panel_surface.blit(label_text, (20, y_offset))
            
            # Value
            value_color = (40, 40, 40)
            if label == "Status:":
                value_color = (60, 179, 113) if value == "SOLVED" else (220, 20, 60)
            elif label == "Algorithm:":
                value_color = (70, 130, 180)
            
            value_text = stats_font.render(value, True, value_color)
            panel_surface.blit(value_text, (180, y_offset))
            
            y_offset += line_height
        
        # Performance rating
        if self.statistics.get('solved', False):
            time_taken = self.statistics.get('time_executed', 0)
            nodes_expanded = self.statistics.get('nodes_expanded', 0)
            
            # Simple rating system
            if time_taken < 0.1 and nodes_expanded < 100:
                rating = "★★★ EXCELLENT"
                rating_color = GOLD
            elif time_taken < 0.5 and nodes_expanded < 500:
                rating = "★★☆ GOOD"
                rating_color = (70, 130, 180)
            else:
                rating = "★☆☆ COMPLETED"
                rating_color = (128, 128, 128)
            
            rating_text = stats_font.render(rating, True, rating_color)
            rating_rect = rating_text.get_rect(center=(panel_width//2, panel_height - 25))
            panel_surface.blit(rating_text, rating_rect)
        
        surface.blit(panel_surface, (panel_x, panel_y))

    def draw_victory_elements(self, surface):
        """Vẽ các elements của victory screen"""
        # Draw characters
        for char_data in self.characters:
            char = char_data['character']
            try:
                char.draw(surface)
            except Exception as e:
                print(f"Error drawing character: {e}")
        
        # Draw particles
        self.draw_particles(surface)
        
        # Draw victory text
        if self.animation_phase >= 2:
            # Victory title with bounce
            title_rect = self.victory_title.rect.copy()
            title_rect.centery += self.title_bounce_offset
            victory_surface = self.victory_title.font.render(self.victory_title.text, self.victory_title.color)
            surface.blit(victory_surface, title_rect)
            
            # Congratulations text
            congrats_surface = self.congratulations.font.render(self.congratulations.text, self.congratulations.color)
            surface.blit(congrats_surface, self.congratulations.rect)
            
            # Continue text with fade
            if self.text_fade_alpha > 0:
                continue_surface = self.continue_text.font.render(self.continue_text.text, self.continue_text.color)
                continue_surface.set_alpha(self.text_fade_alpha)
                continue_rect = self.continue_text.rect.copy()
                continue_rect.centery = SCREEN_H - 50
                surface.blit(continue_surface, continue_rect)
            
            # Draw statistics panel
            self.draw_statistics_panel(surface)

    def update_animation_phase(self):
        """Cập nhật phase của animation"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        phase_total = 0
        for i, duration in enumerate(self.phase_duration):
            phase_total += duration
            if elapsed < phase_total:
                self.animation_phase = i
                return
        
        # All phases completed
        self.animation_phase = 3

    def draw(self, surface):
        """Vẽ toàn bộ victory screen"""
        self.draw_victory_background(surface)
        self.draw_victory_elements(surface)

    def update(self):
        """Cập nhật victory screen"""
        self.update_animation_phase()
        self.update_characters()
        self.update_victory_text()
        self.create_particles()
        return True

    def on_enter(self):
        """Called when entering victory screen"""
        # Sử dụng AudioManager singleton để phát nhạc nền victory
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('victory')
        
        # Reload statistics
        self.load_statistics()
        
        # Reset animation
        self.start_time = pygame.time.get_ticks()
        self.animation_phase = 0
        self.particles = []
        self.text_fade_alpha = 0
        self.title_bounce_offset = 0
        self.stats_panel_alpha = 0
        
        # Reset character positions
        for char_data in self.characters:
            char_data['current_x'] = char_data['start_x']
            char_data['character'].x = char_data['start_x']
            char_data['character'].y = char_data['y']

    def handle_event(self, event):
        """Xử lý events"""
        # Cho phép skip victory animation hoặc continue
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            
            # If still in early phases, skip to victory text
            if self.animation_phase < 2:
                self.start_time = current_time - sum(self.phase_duration[:2])
                self.animation_phase = 2
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
            
            # If victory text is showing, allow continue
            elif self.animation_phase == 2 and elapsed > sum(self.phase_duration[:2]) + 1000:
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen("menu")  # Return to main menu
            
            # If in exit phase, immediately go to menu
            elif self.animation_phase == 3:
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen("menu")

    def on_exit(self):
        """Called when exiting victory screen"""
        # Stop victory music
        audio_manager = AudioManager.get_instance()
        audio_manager.stop_background_music()