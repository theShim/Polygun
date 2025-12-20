import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE

    ##############################################################################################
    
class DeviceConnection(pygame.sprite.Sprite):
    def __init__(self, game, groups, index):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.font: Font = Custom_Font.font2
        self.index = index

        self.surf = pygame.Surface((300, 200), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (0, 0, 0), self.surf.get_rect(), 8, 30)
        pygame.draw.rect(self.surf, (255, 255, 255), self.surf.get_rect().inflate(-4, -4), 3, 30)
        self.font.render(self.surf, f"Device {self.index + 1}", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width(f"Device {self.index + 1}"), self.font.space_height * 2) / 2 + vec(-2, -2))
        self.font.render(self.surf, f"Device {self.index + 1}", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width(f"Device {self.index + 1}"), self.font.space_height * 2) / 2 + vec(-2, 2))
        self.font.render(self.surf, f"Device {self.index + 1}", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width(f"Device {self.index + 1}"), self.font.space_height * 2) / 2 + vec(2, -2))
        self.font.render(self.surf, f"Device {self.index + 1}", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width(f"Device {self.index + 1}"), self.font.space_height * 2) / 2 + vec(2, 2))
        self.font.render(self.surf, f"Device {self.index + 1}", (255, 255, 255), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width(f"Device {self.index + 1}"), self.font.space_height * 2) / 2)
        self.font.render(self.surf, "Connected", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width("Connected"), 0) / 2 + vec(-2, -2))
        self.font.render(self.surf, "Connected", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width("Connected"), 0) / 2 + vec(-2, 2))
        self.font.render(self.surf, "Connected", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width("Connected"), 0) / 2 + vec(2, -2))
        self.font.render(self.surf, "Connected", (1, 0, 0), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width("Connected"), 0) / 2 + vec(2, 2))
        self.font.render(self.surf, "Connected", (255, 255, 255), vec(self.surf.size) / 2 - vec(self.font.calc_surf_width("Connected"), 0) / 2)

        self.pos = self.surf.get_rect(center=vec(SIZE)/2).topleft

    def update(self):
        self.screen.blit(self.surf, self.pos)