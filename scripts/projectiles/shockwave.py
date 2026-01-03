import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import numpy as np

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE, FPS, GRAV, FRIC, TILE_SIZE
from scripts.utils.CORE_FUNCS import vec, lerp, Timer

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

    ##############################################################################################

class Lightning(pygame.sprite.Sprite):
    def __init__(self, game, groups, points: list, speed=10, colours=[(230, 230, 230)], line_width=2):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.segments = []
        self.points = points
        self.interp = 0
        self.speed = lambda: random.uniform(speed*0.8, speed*1.2)

        self.offset = 4
        self.generations = 3
        self.colours = colours
        self.line_width = line_width

    def gen_bolts(self):
        t = math.floor(self.interp) % len(self.points)
        interp = (self.interp % len(self.points)) - t

        start = vec(self.points[t]).lerp(vec(self.points[t+1 if t < len(self.points)-1 else 0]), interp)
        end = vec(self.points[t]).lerp(vec(self.points[t+1 if t < len(self.points)-1 else 0]), min(1, interp+self.speed()))

        self.segments = []
        self.segments.append([start, end])
        offset = self.offset

        for gen in range(self.generations):
            for segment in list(self.segments):
                self.segments.remove(segment)

                midpoint = segment[0].lerp(segment[1], 0.5)
                normal = (segment[1]-segment[0]).normalize()
                offset_vec = vec(-normal.y, normal.x)
                offset_vec *= random.uniform(-offset, offset)
                midpoint += offset_vec

                self.segments.append([segment[0], midpoint])
                self.segments.append([midpoint, segment[1]])
                
            offset //= 2

    def update(self):
        self.interp += math.radians(self.speed())
        self.gen_bolts()

        self.draw()

    def draw(self):
        i = 0
        for segment in self.segments:
            pygame.draw.line(
                self.screen, 
                (0, 0, 0), 
                segment[0] - self.game.offset + vec(0, 3), 
                segment[1] - self.game.offset + vec(0, 3), 
                int(self.line_width)
            )
            i += 0.5 if i < 128 else 0
            pygame.draw.line(
                self.screen, 
                [max(c-i, 0) for c in random.choice(self.colours)], 
                segment[0] - self.game.offset, 
                segment[1] - self.game.offset, 
                int(self.line_width)
            )
            i += 0.5 if i < 128 else 0


class Shockwave(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.size = 1
        self.size_mod = 12
        angles = np.linspace(0, 2 * math.pi, 7)
        self.points = np.column_stack((np.cos(angles), np.sin(angles))) * self.size
        self.pos = vec(pos)
        self.angle = 0

        self.lightnings = pygame.sprite.Group()
        self.edges = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
            [5, 0]
        ]
        for edge in self.edges:
            p1, p2 = self.points[edge]
            Lightning(game, [self.lightnings], [p1, p2], line_width=7, colours=[(156, 0, 161), (140, 0, 210), (114, 0, 73), (110, 0, 143)])

    def update(self):
        self.size += self.size_mod
        self.size_mod *= 0.95
        if self.size_mod < 0.1:
            return self.kill()
        
        self.angle += math.radians(2)

        points = rot_2d(self.points * self.size, self.angle) + self.pos
        for l, edge in zip(self.lightnings.sprites(), self.edges):
            l.points = points[edge]
            l.line_width -= 0.1

        self.draw()

    def draw(self):
        self.lightnings.update()