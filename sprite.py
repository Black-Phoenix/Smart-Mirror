import glob
import pygame


class Sprite:
    def __init__(self):
        self.frames = []
        self.pos = 0

    def load_gif(self, path):
        file_name = glob.glob(path)
        file_name.sort()
        for i in file_name:
            self.frames.append(pygame.transform.scale(pygame.image.load(i).convert_alpha(), (30, 30)))

    def draw_frame(self, pos, screen, ai=0.1):
        screen.blit(self.frames[int(self.pos)], pos)
        self.pos = (self.pos + ai) % len(self.frames)
