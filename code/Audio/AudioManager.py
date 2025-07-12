import pygame
import threading
import os
from typing import Dict, Optional
from constants import *

class AudioManager:
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AudioManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AudioManager._initialized:
            return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"Lỗi khởi tạo audio: {e}")
            return
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_enabled = True
        self.sfx_enabled = True
        self.background_music = {
            'intro': 'assets/audio/intro_music.mp3',
            'menu': 'assets/audio/menu_music.mp3', 
            'level_select': 'assets/audio/level_select_music.mp3',
            'game': 'assets/audio/game_music.mp3'
        }
        self.sound_effects = {
            'button_click': 'assets/audio/button_click.wav',
            'button_hover': 'assets/audio/button_hover.wav',
            'victory': 'assets/audio/victory.wav',
            'car_move': 'assets/audio/car_move.wav',
        }
        self.loaded_sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        self.current_screen: Optional[str] = None
        self.audio_thread = None
        self.music_fade_thread = None
        self.sound_lock = threading.Lock()
        self._load_all_sounds()
        AudioManager._initialized = True
    
    @classmethod
    def get_instance(cls):
        return cls()
    
    def _load_all_sounds(self):
        for name, path in self.sound_effects.items():
            try:
                if os.path.exists(path):
                    self.loaded_sounds[name] = pygame.mixer.Sound(path)
                    self.loaded_sounds[name].set_volume(self.sfx_volume)
                else:
                    print(f"Warning: Sound file not found: {path}")
            except pygame.error as e:
                print(f"Error loading sound {name}: {e}")
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def increase_volume(self, amount):
        self.music_volume = min(1.0, self.music_volume + amount)
        pygame.mixer.music.set_volume(self.music_volume)

    def decrease_volume(self, amount):
        self.music_volume = max(0.0, self.music_volume - amount)
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.loaded_sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_music(self):
        if self.music_enabled:
            self.music_enabled = False
            pygame.mixer.music.stop()
        else:
            self.music_enabled = True
            if self.current_screen:
                self.play_background_music(self.current_screen, fade_in=True)
                pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
    
    def play_background_music(self, screen_name, fade_in=True):
        if not self.music_enabled:
            return
        if screen_name not in self.background_music:
            return
        music_path = self.background_music[screen_name]
        if self.current_music != music_path:
            if os.path.exists(music_path):
                try:
                    if pygame.mixer.music.get_busy():
                        self._fade_out_music(500)
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    if fade_in:
                        pygame.mixer.music.play(-1, fade_ms=1000)
                    else:
                        pygame.mixer.music.play(-1)
                    self.current_music = music_path
                    self.current_screen = screen_name
                except pygame.error as e:
                    print(f"Error playing background music: {e}")
            else:
                print(f"Warning: Music file not found: {music_path}")
    
    def _fade_out_music(self, duration):
        if self.music_fade_thread and self.music_fade_thread.is_alive():
            return
        def fade_out():
            pygame.mixer.music.fadeout(duration)
        self.music_fade_thread = threading.Thread(target=fade_out, daemon=True)
        self.music_fade_thread.start()
    
    def play_sound_effect(self, effect_name, volume_multiplier=1.0):
        if not self.sfx_enabled or effect_name not in self.loaded_sounds:
            return
        def play_sound():
            try:
                sound = self.loaded_sounds[effect_name]
                sound.set_volume(self.sfx_volume * volume_multiplier)
                sound.play()
            except pygame.error as e:
                print(f"Error playing sound effect {effect_name}: {e}")
        self.audio_thread = threading.Thread(target=play_sound, daemon=True)
        self.audio_thread.start()
    
    def play_button_click(self):
        self.play_sound_effect('button_click')
    
    def play_button_hover(self):
        self.play_sound_effect('button_hover', 0.3)
    
    def play_game_reset(self):
        self.play_sound_effect('game_reset')
    
    def play_solve_start(self):
        self.play_sound_effect('solve_start')
    
    def play_victory(self):
        self.play_sound_effect('victory')
    
    def play_car_move(self):
        self.play_sound_effect('car_move', 0.5)
    
    def stop_all_sounds(self):
        pygame.mixer.music.stop()
        pygame.mixer.stop()
    
    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
    
    def resume_music(self):
        pygame.mixer.music.unpause()
    
    def cleanup(self):
        self.stop_all_sounds()
        pygame.mixer.quit()
