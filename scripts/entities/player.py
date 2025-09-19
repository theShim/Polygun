import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math
import random
import json
import numpy as np


from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, Z_LAYERS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

class Player(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.size = size = 24
        self.points = np.array([
            [-size/2, -size/2],
            [size/2, -size/2],
            [size/2, size/2],
            [-size/2, size/2]
        ])
        self.pos = vec(WIDTH/2 - size/2, HEIGHT/2 - size/2)

        self.vel = vec()
        self.acc = vec()
        self.run_speed = 100
        self.angle = 0

    def move(self):
        self.acc = vec()

        self.directional_inputs()
        self.apply_forces()

    def directional_inputs(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.acc.x = -1 * self.run_speed
            # if self.vel.x > 0: self.vel.x = 0
        if keys[pygame.K_d]:
            self.acc.x = 1 * self.run_speed
            # if self.vel.x < 0: self.vel.x = 0
        if keys[pygame.K_s]:
            self.acc.y = 1 * self.run_speed
            # if self.vel.y < 0: self.vel.y = 0
        if keys[pygame.K_w]:
            self.acc.y = -1 * self.run_speed
            # if self.vel.y > 0: self.vel.y = 0

        self.acc.clamp_magnitude_ip(self.run_speed)
        self.change_direction()

    def apply_forces(self):
        #actually applying acceleration to the player velocity
        self.vel.x += self.acc.x * self.game.dt
        self.vel.y += self.acc.y * self.game.dt

        self.vel *= FRIC #slowing them down by applying friction
        if -0.25 < self.vel.x < 0.25: #bounds to prevent sliding bug
            self.vel.x = 0
        if -0.25 < self.vel.y < 0.25:
            self.vel.y = 0
            
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def change_direction(self):
        # get raw mouse pos (window coords, affected by scaling)
        mousePos = pygame.mouse.get_pos()

        # scale back into internal surface resolution
        window_size = pygame.display.get_window_size()  # actual window size (after scaling)
        scale_x = WIDTH / window_size[0]
        scale_y = HEIGHT / window_size[1]
        mousePos = vec(mousePos[0] * scale_x, mousePos[1] * scale_y)

        mousePos = (mousePos) + self.game.offset

        mousePos = self.pos + self.vel

        delta = mousePos - self.pos
        self.angle = math.atan2(delta.y, delta.x)

    def update(self):
        self.move()
        self.draw()

    def draw(self):
        points = self.points.copy()
        if self.acc.magnitude():
            points[0, 1] *= 0.6
            points[3, 1] *= 0.6
            points[1, 1] *= 0.6
            points[2, 1] *= 0.6
        points = rot_2d(points, self.angle)
        pygame.draw.polygon(self.screen, (0, 255, 247), points + self.pos)