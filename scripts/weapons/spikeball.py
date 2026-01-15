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

        self.radius = 10

    def update(self):
        self.render()

    def render(self):
        pygame.draw.circle(self.screen, (255, 0, 0), self.pos, self.radius)