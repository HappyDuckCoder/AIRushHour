import pygame
from constants import *

class ResourceManager:
    _images = {}
    _sounds = {}
    _fonts = {}

    @staticmethod
    def init():
        """Khởi tạo pygame nếu chưa có."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    @staticmethod
    def load_image(name, path, size=None, rotate=None):
        """Tải và xử lý ảnh (scale, rotate nếu có)."""
        try:
            image = pygame.image.load(path).convert_alpha()
            if rotate:
                image = pygame.transform.rotate(image, rotate)
            if size:
                image = pygame.transform.scale(image, size)
            ResourceManager._images[name] = image
        except pygame.error as e:
            print(f"[ERROR] Cannot load image '{name}' from '{path}': {e}")

    @staticmethod
    def load_sound(name, path):
        """Tải âm thanh."""
        try:
            sound = pygame.mixer.Sound(path)
            ResourceManager._sounds[name] = sound
        except pygame.error as e:
            print(f"[ERROR] Cannot load sound '{name}' from '{path}': {e}")

    @staticmethod
    def load_font(name, path, size):
        """Tải font."""
        try:
            font = pygame.font.Font(path, size)
            ResourceManager._fonts[name] = font
        except pygame.error as e:
            print(f"[ERROR] Cannot load font '{name}' from '{path}': {e}")

    @staticmethod
    def get_image(name):
        return ResourceManager._images.get(name)

    @staticmethod
    def get_sound(name):
        return ResourceManager._sounds.get(name)

    @staticmethod
    def get_font(name):
        return ResourceManager._fonts.get(name)

    @staticmethod
    def upload_all():
        """Load all necessary game resources"""
        # Background
        ResourceManager.load_image("background", "assets/bg.png", size=(SCREEN_W, SCREEN_H))
        
        # Map overlay
        map_size = MAP_N * TILE
        ResourceManager.load_image("map", "assets/map.png", size=(map_size, map_size))

        # Vehicles
        ResourceManager.load_image("target", "assets/target.png", size=(TILE * 2, TILE))
        
        ResourceManager.load_image("v2_h", "assets/vh2h.png", size=(TILE * 2, TILE))
        ResourceManager.load_image("v2_v", "assets/vh2h.png", size=(TILE, TILE * 2), rotate=90)
        
        ResourceManager.load_image("v3_h", "assets/vh3h.png", size=(TILE * 3, TILE))
        ResourceManager.load_image("v3_v", "assets/vh3h.png", size=(TILE, TILE * 3), rotate=90)

    @staticmethod
    def unload_all():
        """Xóa hết tài nguyên đã load (nếu cần reset)."""
        ResourceManager._images.clear()
        ResourceManager._sounds.clear()
        ResourceManager._fonts.clear()
