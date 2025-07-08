import pygame
from constants import *
from Resource.Resource import ResourceManager
from Animation.Animation import AnimationStrategy

class Character:
    def __init__(self, x, y, character_type, size=1.0):
        self.x = x
        self.y = y
        self.character_type = character_type
        self.size = size  # Scale factor for character
        self.current_state = "idle"
        self.animations = {}
        self.current_animation = None
        self.is_moving = False
        self.is_performing_skill = False
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 10

        self.is_loaded = False
        
        # Cache cho scaled frames để tối ưu hiệu suất
        self.scaled_frames_cache = {}
        
        # Load animations cho nhân vật
        if not self.is_loaded:
            self._load_animations()
            self.is_loaded = True
        else: 
            self.set_state("idle")
    
    def _load_animations(self):
        """Load animations cho nhân vật - sẽ được override trong class con"""
        pass
    
    def set_state(self, state):
        """Thay đổi trạng thái animation"""
        if state in self.animations and self.current_state != state:
            self.current_state = state
            self.current_animation = self.animations[state]
            if self.current_animation:
                self.current_animation.index = 0
                self.current_animation.done_once = False
                self.current_animation.current_frames = self.current_animation.frames
                
                # Clear cache khi đổi animation
                self.scaled_frames_cache.clear()
    
    def update(self):
        """Cập nhật nhân vật"""
        # Tự động chuyển về idle sau khi hoàn thành skill
        if self.is_performing_skill and self.current_animation and self.current_animation.done_once:
            self.is_performing_skill = False
            self.set_state("idle")
        
        # Cập nhật animation nếu có
        if self.current_animation:
            # Lật sprite theo hướng nếu cần
            if hasattr(self.current_animation, 'frames') and self.current_animation.frames:
                frames = self.current_animation.frames
                if self.direction == -1:
                    # Tạo frames đã lật nếu chưa có
                    if not hasattr(self.current_animation, 'flipped_frames'):
                        self.current_animation.flipped_frames = [
                            pygame.transform.flip(frame, True, False) for frame in frames
                        ]
                    self.current_animation.current_frames = self.current_animation.flipped_frames
                else:
                    self.current_animation.current_frames = frames
    
    def draw(self, surface):
        """Vẽ nhân vật với scale"""
        if not self.current_animation:
            # Thử khôi phục animation
            if "idle" in self.animations and self.animations["idle"]:
                self.current_animation = self.animations["idle"]
                self.current_animation.index = 0
                self.current_animation.done_once = False
            else:
                print("ERROR: No valid animations available!")
                return
        
        self._draw_scaled(surface)

    
    def _draw_scaled(self, surface):
        """Vẽ nhân vật với scale - version được tối ưu"""
        if not self.current_animation or not self.current_animation.current_frames:
            return
            
        # Lấy frame hiện tại
        current_frames = self.current_animation.current_frames
        if self.current_animation.index >= len(current_frames):
            return
            
        current_frame = current_frames[self.current_animation.index]
        if not current_frame:
            return
        
        # Tạo cache key để tránh scale lại frame đã được scale
        cache_key = (
            id(current_frame),  # ID của frame
            self.size,          # Scale factor
            self.direction      # Direction để phân biệt flipped frames
        )
        
        # Kiểm tra cache
        if cache_key not in self.scaled_frames_cache:
            original_size = current_frame.get_size()
            new_size = (int(original_size[0] * self.size), int(original_size[1] * self.size))
            self.scaled_frames_cache[cache_key] = pygame.transform.scale(current_frame, new_size)
        
        # Vẽ scaled frame từ cache
        scaled_frame = self.scaled_frames_cache[cache_key]
        surface.blit(scaled_frame, (self.x, self.y))
        
        # Cập nhật animation index (sử dụng current_frames thay vì frames)
        self.current_animation.index += 1
        if self.current_animation.index >= len(current_frames):
            self.current_animation.done_once = True
            self.current_animation.index = 0
    
    def perform_skill(self):
        """Thực hiện kỹ năng đặc biệt - sẽ được override"""
        pass
    
    def get_rect(self):
        """Lấy rectangle cho collision detection với scale"""
        if self.current_animation and self.current_animation.current_frames:
            current_frame = self.current_animation.current_frames[self.current_animation.index]
            if current_frame:
                # Sử dụng kích thước thật của frame đã scale
                original_size = current_frame.get_size()
                scaled_width = int(original_size[0] * self.size)
                scaled_height = int(original_size[1] * self.size)
                return pygame.Rect(self.x, self.y, scaled_width, scaled_height)
        
        # Fallback nếu không có frame
        base_size = 32
        scaled_size = int(base_size * self.size)
        return pygame.Rect(self.x, self.y, scaled_size, scaled_size)
    
    def cleanup(self):
        """Cleanup cache khi không cần thiết"""
        self.scaled_frames_cache.clear()


class Warrior(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Warrior", size)
    
    def _load_animations(self):
        """Load animations cho Warrior"""
        # Idle animation
        idle_frames = ResourceManager.get_image("warrior_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames)
        
        # Run animation
        run_frames = ResourceManager.get_image("warrior_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames)
        
        # Guard animation (skill đặc biệt)
        guard_frames = ResourceManager.get_image("warrior_guard")
        if guard_frames:
            self.animations["guard"] = AnimationStrategy(guard_frames)
    
    def perform_skill(self):
        """Kỹ năng Shield"""
        if not self.is_performing_skill:
            self.set_state("guard")
            self.is_performing_skill = True

class Archer(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Archer", size)
    
    def _load_animations(self):
        """Load animations cho Archer"""
        # Idle animation
        idle_frames = ResourceManager.get_image("archer_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames)
        
        # Run animation
        run_frames = ResourceManager.get_image("archer_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames)
        
        # Shoot animation (skill đặc biệt)
        shoot_frames = ResourceManager.get_image("archer_shoot")
        if shoot_frames:
            self.animations["shoot"] = AnimationStrategy(shoot_frames)
    
    def perform_skill(self):
        """Kỹ năng Shoot - bắn mũi tên"""
        if not self.is_performing_skill:
            self.set_state("shoot")
            self.is_performing_skill = True
