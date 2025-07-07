from Animation.CharacterAnimation import Warrior, Archer, Monk
from Resource.Resource import ResourceManager
from constants import *


# ===============================
# Vehicle Class 
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
        """Khởi tạo 4 chiến binh cho target vehicle - xếp thành hàng ngang"""
        # Tính toán vị trí cho 4 chiến binh xếp thành hàng ngang
        base_x = BOARD_OFFSET_X + self.x * TILE
        base_y = BOARD_OFFSET_Y + self.y * TILE
        
        # Chọn size hợp lý với TILE = 70
        character_size = 0.7  # Size phù hợp với TILE = 70
        original_size = TILE // 3  # ~23px
        
        # Tính kích thước character sau khi scale
        char_width = int(original_size)
        
        # Tính khoảng cách giữa các characters để fit trong 2 tiles (140px với TILE=70)
        total_width = self.len * TILE  # 2 * 70 = 140px
        char_spacing = total_width / 2 
        
        # Vị trí y căn giữa tile
        center_y = base_y + (TILE - original_size) // 2
        
        # Tạo 4 vị trí xếp hàng ngang - căn giữa mỗi khoảng
        positions = [
            (base_x + int(char_spacing * 0 + char_spacing/2) - char_width // 2, center_y),  # Warrior
            (base_x + int(char_spacing * 1 + char_spacing/2) - char_width // 2, center_y),  # Archer  
            (base_x + int(char_spacing * 2 + char_spacing/2) - char_width // 2, center_y)   # Monk
        ]
        
        # Tạo 4 chiến binh với size hợp lý
        self.characters = [
            Archer(positions[1][0], positions[1][1], character_size),
            Monk(positions[2][0], positions[2][1], character_size),
            Warrior(positions[0][0], positions[0][1], character_size),
        ]

    def update_characters_position(self):
        """Cập nhật vị trí của các characters khi vehicle di chuyển"""
        if not self.is_target or not self.characters:
            return
            
        base_x = BOARD_OFFSET_X + self.x * TILE
        base_y = BOARD_OFFSET_Y + self.y * TILE // 2
        
        # Sử dụng cùng logic với _init_characters
        character_size = 0.7
        original_size = TILE // 3
        char_width = int(original_size)
        
        # Tính khoảng cách giữa các characters
        total_width = self.len * TILE
        char_spacing = total_width / 8
        
        # Vị trí y căn giữa tile
        center_y = base_y + (TILE - original_size) // 2
        
        # Cập nhật vị trí cho từng character
        positions = [
            (base_x + int(char_spacing * 0 + char_spacing/2) - char_width // 2, center_y),
            (base_x + int(char_spacing * 1 + char_spacing/2) - char_width // 2, center_y),
            (base_x + int(char_spacing * 2 + char_spacing/2) - char_width // 2, center_y),
            (base_x + int(char_spacing * 3 + char_spacing/2) - char_width // 2, center_y)
        ]
        
        for i, character in enumerate(self.characters):
            character.x = positions[i][0]
            character.y = positions[i][1]

    def check_movement_state(self):
        """Kiểm tra trạng thái di chuyển và cập nhật animation"""
        if not self.is_target or not self.characters:
            return
            
        # Kiểm tra xem vehicle có đang di chuyển không
        current_moving = (self.x != self.previous_x or self.y != self.previous_y)
        
        if current_moving != self.is_moving:
            self.is_moving = current_moving
            
            # Cập nhật animation cho tất cả characters
            for character in self.characters:
                if self.is_moving:
                    character.set_state("run")
                else:
                    character.set_state("idle")
        
        # Cập nhật vị trí trước đó
        self.previous_x = self.x
        self.previous_y = self.y

    def play_victory_animation(self):
        """Phát animation chiến thắng"""
        if not self.is_target or not self.characters or self.victory_animation_played:
            return
            
        self.victory_animation_played = True
        
        # Tất cả characters thực hiện skill đặc biệt
        for character in self.characters:
            character.perform_skill()

    def update(self):
        """Cập nhật vehicle và characters"""
        if self.is_target and self.characters:
            self.update_characters_position()
            self.check_movement_state()
            
            # Cập nhật từng character
            for character in self.characters:
                character.update()

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
            
        # Nếu có pos_override, tạm thời cập nhật vị trí characters
        if pos_override:
            temp_x, temp_y = pos_override
            base_x = BOARD_OFFSET_X + temp_x * TILE
            base_y = BOARD_OFFSET_Y + temp_y * TILE
            
            # Tính kích thước và vị trí tạm thời
            character_size = 0.7
            original_size = TILE // 3
            char_width = int(original_size)
            total_width = self.len * TILE
            char_spacing = total_width / 4
            center_y = base_y + (TILE - original_size) // 2
            
            positions = [
                (base_x + int(char_spacing * 0 + char_spacing/2) - char_width // 2, center_y),
                (base_x + int(char_spacing * 1 + char_spacing/2) - char_width // 2, center_y),
                (base_x + int(char_spacing * 2 + char_spacing/2) - char_width // 2, center_y),
                (base_x + int(char_spacing * 3 + char_spacing/2) - char_width // 2, center_y)
            ]
            
            # Vẽ characters tại vị trí tạm thời
            for i, character in enumerate(self.characters):
                temp_character_x = character.x
                temp_character_y = character.y
                character.x = positions[i][0]
                character.y = positions[i][1]
                character.draw(surface)
                character.x = temp_character_x
                character.y = temp_character_y
        else:
            # Vẽ characters tại vị trí hiện tại
            for character in self.characters:
                character.draw(surface)

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