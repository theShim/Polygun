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

        displacement = (self.target_pos - self.start_pos).magnitude()
        self.speed = 300
        self.total_time = displacement / self.speed # s = ut => t = s/u
        self.time = 0
        self.dh = 0
        self.landed = False

        self.max_height = 50
        self.u = math.sqrt(2 * GRAV * self.max_height) #v^2 = u^2 - 2as, v = 0 at max height

    def move(self):
        self.time += self.game.dt
        self.dh = (self.u * self.time) - (0.5 * GRAV * self.time ** 2) #s = ut + 1/2 at^2
        
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
        screen_y = self.pos.y - self.game.offset.y
        radius = (((5 * screen_y) / HEIGHT) + 4)

        y = radius / 2
        shadow = pygame.Surface((y*4, y), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y])
        shadow.set_alpha(128)
        self.screen.blit(shadow, shadow.get_rect(center=(self.pos + vec(0, radius) - self.game.offset)))

        pygame.draw.circle(self.screen, (255, 0, 0), self.pos - self.game.offset - vec(0, self.dh), radius)