import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math
import random

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT, FRIC

    ##############################################################################################

class Remains(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}


    def __init__(self, game, groups, pos, colour, initial_height=0):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.colour = colour
        self.height = initial_height

        self.surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        # for i in range(random.randint(4, 5))

        self.shadow = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0, 150), unsetcolor=(0, 0, 0, 0))

        angle = random.uniform(0, 2 * math.pi)
        self.vel = vec(math.cos(angle), math.sin(angle)) * random.uniform(2, 10)

    def move(self):
        self.pos += self.vel

        self.vel *= FRIC
        if self.vel.magnitude() < 0.25:
            self.vel = vec()

    def update(self):
        self.move()

        self.draw()

    def draw(self):
        self.screen.blit(self.shadow, self.surf.get_rect(center=self.pos - self.game.offset + vec(0, 3)))
        self.screen.blit(self.surf, self.surf.get_rect(center=self.pos - self.game.offset + vec(0, -self.height)))