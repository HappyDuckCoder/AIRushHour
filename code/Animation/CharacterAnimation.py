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
        self.speed = 0.1
        
        # Load animations cho nhân vật
        self._load_animations()
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
        if self.current_animation:
            # Nếu có size khác 1.0, scale animation frames
            if self.size != 1.0:
                self._draw_scaled(surface)
            else:
                self.current_animation.update(surface, self.x, self.y)
    
    def _draw_scaled(self, surface):
        """Vẽ nhân vật với scale"""
        if not self.current_animation:
            return
            
        # Lấy frame hiện tại
        current_frame = self.current_animation.current_frames[self.current_animation.index]
        if current_frame:
            # Scale frame
            original_size = current_frame.get_size()
            new_size = (int(original_size[0] * self.size), int(original_size[1] * self.size))
            scaled_frame = pygame.transform.scale(current_frame, new_size)
            
            # Vẽ scaled frame
            surface.blit(scaled_frame, (self.x, self.y))
            
            # Cập nhật animation index
            self.current_animation.index += 1
            if self.current_animation.index >= len(self.current_animation.frames):
                self.current_animation.done_once = True
                self.current_animation.index = 0
    
    def move(self, dx, dy):
        """Di chuyển nhân vật"""
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Cập nhật hướng
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1
        
        # Cập nhật trạng thái animation
        if dx != 0 or dy != 0:
            if not self.is_moving and not self.is_performing_skill:
                self.set_state("run")
                self.is_moving = True
        else:
            if self.is_moving and not self.is_performing_skill:
                self.set_state("idle")
                self.is_moving = False
    
    def perform_skill(self):
        """Thực hiện kỹ năng đặc biệt - sẽ được override"""
        pass
    
    def get_rect(self):
        """Lấy rectangle cho collision detection với scale"""
        base_size = 32
        scaled_size = int(base_size * self.size)
        return pygame.Rect(self.x, self.y, scaled_size, scaled_size)


class Warrior(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Warrior", size)
        self.is_guarding = False
        self.defense_boost = 0
    
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
            self.is_guarding = True
            self.defense_boost = 50  # Increase defense by 50%
    
    def update(self):
        super().update()
        # Tắt guard khi animation kết thúc
        if self.is_guarding and self.current_animation and self.current_animation.done_once:
            self.is_guarding = False
            self.defense_boost = 0

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

class Monk(Character):
    def __init__(self, x, y, size=1.0):
        super().__init__(x, y, "Monk", size)
    
    def _load_animations(self):
        """Load animations cho Monk"""
        # Idle animation
        idle_frames = ResourceManager.get_image("monk_idle")
        if idle_frames:
            self.animations["idle"] = AnimationStrategy(idle_frames)
        
        # Run animation
        run_frames = ResourceManager.get_image("monk_run")
        if run_frames:
            self.animations["run"] = AnimationStrategy(run_frames)
        
        # Heal animation (skill đặc biệt)
        heal_frames = ResourceManager.get_image("monk_heal")
        if heal_frames:
            self.animations["heal"] = AnimationStrategy(heal_frames)
    
    def perform_skill(self):
        """Kỹ năng Heal"""
        if not self.is_performing_skill:
            self.set_state("heal")
            self.is_performing_skill = True