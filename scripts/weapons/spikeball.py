import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import json
import numpy as np

from scripts.particles.sparks import Spark

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

class Spikeball(pygame.sprite.Sprite):
    TYPE = "melee"
    
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.vel = vec()
        self.acc = vec()

        self.radius = 10

    def move(self):
        mousePos = self.game.mousePos
        self.vel += (mousePos + self.game.offset - self.pos) * 0.2

        if (delta := self.pos - self.game.player.pos).magnitude() > 100:
            self.vel += -delta * 0.5
            
        self.vel *= 0.9
        # self.vel.clamp_magnitude_ip()
        self.pos += self.vel * 0.1

    def update(self):
        self.move()
        self.render()

    def render(self):
        pygame.draw.circle(self.screen, (255, 0, 0), self.pos - self.game.offset, self.radius)
        pygame.draw.circle(self.game.emissive_surf, (255, 0, 0), self.pos - self.game.offset, self.radius * 1.3)