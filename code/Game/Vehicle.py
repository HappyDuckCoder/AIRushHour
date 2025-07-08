from Animation.CharacterAnimation import Warrior, Archer
from Resource.Resource import ResourceManager
from constants import *


# ===============================
# Vehicle Class - Optimized
# ===============================
class Vehicle:
    def __init__(self, image_key, orientation, length, x, y, name, images=None):
        self.image_key = image_key
        self.orient = orientation
        self.len = length
        self.x = x
        self.y = y
        self.images = images
        self.name = name
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.resource_manager = ResourceManager()
        
        # Character integration cho target vehicle
        self.is_target = (image_key == 'target')
        self.characters = []
        self.is_moving = False
        self.previous_x = x
        self.previous_y = y
        self.victory_animation_played = False
        
        # Khởi tạo characters nếu là target vehicle
        if self.is_target:
            self._init_characters()

    def _init_characters(self):
        """Khởi tạo characters cho target vehicle - OPTIMIZED"""
        # Tính toán vị trí trước khi tạo characters
        base_x = BOARD_OFFSET_X + self.x * TILE
        base_y = BOARD_OFFSET_Y + self.y * TILE
        
        # Kích thước character
        character_size = 0.6
        original_size = TILE // 2
        char_width = int(original_size * character_size)
        
        # Tính khoảng cách giữa các characters
        total_width = self.len * TILE
        spacing = total_width / 3
        
        # Vị trí y căn giữa tile
        center_y = base_y + (TILE - char_width) // 2 - 50
        
        # Vị trí cho 2 characters
        pos1_x = base_x + spacing - char_width // 2 - 50 
        pos2_x = base_x + spacing * 2 - char_width // 2 - 50
         
        # Tạo characters với vị trí đã tính toán
        self.characters = [
            Warrior(pos1_x, center_y, character_size),
            Archer(pos2_x, center_y, character_size)
        ]
        
        self._characters_initialized = False

        # *** KHỞI TẠO NGAY LẬP TỨC ĐỂ HIỂN THỊ KHI VỪA CHẠY GAME ***
        self._characters_initialized = False
        self._ensure_characters_ready()  # Gọi ngay để khởi tạo animations

    def _ensure_characters_ready(self):
        """Đảm bảo characters được khởi tạo đúng cách - LAZY LOADING"""
        if not self._characters_initialized and self.characters:
            for character in self.characters:
                if hasattr(character, 'animations') and character.animations:
                    character.set_state("idle")
                elif hasattr(character, '_load_animations'):
                    try:
                        character._load_animations()
                        character.set_state("idle")
                    except Exception as e:
                        print(f"Failed to load character animations: {e}")
            self._characters_initialized = True

    def _update_character_positions(self):
        """Cập nhật vị trí của các characters"""
        if not self.characters:
            return
            
        # Tính toán vị trí cho characters xếp thành hàng ngang
        base_x = BOARD_OFFSET_X + self.x * TILE
        base_y = BOARD_OFFSET_Y + self.y * TILE
        
        character_size = 0.6  # Sử dụng cùng size với init
        original_size = TILE // 2
        char_width = int(original_size * character_size)
        
        total_width = self.len * TILE
        spacing = total_width / 3

        center_y = base_y + (TILE - char_width) // 2 - 50
        
        pos1_x = base_x + spacing - char_width // 2 - 50 
        pos2_x = base_x + spacing * 2 - char_width // 2 - 50

        # Vị trí cho 2 characters
        positions = [
            (pos1_x, center_y),
            (pos2_x, center_y)
        ]
        
        # Cập nhật vị trí cho từng character
        for i, character in enumerate(self.characters):
            if i < len(positions):
                character.x = positions[i][0]
                character.y = positions[i][1]

    def update_characters_position(self):
        """Cập nhật vị trí của các characters khi vehicle di chuyển"""
        if not self.is_target or not self.characters:
            return
        
        self._update_character_positions()

    def check_movement_state(self):
        """Kiểm tra trạng thái di chuyển và cập nhật animation - OPTIMIZED"""
        if not self.is_target or not self.characters:
            return
            
        # Chỉ kiểm tra khi có thay đổi vị trí
        current_moving = (self.x != self.previous_x or self.y != self.previous_y)
        
        if current_moving != self.is_moving:
            self.is_moving = current_moving
            
            # Đảm bảo characters đã sẵn sàng
            self._ensure_characters_ready()
            
            # Cập nhật animation cho tất cả characters
            for character in self.characters:
                try:
                    if self.is_moving:
                        character.set_state("run")
                    else:
                        character.set_state("idle")
                except Exception as e:
                    print(f"Error setting character state: {e}")
        
        # Cập nhật vị trí trước đó
        self.previous_x = self.x
        self.previous_y = self.y

    def play_victory_animation(self):
        """Phát animation chiến thắng"""
        if not self.is_target or not self.characters or self.victory_animation_played:
            return
            
        self.victory_animation_played = True
        
        # Đảm bảo characters đã sẵn sàng
        self._ensure_characters_ready()
        
        # Tất cả characters thực hiện skill đặc biệt
        for character in self.characters:
            try:
                character.perform_skill()
            except Exception as e:
                print(f"Error performing character skill: {e}")

    def update(self):
        if self.is_target and self.characters:
            # Chỉ cập nhật khi có thay đổi vị trí
            if self.x != self.previous_x or self.y != self.previous_y:
                self.update_characters_position()
                self.check_movement_state()
            
            # Đảm bảo characters đã sẵn sàng trước khi update
            self._ensure_characters_ready()
            
            # Cập nhật từng character
            for character in self.characters:
                try:
                    character.update()
                except Exception as e:
                    print(f"Error updating character: {e}")

    def get_image(self):
        """Lấy image cho vehicle thông thường (không phải target)"""
        if self.image_key.startswith('v2'):
            return self.resource_manager.get_image(f'v2_{self.orient}')
        elif self.image_key.startswith('v3'):
            return self.resource_manager.get_image(f'v3_{self.orient}')
        elif self.image_key.startswith('target'):
            # Target vehicle sẽ được vẽ bằng characters, không cần image
            return None
    
    def draw_vehicle(self, surface, pos_override=None):
        """Vẽ vehicle"""
        if self.is_target:
            # Vẽ target vehicle bằng characters
            self.draw_target_vehicle(surface, pos_override)
        else:
            # Vẽ vehicle thông thường
            self.draw_normal_vehicle(surface, pos_override)

    def draw_normal_vehicle(self, surface, pos_override=None):
        """Vẽ vehicle thông thường"""
        if pos_override:
            draw_x, draw_y = pos_override
        else:
            draw_x, draw_y = self.x, self.y
            
        image = self.get_image()
        if image:
            screen_x = BOARD_OFFSET_X + draw_x * TILE
            screen_y = BOARD_OFFSET_Y + draw_y * TILE
            surface.blit(image, (screen_x, screen_y))

    def draw_target_vehicle(self, surface, pos_override=None):
        """Vẽ target vehicle bằng characters xếp hàng ngang"""
        if not self.characters:
            return
            
        # Đảm bảo characters đã sẵn sàng
        self._ensure_characters_ready()
            
        # Nếu có pos_override, tạm thời cập nhật vị trí characters
        if pos_override:
            temp_x, temp_y = pos_override
            base_x = BOARD_OFFSET_X + temp_x * TILE
            base_y = BOARD_OFFSET_Y + temp_y * TILE
            
            # Tính kích thước và vị trí tạm thời
            character_size = 0.6
            original_size = TILE // 2
            char_width = int(original_size * character_size)
            total_width = self.len * TILE
            spacing = total_width / 3
            center_y = base_y + (TILE - char_width) // 2 - 10
            
            positions = [
                (base_x + spacing - char_width // 2, center_y),
                (base_x + spacing * 2 - char_width // 2, center_y)
            ]
            
            # Vẽ characters tại vị trí tạm thời
            for i, character in enumerate(self.characters):
                if i < len(positions):
                    temp_character_x = character.x
                    temp_character_y = character.y
                    character.x = positions[i][0]
                    character.y = positions[i][1]
                    try:
                        character.draw(surface)
                    except Exception as e:
                        print(f"Error drawing character: {e}")
                    character.x = temp_character_x
                    character.y = temp_character_y
        else:
            # Vẽ characters tại vị trí hiện tại
            for character in self.characters:
                try:
                    character.draw(surface)
                except Exception as e:
                    print(f"Error drawing character: {e}")

    def positions(self):
        """Lấy các vị trí mà vehicle chiếm trên grid"""
        if self.orient == 'h':
            return [(self.x + i, self.y) for i in range(self.len)]
        else:
            return [(self.x, self.y + i) for i in range(self.len)]

    def contains_point(self, mouse_x, mouse_y):
        """Kiểm tra xem điểm chuột có nằm trong vehicle không"""
        board_x = (mouse_x - BOARD_OFFSET_X) // TILE
        board_y = (mouse_y - BOARD_OFFSET_Y) // TILE
        return (board_x, board_y) in self.positions()

    def draw(self, surf, pos_override=None):
        """Vẽ vehicle"""
        self.draw_vehicle(surf, pos_override)

    def copy(self):
        """Tạo bản sao của vehicle"""
        new_vehicle = Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.name, self.images)
        new_vehicle.is_target = self.is_target
        new_vehicle.victory_animation_played = self.victory_animation_played
        
        # Sao chép characters nếu có
        if self.is_target and self.characters:
            new_vehicle._init_characters()
        
        return new_vehicle
    
    def change_vehicle_data(self): 
        """Lấy dữ liệu vehicle"""
        a = [self.name, self.x, self.y]
        b = [self.name, self.orient, self.len]
        return a, b