import pygame
from constants import *

class ResourceManager:
    _images = {}
    _sounds = {}
    _fonts = {}

    @staticmethod
    def init():
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    @staticmethod
    def load_image(name, path, size=None, rotate=None):
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
    def load_frames(name, path, frame_width, frame_height, num_frames):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = [
                sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                for i in range(num_frames)
            ]
            ResourceManager._images[name] = frames
        except pygame.error as e:
            print(f"[ERROR] Cannot load frames '{name}' from '{path}': {e}")

    @staticmethod
    def get_image(name):
        return ResourceManager._images.get(name)

    @staticmethod
    def get_image(name):
        return ResourceManager._images.get(name)

    @staticmethod
    def upload_all():

        ResourceManager.load_background()

        map_size = MAP_N * TILE
        ResourceManager.load_image(
            "map",
            "assets/map.png",
            size=(map_size, map_size + TILE)
        )

        ResourceManager.load_image(
            "target",
            "assets/target.png",
            size=(TILE * 2, TILE)
        )

        ResourceManager.load_image(
            "mouse",
            "assets/Mouse.png",
            size=(MOUSE_SIZE, MOUSE_SIZE)
        )

        ResourceManager.load_image(
            "icon",
            "assets/Units/Blue Units/Archer/Archer_Idle.png",
            size=(ICON_SIZE, ICON_SIZE)
        )

        ResourceManager.load_image(
            "exit",
            "assets/Bridge.png",
            size=(TILE * 2, TILE)
        )
        
        ResourceManager.load_all_vehicle_image()

        ResourceManager.load_all_character_animations()

        ResourceManager.load_statistics_image()

    @staticmethod
    def unload_all():
        ResourceManager._images.clear()
        ResourceManager._sounds.clear()
        ResourceManager._fonts.clear()

    @staticmethod
    def load_background():
        ResourceManager.load_image(
            "background1",
            "assets/bgRes/bg2/background.png",
            size=(SCREEN_W, SCREEN_H)
        )
        ResourceManager.load_image(
            "background12",
            "assets/bgRes/bg2/background2.png",
            size=(SCREEN_W, SCREEN_H)
        )
        ResourceManager.load_image(
            "background13",
            "assets/bgRes/bg2/background3.png",
            size=(SCREEN_W, SCREEN_H)
        )
        ResourceManager.load_image(
            "background14",
            "assets/bgRes/bg2/background4.png",
            size=(SCREEN_W, SCREEN_H)
        )

        ResourceManager.load_image(
            "background21",
            "assets/bgRes/bg1/background1.png",
            size=(SCREEN_W, SCREEN_H)
        )
        ResourceManager.load_image(
            "background22",
            "assets/bgRes/bg1/background2.png",
            size=(SCREEN_W, SCREEN_H)
        )
        ResourceManager.load_image(
            "background23",
            "assets/bgRes/bg1/background3.png",
            size=(SCREEN_W, SCREEN_H)
        )

    @staticmethod
    def load_all_vehicle_image():

        ResourceManager.load_image(
            "v2_h",
            "assets/vh/vh2h.png",
            size=(TILE * 2, TILE)
        )
        ResourceManager.load_image(
            "v2_v",
            "assets/vh/vh2v.png",
            size=(TILE, TILE * 2),
        )

        ResourceManager.load_image(
            "v3_h",
            "assets/vh/vh3h.png",
            size=(TILE * 3, TILE)
        )
        ResourceManager.load_image(
            "v3_v",
            "assets/vh/vh3v.png",
            size=(TILE, TILE * 3 + 25),
        )

    @staticmethod
    def load_all_character_animations():
        
        ResourceManager.load_frames(
            "archer_idle", 
            "assets/Units/Blue Units/Archer/Archer_Idle.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 6
        )
        ResourceManager.load_frames(
            "archer_run", 
            "assets/Units/Blue Units/Archer/Archer_Run.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 4
        )
        ResourceManager.load_frames(
            "archer_shoot", 
            "assets/Units/Blue Units/Archer/Archer_Shoot.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 8
        )
        
        ResourceManager.load_frames(
            "warrior_idle", 
            "assets/Units/Red Units/Warrior/Warrior_Idle.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 8
        )
        ResourceManager.load_frames(
            "warrior_run", 
            "assets/Units/Red Units/Warrior/Warrior_Run.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 6
        )
        ResourceManager.load_frames(
            "warrior_guard", 
            "assets/Units/Red Units/Warrior/Warrior_Guard.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 6
        )
    
        ResourceManager.load_frames(
            "monk_idle", 
            "assets/Units/Black Units/Monk/Monk_Idle.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 6
        )
        ResourceManager.load_frames(
            "monk_run", 
            "assets/Units/Black Units/Monk/Monk_Run.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 4
        )
        ResourceManager.load_frames(
            "monk_heal", 
            "assets/Units/Black Units/Monk/Monk_Heal.png", 
            FRAME_WIDTH, FRAME_HEIGHT, 11
        )

    @staticmethod
    def load_statistics_image():
        for i in range(1, 11):
            ResourceManager.load_image(
                f"map_{i}_statistic",
                f"code/Comparison/Results/0{i}_comparison_chart.png",
                size=(SCREEN_W // 2 + TILE, SCREEN_H // 2 + TILE)
            )