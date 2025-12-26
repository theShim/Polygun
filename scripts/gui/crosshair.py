import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################
    
rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

    ##############################################################################################

class CrossHair(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.radius = 16
        self.angle = 0

        self.spoke_angles = np.array([math.radians(a) for a in (0, 90, 180, 270)])
        self.outer_ring = self.radius * np.column_stack((np.cos(self.spoke_angles), np.sin(self.spoke_angles)))
        self.inner_ring = 0.4 * self.radius * np.column_stack((np.cos(self.spoke_angles), np.sin(self.spoke_angles)))

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            self.angle += math.radians(10)

        self.draw()

    def draw(self):
        for inner, outer in zip(self.inner_ring, self.outer_ring):
            start = self.game.mousePos + vec(inner)
            end   = self.game.mousePos + vec(outer) * 0.95
            pygame.draw.line(self.screen, (20, 20, 20), start + vec(0, 3), end + vec(0, 3), 3)

        pygame.draw.circle(self.screen, (20, 20, 20), self.game.mousePos + vec(0, 3), self.radius, 4)

        
        for inner, outer in zip(self.inner_ring, self.outer_ring):
            start = self.game.mousePos + vec(inner)
            end   = self.game.mousePos + vec(outer) * 0.95
            pygame.draw.line(self.screen, (120, 120, 120), start, end, 3)

        pygame.draw.circle(self.screen, (120, 120, 120), self.game.mousePos, self.radius, 4)