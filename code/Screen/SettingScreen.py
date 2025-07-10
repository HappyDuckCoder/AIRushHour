from Screen.BaseScreen import Screen
from UI.Button import Button
from UI.Text import Text, Font
from Audio.AudioManager import AudioManager
from constants import *
import pygame

# ===============================
# Setting Screen
# ===============================
class SettingScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        
        # Audio Manager instance
        self.audio_manager = AudioManager.get_instance()
        
        # Title
        self.title = Text("SETTINGS", WHITE, (SCREEN_W//2, 100), font=Font(48))
        
        # Sound toggle button
        self.sound_toggle_btn = Button(
            "SOUND: ON" if self.audio_manager.music_enabled else "SOUND: OFF",
            (SCREEN_W//2 - 100, 200), 200, 50, GREEN if self.audio_manager.music_enabled else RED
        )
        
        # Volume controls
        self.volume_text = Text("VOLUME", WHITE, (SCREEN_W//2, 280), font=Font(32))
        self.volume_down_btn = Button("-", (SCREEN_W//2 - 120, 320), 50, 40, BLUE)
        self.volume_up_btn = Button("+", (SCREEN_W//2 + 70, 320), 50, 40, BLUE)
        self.volume_value_text = Text(f"{int(self.audio_manager.music_volume * 100)}%", WHITE, (SCREEN_W//2, 340), font=Font(28))
        
        # Back button
        self.back_btn = Button("BACK", (SCREEN_W//2 - 75, 450), 150, 50, GRAY)
        
    def update_sound_button(self):
        """Update sound toggle button text and color"""
        if self.audio_manager.music_enabled:
            self.sound_toggle_btn.text = "SOUND: ON"
            self.sound_toggle_btn.color = GREEN
        else:
            self.sound_toggle_btn.text = "SOUND: OFF"
            self.sound_toggle_btn.color = RED
        # Recreate button surface with new text and color
        self.sound_toggle_btn.set_text(self.sound_toggle_btn.text)
        self.sound_toggle_btn.set_color(self.sound_toggle_btn.color)
    
    def update_volume_text(self):
        """Update volume percentage text"""
        self.volume_value_text.text = f"{int(self.audio_manager.music_volume * 100)}%"
        self.volume_value_text.set_text(self.volume_value_text.text)
    
    def draw_setting_background(self, surface):
        """Draw setting screen background"""
        self.draw_background(surface, "menu")  
        
        # Add semi-transparent overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
    
    def draw(self, surface):
        """Draw the setting screen"""
        self.draw_setting_background(surface)        
        self.title.draw(surface)
        self.sound_toggle_btn.draw(surface)
        self.volume_text.draw(surface)
        self.volume_down_btn.draw(surface)
        self.volume_up_btn.draw(surface)
        self.volume_value_text.draw(surface)
        
        # Draw volume bar
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_W//2 - bar_width//2
        bar_y = 380
        # Background bar
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Volume bar
        volume_bar_width = int(bar_width * self.audio_manager.music_volume)
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, volume_bar_width, bar_height))
        
        # Draw back button
        self.back_btn.draw(surface)
    
    def update(self):
        self.sound_toggle_btn.update()
        self.volume_down_btn.update()
        self.volume_up_btn.update()
        self.back_btn.update()
        return True
    
    def on_enter(self):
        """Called when entering setting screen"""
        pass
    
    def handle_event(self, event):
        # Update all buttons
        self.sound_toggle_btn.handle_event(event)
        self.volume_down_btn.handle_event(event)
        self.volume_up_btn.handle_event(event)
        self.back_btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Sound toggle
            if self.sound_toggle_btn.hit(event.pos):
                self.audio_manager.toggle_music()
                self.update_sound_button()
                if self.audio_manager.music_enabled:
                    self.audio_manager.play_sound_effect('button_click')
            
            # Volume down
            elif self.volume_down_btn.hit(event.pos):
                self.audio_manager.decrease_volume(0.1)
                self.update_volume_text()
                if self.audio_manager.music_enabled:
                    self.audio_manager.play_sound_effect('button_click')
            
            # Volume up
            elif self.volume_up_btn.hit(event.pos):
                self.audio_manager.increase_volume(0.1)
                self.update_volume_text()
                if self.audio_manager.music_enabled:
                    self.audio_manager.play_sound_effect('button_click')
            
            # Back button
            elif self.back_btn.hit(event.pos):
                if self.audio_manager.music_enabled:
                    self.audio_manager.play_sound_effect('button_click')
                self.screen_manager.set_screen('menu')