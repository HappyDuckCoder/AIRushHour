from constants import *
from Resource.Resource import ResourceManager

# ===============================
# Screen Management
# ===============================
class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None
        
    def add_screen(self, name, screen):
        self.screens[name] = screen
        
    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = self.screens[name]
            if hasattr(self.current_screen, 'on_enter'):
                self.current_screen.on_enter()
                
    def update(self):
        if self.current_screen:
            return self.current_screen.update()
        return True
        
    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)

# ===============================
# Base Screen Class
# ===============================
class Screen:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

        self.layer_backgrouds = ["background", "background2", "background3", "background4"]

    def draw_background(self, surface):
        for layer in self.layer_backgrouds:
            layer = ResourceManager().get_image(layer)
            if layer:
                surface.blit(layer, (0, 0))

    def update(self):
        return True
        
    def draw(self, surface):
        surface.fill(BLACK)
        
    def handle_event(self, event):
        pass
        
    def on_enter(self):
        pass