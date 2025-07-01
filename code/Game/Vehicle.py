from constants import *
from Graphic.Graphic import *

# ===============================
# Vehicle Class
# ===============================
class Vehicle:
    def __init__(self, image_key, orientation, length, x, y, images=None, name='A'):
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
        gfx.draw_vehicle(surf, self, pos_override)

    def copy(self):
        return Vehicle(self.image_key, self.orient, self.len, self.x, self.y, self.images, self.name)
    
    def change_vehicle_data(self): 
        a = [self.name, self.x, self.y]
        b = [self.name, self.orient, self.len]
        return a, b