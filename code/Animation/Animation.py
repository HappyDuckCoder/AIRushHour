import pygame

class AnimationStrategy:
    def __init__(self, frames):
        self.frames = frames
        self.index = 0
        self.frame_rate = 100000
        self.last_update = pygame.time.get_ticks()
        self.current_frames = frames
        self.done_once = False

    def update(self, surface, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.index += 1
            self.last_update = now
            if self.index >= len(self.frames):
                self.index = 0
                self.done_once = True
        surface.blit(self.frames[self.index], (x, y))
