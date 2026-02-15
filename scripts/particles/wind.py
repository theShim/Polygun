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

class Wind_Particle(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, vel, col=(255, 0, 0)):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos) - vel
        self.tail = self.pos - vel * (random.randint(10, 15) / 20)
        self.t = 0
        self.decay = random.uniform(0.0125, 0.015) / 5
        self.vel: vec = vel / 2
        self.col = col
        self.rot_direction = random.choice([-1, 1]) * 4
        self.alpha = 255

    def update(self):
        if self.pos.y - self.game.offset.y < -50:
            return self.kill()
        
        self.t += self.decay
        if self.t >= 0.5:
            return self.kill()
        
        self.alpha -= random.randint(1, 3)
        if self.alpha <= 0:
            return self.kill()
        
        self.pos += self.vel
        self.vel.rotate_ip(self.t * self.rot_direction * self.vel.magnitude())
        self.tail = self.tail.lerp(self.pos, min(1, self.t))
        self.draw()

    def draw(self):
        pygame.draw.line(self.screen, self.col, self.pos - self.game.offset, self.tail - self.game.offset, 2)

    def draw(self):
        min_x = min(self.pos[0], self.tail[0])
        min_y = min(self.pos[1], self.tail[1])
        max_x = max(self.pos[0], self.tail[0])
        max_y = max(self.pos[1], self.tail[1])
        
        width = max_x - min_x
        height = max_y - min_y
        
        temp_surface = pygame.Surface((width + 1, height + 1), pygame.SRCALPHA)
        
        start_pos = (self.pos[0] - min_x, self.pos[1] - min_y)
        end_pos = (self.tail[0] - min_x, self.tail[1] - min_y)
        pygame.draw.line(temp_surface, self.col + (self.alpha,), start_pos, end_pos, 2)
        
        self.screen.blit(temp_surface, (min_x - self.game.offset[0], min_y - self.game.offset[1]))
        self.game.emissive_surf.blit(temp_surface, (min_x - self.game.offset[0], min_y - self.game.offset[1]))