from constants import *

# ===============================
# Vehicle Class
# ===============================
class Vehicle:
    def __init__(self, image_key, orientation, length, x, y, is_target=False, images=None):
        self.image_key = image_key
        self.orient = orientation
        self.len = length
        self.x = x
        self.y = y
        self.is_target = is_target
        self.images = images
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def get_image(self):
        if self.images:
            if self.image_key.startswith('v2'):
                return self.images.get(f'v2_{self.orient}')
            elif self.image_key.startswith('v3'):
                return self.images.get(f'v3_{self.orient}')
            return self.images.get(self.image_key)
        return None

    def positions(self):
        if self.orient == 'h':
            return [(self.x + i, self.y) for i in range(self.len)]
        else:
            return [(self.x, self.y + i) for i in range(self.len)]

    def contains_point(self, mouse_x, mouse_y):
        board_x = (mouse_x - BOARD_OFFSET_X) // TILE
        board_y = (mouse_y - BOARD_OFFSET_Y) // TILE
        return (board_x, board_y) in self.positions()

    def draw(self, surf, pos_override=None):
        if pos_override:
            draw_x, draw_y = pos_override
        else:
            draw_x, draw_y = self.x, self.y
            
        image = self.get_image()
        if image:
            screen_x = BOARD_OFFSET_X + draw_x * TILE
            screen_y = BOARD_OFFSET_Y + draw_y * TILE
            surf.blit(image, (screen_x, screen_y))

    def copy(self):
        return Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.is_target, self.images)