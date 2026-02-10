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
from scripts.utils.CORE_FUNCS import vec, lerp, Timer, saturate_colour

    ##############################################################################################

class Grenade_Explosion(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)

        self.parts = pygame.sprite.Group()
        self.outer = Grenade_Explosion.Circle(self.game, [self.parts], self.pos, 20, 7, (30 - 15, 28 - 15, 38 - 15))
        Grenade_Explosion.Circle(self.game, [self.parts], self.pos, 16, 4, (235, 101, 70))
        Grenade_Explosion.Circle(self.game, [self.parts], self.pos, 10, 2, (253, 252, 211))

        colours = [
            (25, 12, 36),
            (235, 101, 70),
            (253, 252, 211),
            (239, 209, 113),
            (191, 60, 97)
        ]
        for i in range(random.randint(12, 24)):
            Spark(
                self.game, 
                [self.parts], 
                self.pos, 
                random.uniform(3, 10),
                random.uniform(0, 2*math.pi),
                random.uniform(3, 8) / 2,
                random.choice(colours)
            )

        self.hit = False

    def update(self):
        self.parts.update()
        
        if not self.hit:
            if self.game.player.jump_height < 4 and (self.game.player.pos - self.pos).magnitude() < self.outer.radius * 0.9:
                self.game.player.health -= 10
                self.hit = True
                self.game.screen_shake.start(10, 10)
                # self.game.player.jump_height += 20

    class Circle(pygame.sprite.Sprite):
        def __init__(self, game, groups, pos, width, radius_mod, colour):
            super().__init__(groups)
            self.game = game
            self.screen = self.game.screen

            self.pos = vec(pos)
            self.radius = 0
            self.radius_mod = radius_mod
            self.width = width

            self.colour = colour

        def update(self):
            self.radius += self.radius_mod
            self.radius_mod *= 0.95
            self.width -= 0.2

            if self.width <= 0.1:
                return self.kill()

            pygame.draw.circle(self.screen, (0, 0, 0), self.pos - self.game.offset + vec(0, 4), self.radius, math.ceil(self.width))
            pygame.draw.circle(self.screen, self.colour, self.pos - self.game.offset, self.radius, math.ceil(self.width))
            
            pygame.draw.circle(self.game.emissive_surf, saturate_colour(self.colour, 3), self.pos - self.game.offset, self.radius * 1.1, math.ceil(self.width * 1.1))