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
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

class Spark(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, scale, angle, speed=None, colour=(255, 255, 255), spin=False, grav=False, outline=None, shadow_height=None, shadow_col=(0, 0, 0, 0)):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.scale = scale
        self.angle = angle
        self.speed = random.uniform(3, 6) if speed == None else speed
        self.colour = colour
        self.shadow_height = shadow_height or vec()
        self.shadow_mod = random.random() if random.randint(0, 5) == 0 else 0
        self.shadow_col = shadow_col

        self.spin = spin
        self.grav = grav
        self.outline = outline

        for i in range(int(self.scale)+1):
            self.move()


    def move(self):
        self.pos += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed

    def apply_gravity(self, friction, force, terminal_velocity):
        movement = vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        movement[1] = min(terminal_velocity, movement[1] + force)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])


    def update(self):
        self.speed -= 0.1
        if self.speed < 0:
            return self.kill()
        
        if self.spin:
            self.angle += 0.1
        if self.grav:
            self.apply_gravity(0.975, 0.2, 8)
        self.move()

        self.shadow_height.y -= self.shadow_mod
        
        self.draw()

    def draw(self):
        points = np.array([
            vec(math.cos(self.angle), math.sin(self.angle)) * self.scale * self.speed,
            vec(math.cos(self.angle - math.pi/2), math.sin(self.angle - math.pi/2)) * 0.3 * self.scale * self.speed,
            vec(math.cos(self.angle - math.pi), math.sin(self.angle - math.pi)) * 3 * self.scale * self.speed + vec(random.random(), random.random())*self.speed,
            vec(math.cos(self.angle + math.pi/2), math.sin(self.angle + math.pi/2))  * 0.3 * self.scale * self.speed,
        ])
        points += self.pos - self.game.offset

        if not self.shadow_height:
            pygame.draw.polygon(self.screen, self.shadow_col, points + [0, 2])
            pygame.draw.polygon(self.screen, self.colour, points)
        else:
            pygame.draw.polygon(self.screen, self.shadow_col, points)
            pygame.draw.polygon(self.screen, self.colour, points + self.shadow_height)

        if self.outline:
            pygame.draw.polygon(self.screen, self.outline, points, max(1, int(self.scale/4)))