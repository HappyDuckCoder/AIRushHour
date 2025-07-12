from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
from Animation.CharacterAnimation import Warrior, Archer, Monk
from UI.StatisticBoard import StatisticBoard
from constants import *
import math
import pygame
import random

class WinningScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.start_time = pygame.time.get_ticks()
        self.animation_phase = 0  
        self.phase_duration = [1500, 2000, 2500, 1000]  
        
        self.victory_title = Text("VICTORY!", GOLD, (SCREEN_W//2, -100), font=Font(96))
        self.congratulations = Text("Congratulations!", WHITE, (SCREEN_W//2, SCREEN_H + 50), font=Font(48))
        self.continue_text = Text("Press any key to continue", WHITE, (SCREEN_W//2, SCREEN_H + 100), font=Font(24))
        
        self.setup_characters()
        
        self.title_bounce_offset = 0
        self.text_fade_alpha = 0
        self.particles = []
        self.celebration_timer = 0
        
        self.characters_entered = False
        self.march_start_time = 0
        self.march_speed = 2.0
        
        self.statistics_board = StatisticBoard()

    def setup_characters(self):
        """Thiết lập các character cho victory animation"""
        character_size = 2.0  
        
        start_x = -150
        center_y = SCREEN_H // 2
        spacing = 120
        
        target_x = SCREEN_W // 2 - 180
        
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
                'skill_cooldown': 600,  
                'skill_variety': ['skill1', 'skill2', 'attack'],  
                'current_skill_index': 0,
                'last_skill_time': 0,
                'celebration_pattern': 0 
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
                'skill_cooldown': 700,  
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
                'skill_cooldown': 800,  
                'skill_variety': ['skill1', 'skill2', 'attack'],
                'current_skill_index': 2,
                'last_skill_time': 0,
                'celebration_pattern': 2
            }
        ]
        
        for char_data in self.characters:
            char = char_data['character']
            if hasattr(char, '_load_animations'):
                try:
                    char._load_animations()
                    char.set_state("run")
                except Exception as e:
                    print(f"Failed to load character animations: {e}")

    def update_characters(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        for char_data in self.characters:
            char = char_data['character']
            
            if self.animation_phase == 0:
                if elapsed > char_data['delay']:
                    progress = min(1.0, (elapsed - char_data['delay']) / (self.phase_duration[0] - char_data['delay']))
                    char_data['current_x'] = char_data['start_x'] + (char_data['target_x'] - char_data['start_x']) * self.ease_out(progress)
                    char.set_state("run")
            
            elif self.animation_phase == 1:
                char_data['current_x'] = char_data['target_x']
                
                self.handle_celebration_skills(char_data, current_time)
                
                bounce_speed = 0.01 + (char_data['celebration_pattern'] * 0.003)
                bounce = math.sin(elapsed * bounce_speed) * 10
                char.y = char_data['y'] + bounce
                
            elif self.animation_phase == 2:
                char_data['current_x'] = char_data['target_x']
                
                self.handle_celebration_skills(char_data, current_time)
                
                bounce = math.sin(elapsed * 0.008) * 5
                char.y = char_data['y'] + bounce
            
            elif self.animation_phase == 3:
                phase_elapsed = elapsed - sum(self.phase_duration[:3])
                progress = min(1.0, phase_elapsed / self.phase_duration[3])
                char_data['current_x'] = char_data['target_x'] + (char_data['final_x'] - char_data['target_x']) * self.ease_in(progress)
                char.set_state("run")
            
            char.x = char_data['current_x']
            char.update()

    def handle_celebration_skills(self, char_data, current_time):
        char = char_data['character']
        
        if current_time - char_data['last_skill_time'] >= char_data['skill_cooldown']:
            
            if char_data['celebration_pattern'] == 0:
                skill_name = char_data['skill_variety'][char_data['current_skill_index']]
                if hasattr(char, 'perform_skill'):
                    char.perform_skill()
                char_data['current_skill_index'] = (char_data['current_skill_index'] + 1) % len(char_data['skill_variety'])
                
            elif char_data['celebration_pattern'] == 1:
                if hasattr(char, 'perform_skill'):
                    char.perform_skill()
                if random.random() < 0.3:  
                    char_data['skill_cooldown'] = 200  
                else:
                    char_data['skill_cooldown'] = 700 
                    
            elif char_data['celebration_pattern'] == 2:
                if char_data['current_skill_index'] % 2 == 0:
                    if hasattr(char, 'perform_skill'):
                        char.perform_skill()
                else:
                    if hasattr(char, 'attack'):
                        char.attack()
                    elif hasattr(char, 'perform_skill'):
                        char.perform_skill()
                char_data['current_skill_index'] += 1
            
            base_cooldown = 600 if char_data['celebration_pattern'] == 0 else 700 if char_data['celebration_pattern'] == 1 else 800
            char_data['skill_cooldown'] = base_cooldown + random.randint(-100, 100)
            char_data['last_skill_time'] = current_time
        
        if current_time - char_data['last_skill_time'] > 300:  
            char.set_state("idle")

    def ease_out(self, t):
        return 1 - (1 - t) ** 3

    def ease_in(self, t):
        return t ** 3

    def update_victory_text(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if self.animation_phase == 2:
            phase_elapsed = elapsed - sum(self.phase_duration[:2])
            
            if phase_elapsed < 500:
                progress = phase_elapsed / 500
                self.victory_title.rect.centery = -100 + (SCREEN_H // 2 - 200) * self.ease_out(progress)
            else:
                self.victory_title.rect.centery = SCREEN_H // 2 - 200
                
            if phase_elapsed > 300 and phase_elapsed < 800:
                progress = (phase_elapsed - 300) / 500
                self.congratulations.rect.centery = SCREEN_H + 50 - (SCREEN_H // 2 - 150) * self.ease_out(progress)
            elif phase_elapsed >= 800:
                self.congratulations.rect.centery = SCREEN_H // 2 - 150
                
            if phase_elapsed > 1000:
                self.text_fade_alpha = min(255, (phase_elapsed - 1000) / 500 * 255)
                
            if phase_elapsed > 1200:
                target_alpha = min(255, (phase_elapsed - 1200) / 800 * 255)
                self.statistics_board.set_alpha(target_alpha)
            
            if phase_elapsed > 500:
                self.title_bounce_offset = math.sin((phase_elapsed - 500) * 0.008) * 5

    def create_particles(self):
        if self.animation_phase == 1 or self.animation_phase == 2:
            for _ in range(5):  
                self.particles.append({
                    'x': SCREEN_W // 2 + (random.random() - 0.5) * 300,
                    'y': SCREEN_H // 2 + (random.random() - 0.5) * 150,
                    'vx': (random.random() - 0.5) * 6,
                    'vy': (random.random() - 0.5) * 6,
                    'life': 90, 
                    'color': random.choice([GOLD, WHITE, YELLOW])  
                })
        
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, surface):
        for particle in self.particles:
            alpha = int(255 * particle['life'] / 90)
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 3)

    def draw_victory_background(self, surface):
        self.draw_background(surface, "winning")
        
        if self.animation_phase >= 2:
            glow_surface = pygame.Surface((SCREEN_W, SCREEN_H))
            glow_surface.set_alpha(30)
            glow_surface.fill(GOLD)
            surface.blit(glow_surface, (0, 0))

    def draw_victory_elements(self, surface):
        for char_data in self.characters:
            char = char_data['character']
            try:
                char.draw(surface)
            except Exception as e:
                print(f"Error drawing character: {e}")
        
        self.draw_particles(surface)
        
        if self.animation_phase >= 2:
            title_rect = self.victory_title.rect.copy()
            title_rect.centery += self.title_bounce_offset
            victory_surface = self.victory_title.font.render(self.victory_title.text, self.victory_title.color)
            surface.blit(victory_surface, title_rect)
            
            congrats_surface = self.congratulations.font.render(self.congratulations.text, self.congratulations.color)
            surface.blit(congrats_surface, self.congratulations.rect)
            
            if self.text_fade_alpha > 0:
                continue_surface = self.continue_text.font.render(self.continue_text.text, self.continue_text.color)
                continue_surface.set_alpha(self.text_fade_alpha)
                continue_rect = self.continue_text.rect.copy()
                continue_rect.centery = SCREEN_H - 50
                surface.blit(continue_surface, continue_rect)
            
            self.statistics_board.draw(surface)

    def update_animation_phase(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        phase_total = 0
        for i, duration in enumerate(self.phase_duration):
            phase_total += duration
            if elapsed < phase_total:
                self.animation_phase = i
                return
        
        self.animation_phase = 3

    def draw(self, surface):
        self.draw_victory_background(surface)
        self.draw_victory_elements(surface)

    def update(self):
        self.update_animation_phase()
        self.update_characters()
        self.update_victory_text()
        self.create_particles()
        return True

    def on_enter(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('victory')
        
        self.statistics_board.reload_statistics()
        
        self.start_time = pygame.time.get_ticks()
        self.animation_phase = 0
        self.particles = []
        self.text_fade_alpha = 0
        self.title_bounce_offset = 0
        self.statistics_board.set_alpha(0)
        
        for char_data in self.characters:
            char_data['current_x'] = char_data['start_x']
            char_data['character'].x = char_data['start_x']
            char_data['character'].y = char_data['y']
            char_data['last_skill_time'] = 0
            char_data['skill_timer'] = 0
            char_data['current_skill_index'] = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            
            if self.animation_phase < 2:
                self.start_time = current_time - sum(self.phase_duration[:2])
                self.animation_phase = 2
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
            
            elif self.animation_phase == 2 and elapsed > sum(self.phase_duration[:2]) + 1000:
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen("level_select")  
            
            elif self.animation_phase == 3:
                audio_manager = AudioManager.get_instance()
                audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen("level_select")

    def on_exit(self):
        audio_manager = AudioManager.get_instance()
        audio_manager.stop_background_music()