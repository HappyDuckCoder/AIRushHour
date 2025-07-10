from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
from Animation.CharacterAnimation import Warrior, Archer, Monk
from UI.StatisticBoard import StatisticBoard
from constants import *
import math
import pygame
import random

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
        
        # Statistics board
        self.statistics_board = StatisticBoard()

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
                'delay': 0,
                'skill_timer': 0,
                'skill_cooldown': 600,  # 600ms cooldown between skills
                'skill_variety': ['skill1', 'skill2', 'attack'],  # Different skills to rotate
                'current_skill_index': 0,
                'last_skill_time': 0,
                'celebration_pattern': 0  # Different celebration patterns
            },
            {
                'character': Monk(start_x, center_y, character_size),
                'start_x': start_x,
                'target_x': target_x + spacing,
                'final_x': SCREEN_W + 150,
                'current_x': start_x,
                'y': center_y,
                'delay': 200,
                'skill_timer': 0,
                'skill_cooldown': 700,  # Different cooldown for variety
                'skill_variety': ['skill1', 'skill2', 'attack'],
                'current_skill_index': 1,
                'last_skill_time': 0,
                'celebration_pattern': 1
            },
            {
                'character': Warrior(start_x, center_y + 60, character_size),
                'start_x': start_x,
                'target_x': target_x + spacing * 2,
                'final_x': SCREEN_W + 150,
                'current_x': start_x,
                'y': center_y + 60,
                'delay': 400,
                'skill_timer': 0,
                'skill_cooldown': 800,  # Different cooldown for variety
                'skill_variety': ['skill1', 'skill2', 'attack'],
                'current_skill_index': 2,
                'last_skill_time': 0,
                'celebration_pattern': 2
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
            
            # Phase 1: Celebration at center - MORE SKILLS HERE!
            elif self.animation_phase == 1:
                char_data['current_x'] = char_data['target_x']
                
                # Enhanced celebration with more frequent skills
                self.handle_celebration_skills(char_data, current_time)
                
                # Bounce effect
                bounce_speed = 0.01 + (char_data['celebration_pattern'] * 0.003)
                bounce = math.sin(elapsed * bounce_speed) * 10
                char.y = char_data['y'] + bounce
                
            # Phase 2: Victory text appears, characters still celebrating with skills
            elif self.animation_phase == 2:
                char_data['current_x'] = char_data['target_x']
                
                # Continue skills during victory text phase
                self.handle_celebration_skills(char_data, current_time)
                
                # Smaller bounce during text phase
                bounce = math.sin(elapsed * 0.008) * 5
                char.y = char_data['y'] + bounce
            
            # Phase 3: Characters exit to right
            elif self.animation_phase == 3:
                phase_elapsed = elapsed - sum(self.phase_duration[:3])
                progress = min(1.0, phase_elapsed / self.phase_duration[3])
                char_data['current_x'] = char_data['target_x'] + (char_data['final_x'] - char_data['target_x']) * self.ease_in(progress)
                char.set_state("run")
            
            # Update character position
            char.x = char_data['current_x']
            char.update()

    def handle_celebration_skills(self, char_data, current_time):
        """Xử lý skills cho celebration phase"""
        char = char_data['character']
        
        # Check if it's time for next skill
        if current_time - char_data['last_skill_time'] >= char_data['skill_cooldown']:
            
            # Perform skill based on current pattern
            if char_data['celebration_pattern'] == 0:
                # Pattern 0: Rotate through all skills
                skill_name = char_data['skill_variety'][char_data['current_skill_index']]
                if hasattr(char, 'perform_skill'):
                    char.perform_skill()
                char_data['current_skill_index'] = (char_data['current_skill_index'] + 1) % len(char_data['skill_variety'])
                
            elif char_data['celebration_pattern'] == 1:
                # Pattern 1: Random skills
                if hasattr(char, 'perform_skill'):
                    char.perform_skill()
                # Sometimes do multiple skills in rapid succession
                if random.random() < 0.3:  # 30% chance for double skill
                    char_data['skill_cooldown'] = 200  # Very short cooldown for next skill
                else:
                    char_data['skill_cooldown'] = 700  # Normal cooldown
                    
            elif char_data['celebration_pattern'] == 2:
                # Pattern 2: Alternating between skill and attack
                if char_data['current_skill_index'] % 2 == 0:
                    if hasattr(char, 'perform_skill'):
                        char.perform_skill()
                else:
                    if hasattr(char, 'attack'):
                        char.attack()
                    elif hasattr(char, 'perform_skill'):
                        char.perform_skill()
                char_data['current_skill_index'] += 1
            
            # Add some randomness to cooldown to prevent synchronization
            base_cooldown = 600 if char_data['celebration_pattern'] == 0 else 700 if char_data['celebration_pattern'] == 1 else 800
            char_data['skill_cooldown'] = base_cooldown + random.randint(-100, 100)
            char_data['last_skill_time'] = current_time
        
        # Set idle state between skills
        if current_time - char_data['last_skill_time'] > 300:  # After 300ms from skill
            char.set_state("idle")

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
                target_alpha = min(255, (phase_elapsed - 1200) / 800 * 255)
                self.statistics_board.set_alpha(target_alpha)
            
            # Bounce effect for title
            if phase_elapsed > 500:
                self.title_bounce_offset = math.sin((phase_elapsed - 500) * 0.008) * 5

    def create_particles(self):
        """Tạo hiệu ứng particle cho celebration"""
        if self.animation_phase == 1 or self.animation_phase == 2:
            # Create more particles during celebration
            for _ in range(5):  # Increased from 3 to 5
                self.particles.append({
                    'x': SCREEN_W // 2 + (random.random() - 0.5) * 300,
                    'y': SCREEN_H // 2 + (random.random() - 0.5) * 150,
                    'vx': (random.random() - 0.5) * 6,
                    'vy': (random.random() - 0.5) * 6,
                    'life': 90,  # Longer life
                    'color': random.choice([GOLD, WHITE, YELLOW])  # More color variety
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
            alpha = int(255 * particle['life'] / 90)
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
            self.statistics_board.draw(surface)

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
        self.statistics_board.reload_statistics()
        
        # Reset animation
        self.start_time = pygame.time.get_ticks()
        self.animation_phase = 0
        self.particles = []
        self.text_fade_alpha = 0
        self.title_bounce_offset = 0
        self.statistics_board.set_alpha(0)
        
        # Reset character positions và skill timers
        for char_data in self.characters:
            char_data['current_x'] = char_data['start_x']
            char_data['character'].x = char_data['start_x']
            char_data['character'].y = char_data['y']
            char_data['last_skill_time'] = 0
            char_data['skill_timer'] = 0
            char_data['current_skill_index'] = 0

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
                self.screen_manager.set_screen("level_select")  # Return to main menu
            
            # If in exit phase, immediately go to menu
            elif self.animation_phase == 3:
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen("level_select")

    def on_exit(self):
        """Called when exiting victory screen"""
        # Stop victory music
        audio_manager = AudioManager.get_instance()
        audio_manager.stop_background_music()