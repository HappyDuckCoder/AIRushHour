from constants import *
from Resource.Resource import ResourceManager

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


class Screen:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

        self.layer_backgrouds_1 = ["background1", "background12", "background13", "background14"]
        self.layer_backgrouds_2 = ["background21", "background22", "background23"]

        self.list_screens_1 = ["intro", "menu", "setting", "about_us", "statistic"]

    def draw_background(self, surface, current_screen="intro"):
        if current_screen in self.list_screens_1:
            for layer in self.layer_backgrouds_2:
                layer = ResourceManager().get_image(layer)
                if layer:
                    surface.blit(layer, (0, 0))
        else: 
            for layer in self.layer_backgrouds_1:
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