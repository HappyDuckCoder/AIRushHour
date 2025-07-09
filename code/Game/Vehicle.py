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
        
        # Victory movement properties
        self.victory_movement_active = False
        self.victory_target_x = None
        self.victory_speed = 0.08  # Tốc độ di chuyển (tiles per frame)
        self.victory_current_x = float(x)
        self.victory_current_y = float(y)

        self.is_offscreen = False
        
        # Khởi tạo characters nếu là target vehicle
        if self.is_target:
            self._init_characters()

    def _init_characters(self):
        # Tính toán vị trí trước khi tạo characters
        base_x = BOARD_OFFSET_X + self.x * TILE
        base_y = BOARD_OFFSET_Y + self.y * TILE
        
        # Kích thước character
        character_size = CHARACTER_SIZE_SCALE
        original_size = TILE // 2
        char_width = int(original_size * character_size)
        
        # Tính khoảng cách giữa các characters
        total_width = self.len * TILE
        spacing = total_width / 3
        
        # Vị trí y căn giữa tile
        center_y = base_y + (TILE - char_width) // 2 - SUPPORT_CHARACTER_ALLIANCE
        
        # Vị trí cho 3 characters
        pos1_x = base_x + spacing - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE 
        pos2_x = base_x + spacing * 2 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
        pos3_x = base_x + spacing * 3 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
         
        # Tạo characters với vị trí đã tính toán
        self.characters = [
            Archer(pos1_x, center_y, character_size),
            Monk(pos2_x, center_y, character_size),
            Warrior(pos3_x, center_y, character_size),
        ]
        
        self._characters_initialized = False

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
            
        # Sử dụng vị trí victory nếu đang trong victory movement
        if self.victory_movement_active:
            base_x = BOARD_OFFSET_X + self.victory_current_x * TILE
            base_y = BOARD_OFFSET_Y + self.victory_current_y * TILE
        else:
            base_x = BOARD_OFFSET_X + self.x * TILE
            base_y = BOARD_OFFSET_Y + self.y * TILE
        
        character_size = CHARACTER_SIZE_SCALE  
        original_size = TILE // 2
        char_width = int(original_size * character_size)
        
        total_width = self.len * TILE
        spacing = total_width / 3

        center_y = base_y + (TILE - char_width) // 2 - SUPPORT_CHARACTER_ALLIANCE
        
        pos1_x = base_x + spacing - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
        pos2_x = base_x + spacing * 2 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
        pos3_x = base_x + spacing * 3 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE

        # Vị trí cho 3 characters
        positions = [
            (pos1_x, center_y),
            (pos2_x, center_y),
            (pos3_x, center_y)
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

    def reset_movement_state(self):
        """Reset trạng thái di chuyển về idle - dùng khi solving complete"""
        if not self.is_target or not self.characters:
            return
            
        self.is_moving = False
        self.dragging = False
        self.victory_movement_active = False
        self._ensure_characters_ready()
        
        for character in self.characters:
            try:
                character.set_state("idle")
            except Exception as e:
                print(f"Error resetting character to idle: {e}")

    def check_movement_state(self):
        """Kiểm tra trạng thái di chuyển và cập nhật animation"""
        if not self.is_target or not self.characters:
            return
            
        # Kiểm tra xem có đang di chuyển không
        position_changed = (self.x != self.previous_x or self.y != self.previous_y)
        current_moving = self.dragging or position_changed or self.victory_movement_active
        
        # Chỉ cập nhật khi trạng thái thay đổi
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

    def start_victory_movement(self, board_width=6):
        """Bắt đầu di chuyển chiến thắng - target sẽ di chuyển ra khỏi map"""
        if not self.is_target or self.victory_movement_active:
            return
            
        self.victory_movement_active = True
        self.victory_current_x = float(self.x)
        self.victory_current_y = float(self.y)
        
        # Tính toán điểm đích dựa trên hướng
        if self.orient == 'h':  # Horizontal - di chuyển sang phải
            self.victory_target_x = board_width + self.len + 5  # Ra khỏi map
        else:  # Vertical - di chuyển xuống dưới
            self.victory_target_x = board_width + self.len + 5  # Ra khỏi map
        
        # Đảm bảo characters ở trạng thái run
        self._ensure_characters_ready()
        for character in self.characters:
            try:
                character.set_state("run")
            except Exception as e:
                print(f"Error setting character to run: {e}")

    def update_victory_movement(self):
        """Cập nhật di chuyển chiến thắng"""
        if not self.victory_movement_active:
            return
            
        # Di chuyển theo hướng horizontal (sang phải)
        if self.orient == 'h':
            self.victory_current_x += self.victory_speed
            if self.victory_current_x >= self.victory_target_x:
                self.is_offscreen = True
                self.victory_movement_active = False
        else:
            # Nếu là vertical, cũng di chuyển sang phải
            self.victory_current_x += self.victory_speed
            if self.victory_current_x >= self.victory_target_x:
                self.is_offscreen = True
                self.victory_movement_active = False
        
        # Cập nhật vị trí characters
        self._update_character_positions()

    def play_victory_animation(self):
        """Phát animation chiến thắng và bắt đầu di chuyển"""
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
        
        # Bắt đầu di chuyển victory sau một khoảng thời gian ngắn
        self.start_victory_movement()

    def is_off_screen(self):
        """Kiểm tra xem vehicle đã ra khỏi màn hình chưa"""
        if not self.victory_movement_active:
            return False
        
        # Kiểm tra xem có còn thấy character nào không
        screen_width = BOARD_OFFSET_X + (6 * TILE)  # Giả sử board rộng 6 tiles
        
        if self.victory_current_x * TILE > screen_width:
            return True
        
        return False

    def update(self):
        # Cập nhật victory movement trước
        if self.victory_movement_active:
            self.update_victory_movement()
        
        # Chỉ cập nhật khi có thay đổi vị trí
        if self.is_target and self.characters:
            for character in self.characters:
                character.update()
            
            if (self.x != self.previous_x or self.y != self.previous_y or 
                self.victory_movement_active):
                self.update_characters_position()
                self.check_movement_state()
            
            # Đảm bảo characters đã sẵn sàng trước khi update
            self._ensure_characters_ready()

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
            character_size = CHARACTER_SIZE_SCALE
            original_size = TILE // 2
            char_width = int(original_size * character_size)
            total_width = self.len * TILE
            spacing = total_width / 3

            # Tính vị trí y căn giữa tile
            center_y = base_y + (TILE - char_width) // 2 - SUPPORT_CHARACTER_ALLIANCE
            
            # Vị trí cho 3 characters
            pos1_x = base_x + spacing - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE 
            pos2_x = base_x + spacing * 2 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
            pos3_x = base_x + spacing * 3 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
            
            positions = [
                (pos1_x, center_y),
                (pos2_x, center_y),
                (pos3_x, center_y)
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
        if self.victory_movement_active:
            # Sử dụng vị trí victory khi đang di chuyển
            base_x = int(self.victory_current_x)
            base_y = int(self.victory_current_y)
        else:
            base_x = self.x
            base_y = self.y
            
        if self.orient == 'h':
            return [(base_x + i, base_y) for i in range(self.len)]
        else:
            return [(base_x, base_y + i) for i in range(self.len)]

    def contains_point(self, mouse_x, mouse_y):
        """Kiểm tra xem điểm chuột có nằm trong vehicle không"""
        # Không cho phép tương tác khi đang victory movement
        if self.victory_movement_active:
            return False
            
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