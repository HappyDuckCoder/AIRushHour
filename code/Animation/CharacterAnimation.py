import pygame
from constants import *
from Resource.Resource import ResourceManager
from Animation.Animation import AnimationStrategy

class Character:
    def __init__(self, x, y, character_type, size=1.0):
        self.x = x
        self.y = y
        self.character_type = character_type
        self.size = size
        self.current_state = "idle"
        self.animations = {}
        self.current_animation = None
        self.is_moving = False
        self.is_performing_skill = False
        self.direction = 1
        self.speed = 10
        self.last_frame_update_time = pygame.time.get_ticks()
        self.is_loaded = False
        self.scaled_frames_cache = {}
        if not self.is_loaded:
            self._load_animations()
            self.is_loaded = True
        else:
            self.set_state("idle")
    
    def _load_animations(self):
        pass
    
    def set_state(self, state):
        if state in self.animations and self.current_state != state:
            self.current_state = state
            self.current_animation = self.animations[state]
            if self.current_animation:
                self.current_animation.index = 0
                self.current_animation.done_once = False
                self.current_animation.current_frames = self.current_animation.frames
                self.scaled_frames_cache.clear()
    
    def update(self):
        if self.is_performing_skill and self.current_animation and self.current_animation.done_once:
            self.is_performing_skill = False
            self.set_state("idle")

        if self.current_animation:
            if hasattr(self.current_animation, 'frames') and self.current_animation.frames:
                frames = self.current_animation.frames
                if self.direction == -1:
                    if not hasattr(self.current_animation, 'flipped_frames'):
                        self.current_animation.flipped_frames = [
                            pygame.transform.flip(frame, True, False) for frame in frames
                        ]
                    self.current_animation.current_frames = self.current_animation.flipped_frames
                else:
                    self.current_animation.current_frames = frames

                now = pygame.time.get_ticks()
                delay = 1000 // self.current_animation.framerate

                if now - self.last_frame_update_time >= delay:
                    self.current_animation.index += 1
                    self.last_frame_update_time = now

                    if self.current_animation.index >= len(self.current_animation.current_frames):
                        self.current_animation.index = 0
                        self.current_animation.done_once = True

    def draw(self, surface):
        if not self.current_animation:
            if "idle" in self.animations and self.animations["idle"]:
                self.current_animation = self.animations["idle"]
                self.current_animation.index = 0
                self.current_animation.done_once = False
            else:
                print("ERROR: No valid animations available!")
                return
        self._draw_scaled(surface)

    def _draw_scaled(self, surface):
        if not self.current_animation or not self.current_animation.current_frames:
            return

        current_frames = self.current_animation.current_frames
        if self.current_animation.index >= len(current_frames):
            return

        current_frame = current_frames[self.current_animation.index]
        if not current_frame:
            return

        cache_key = (
            id(current_frame),
            self.size,
            self.direction
        )

        if cache_key not in self.scaled_frames_cache:
            original_size = current_frame.get_size()
            new_size = (int(original_size[0] * self.size), int(original_size[1] * self.size))
            self.scaled_frames_cache[cache_key] = pygame.transform.scale(current_frame, new_size)

        scaled_frame = self.scaled_frames_cache[cache_key]
        surface.blit(scaled_frame, (self.x, self.y))

    def perform_skill(self):
        pass
    
    def get_rect(self):
        if self.current_animation and self.current_animation.current_frames:
            current_frame = self.current_animation.current_frames[self.current_animation.index]
            if current_frame:
                original_size = current_frame.get_size()
                scaled_width = int(original_size[0] * self.size)
                scaled_height = int(original_size[1] * self.size)
                return pygame.Rect(self.x, self.y, scaled_width, scaled_height)
        base_size = 32
        scaled_size = int(base_size * self.size)
        return pygame.Rect(self.x, self.y, scaled_size, scaled_size)
    
    def cleanup(self):
        self.scaled_frames_cache.clear()


class Warrior(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Warrior", size)
    
    def _load_animations(self):
        idle_frames = ResourceManager.get_image("warrior_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        run_frames = ResourceManager.get_image("warrior_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        guard_frames = ResourceManager.get_image("warrior_guard")
        if guard_frames:
            self.animations["guard"] = AnimationStrategy(guard_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
    
    def perform_skill(self):
        if not self.is_performing_skill:
            self.set_state("guard")


class Archer(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Archer", size)
    
    def _load_animations(self):
        idle_frames = ResourceManager.get_image("archer_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        run_frames = ResourceManager.get_image("archer_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        shoot_frames = ResourceManager.get_image("archer_shoot")
        if shoot_frames:
            self.animations["shoot"] = AnimationStrategy(shoot_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
    
    def perform_skill(self):
        if not self.is_performing_skill:
            self.set_state("shoot")


class Monk(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Monk", size)
    
    def _load_animations(self):
        idle_frames = ResourceManager.get_image("monk_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        run_frames = ResourceManager.get_image("monk_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
        
        shoot_frames = ResourceManager.get_image("monk_heal")
        if shoot_frames:
            self.animations["heal"] = AnimationStrategy(shoot_frames, frame_rate=ANIMATION_DEFAULT_SPEED)
    
    def perform_skill(self):
        if not self.is_performing_skill:
            self.set_state("heal")
