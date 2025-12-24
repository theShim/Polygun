import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random

from scripts.particles.sparks import Spark

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp

    ##############################################################################################

class Grenade(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, target_pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        
        self.start_pos = vec(pos)
        self.target_pos = vec(target_pos)
        self.pos = self.start_pos.copy()

        self.max_height = 70
        self.vel = math.sqrt(self.max_height * 2 * GRAV)
        self.total_time = (2 * self.vel) / GRAV
        self.time = 0.1
        self.dh = 0
        self.landed = False

    def move(self):
        self.time += self.game.dt * 5
        self.dh = (self.vel * self.time) - (0.5 * GRAV * (self.time ** 2))
        
        if self.dh <= 0:
            self.dh = 0
            self.landed = True
        if self.time > self.total_time:
            self.time = self.total_time

        self.pos = self.start_pos.lerp(self.target_pos, self.time / self.total_time)

    def update(self):
        self.move()
        self.draw()

    def draw(self):
        radius = (((5 * self.dh) / self.max_height) + 4)

        y = radius / 2
        shadow = pygame.Surface((y*4, y), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y])
        shadow.set_alpha(128)
        self.screen.blit(shadow, shadow.get_rect(center=(self.pos + vec(0, radius) - self.game.offset)))

        pygame.draw.circle(self.screen, (255, 0, 0), self.pos - self.game.offset - vec(0, self.dh), radius)