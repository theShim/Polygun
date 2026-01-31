import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import json
import numpy as np

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer, saturate_colour

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

class Death_Particle(pygame.sprite.Sprite):

    size = 1
    POINTS = np.array([
        [-size/2, -size/2],
        [size/2, -size/2],
        [size/2, size/2],
        [-size/2, size/2]
    ])
    
    def __init__(self, game, groups, pos, angle):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.angle = angle
        self.angle_mod = 10
        self.rot = 0 
        self.t = 0

        self.dist = 0
        self.max_dist = 40
        self.radius = 1

    def update(self):
        self.dist += (self.max_dist - self.dist) * 0.02
        self.t += self.game.dt * 4
        self.radius = max(0, (4/3) * (-self.t * self.t + 6*self.t))
        self.angle += math.radians(self.angle_mod)
        self.angle_mod *= 0.99
        self.rot += math.radians(4)

        if self.radius <= 0:
            return self.kill()

        self.draw()

    def draw(self):
        points = rot_2d(self.POINTS * self.radius, self.rot)
        outline = points * 1.4
        light = points * 2

        points += self.pos + vec(math.cos(self.angle), math.sin(self.angle)) * self.dist - self.game.offset
        outline += self.pos + vec(math.cos(self.angle), math.sin(self.angle)) * self.dist - self.game.offset
        light += self.pos + vec(math.cos(self.angle), math.sin(self.angle)) * self.dist - self.game.offset

        pygame.draw.polygon(self.screen, (0, 114 - 50, 110 - 50), outline)
        col = ((1 + math.sin(2 * self.rot)) * 0.5 * 255, 255, 247)
        pygame.draw.polygon(self.screen, col, points)
        pygame.draw.polygon(self.game.emissive_surf, (0, 114 - 50, 110 - 50), outline)
        pygame.draw.polygon(self.game.emissive_surf, col, light)