from Animation.CharacterAnimation import Warrior, Archer, Monk
from Resource.Resource import ResourceManager
from constants import *


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
        
        self.is_target = (image_key == 'target')
        self.characters = []
        self.is_moving = False
        self.previous_x = x
        self.previous_y = y
        self.victory_animation_played = False
        
        self.victory_movement_active = False
        self.victory_target_x = None
        self.victory_speed = 0.08 
        self.victory_current_x = float(x)
        self.victory_current_y = float(y)

        self.is_offscreen = False
        
        if self.is_target:
            self._init_characters()

    def _init_characters(self):
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
         
        self.characters = [
            Archer(pos1_x, center_y, character_size),
            Monk(pos2_x, center_y, character_size),
            Warrior(pos3_x, center_y, character_size),
        ]
        
        self._characters_initialized = False

    def _ensure_characters_ready(self):
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
        if not self.characters:
            return
            
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

        positions = [
            (pos1_x, center_y),
            (pos2_x, center_y),
            (pos3_x, center_y)
        ]
        
        for i, character in enumerate(self.characters):
            if i < len(positions):
                character.x = positions[i][0]
                character.y = positions[i][1]

    def update_characters_position(self):
        if not self.is_target or not self.characters:
            return
        
        self._update_character_positions()

    def reset_movement_state(self):
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
        if not self.is_target or not self.characters:
            return
            
        position_changed = (self.x != self.previous_x or self.y != self.previous_y)
        current_moving = self.dragging or position_changed or self.victory_movement_active
        
        if current_moving != self.is_moving:
            self.is_moving = current_moving
            
            self._ensure_characters_ready()
            
            for character in self.characters:
                try:
                    if self.is_moving:
                        character.set_state("run")
                    else:
                        character.set_state("idle")
                except Exception as e:
                    print(f"Error setting character state: {e}")
        
        self.previous_x = self.x
        self.previous_y = self.y

    def start_victory_movement(self, board_width=6):
        if not self.is_target or self.victory_movement_active:
            return
            
        self.victory_movement_active = True
        self.victory_current_x = float(self.x)
        self.victory_current_y = float(self.y)
        
        if self.orient == 'h':  
            self.victory_target_x = board_width + self.len + 5  
        else:  
            self.victory_target_x = board_width + self.len + 5 
        
        self._ensure_characters_ready()
        for character in self.characters:
            try:
                character.set_state("run")
            except Exception as e:
                print(f"Error setting character to run: {e}")

    def update_victory_movement(self):
        if not self.victory_movement_active:
            return
            
        if self.orient == 'h':
            self.victory_current_x += self.victory_speed
            if self.victory_current_x >= self.victory_target_x:
                self.is_offscreen = True
                self.victory_movement_active = False
        else:
            self.victory_current_x += self.victory_speed
            if self.victory_current_x >= self.victory_target_x:
                self.is_offscreen = True
                self.victory_movement_active = False
        
        self._update_character_positions()

    def play_victory_animation(self):
        if not self.is_target or not self.characters or self.victory_animation_played:
            return
                    
        self.victory_animation_played = True
        
        self._ensure_characters_ready()
        
        for character in self.characters:
            try:
                character.perform_skill()
            except Exception as e:
                print(f"Error performing character skill: {e}")
        
        self.start_victory_movement()

    def is_off_screen(self):
        if not self.victory_movement_active:
            return False
        
        screen_width = BOARD_OFFSET_X + (6 * TILE)  
        
        if self.victory_current_x * TILE > screen_width:
            return True
        
        return False

    def update(self):
        if self.victory_movement_active:
            self.update_victory_movement()
        
        if self.is_target and self.characters:
            for character in self.characters:
                character.update()
            
            if (self.x != self.previous_x or self.y != self.previous_y or 
                self.victory_movement_active):
                self.update_characters_position()
                self.check_movement_state()
            
            self._ensure_characters_ready()

    def get_image(self):
        if self.image_key.startswith('v2'):
            return self.resource_manager.get_image(f'v2_{self.orient}')
        elif self.image_key.startswith('v3'):
            return self.resource_manager.get_image(f'v3_{self.orient}')
        elif self.image_key.startswith('target'):
            return None
    
    def draw_vehicle(self, surface, pos_override=None):
        if self.is_target:
            self.draw_target_vehicle(surface, pos_override)
        else:
            self.draw_normal_vehicle(surface, pos_override)

    def draw_normal_vehicle(self, surface, pos_override=None):
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
        if not self.characters:
            return
            
        self._ensure_characters_ready()
        
        if pos_override:
            temp_x, temp_y = pos_override
            base_x = BOARD_OFFSET_X + temp_x * TILE
            base_y = BOARD_OFFSET_Y + temp_y * TILE
            
            character_size = CHARACTER_SIZE_SCALE
            original_size = TILE // 2
            char_width = int(original_size * character_size)
            total_width = self.len * TILE
            spacing = total_width / 3

            center_y = base_y + (TILE - char_width) // 2 - SUPPORT_CHARACTER_ALLIANCE
            
            pos1_x = base_x + spacing - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE 
            pos2_x = base_x + spacing * 2 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
            pos3_x = base_x + spacing * 3 - char_width // 2 - SUPPORT_CHARACTER_ALLIANCE
            
            positions = [
                (pos1_x, center_y),
                (pos2_x, center_y),
                (pos3_x, center_y)
            ]
            
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
            for character in self.characters:
                try:
                    character.draw(surface)
                except Exception as e:
                    print(f"Error drawing character: {e}")

    def positions(self):
        if self.victory_movement_active:
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

        if self.victory_movement_active:
            return False
            
        board_x = (mouse_x - BOARD_OFFSET_X) // TILE
        board_y = (mouse_y - BOARD_OFFSET_Y) // TILE
        return (board_x, board_y) in self.positions()

    def draw(self, surf, pos_override=None):
        self.draw_vehicle(surf, pos_override)

    def copy(self):
        new_vehicle = Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.name, self.images)
        new_vehicle.is_target = self.is_target
        new_vehicle.victory_animation_played = self.victory_animation_played
        
        if self.is_target and self.characters:
            new_vehicle._init_characters()
        
        return new_vehicle
    
    def change_vehicle_data(self): 
        a = [self.name, self.x, self.y]
        b = [self.name, self.orient, self.len]
        return a, b