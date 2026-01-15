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

        self.rope = Rope(self.game, [], vec(pos))

        self.radius = 16

    def move(self):
        mousePos = self.game.mousePos
        self.vel += (mousePos + self.game.offset - self.pos) * 0.2

        if (delta := self.pos - self.game.player.pos).magnitude() > 150:
            self.vel += -delta * 0.9
            
        self.vel *= 0.7
        self.pos += self.vel * 0.1

    def update(self):
        self.move()
        
        self.rope.start.pos = self.game.player.pos.copy()
        self.rope.end.pos = self.pos.copy()
        self.rope.update()

        self.render()

    def render(self):
        pygame.draw.circle(self.screen, (255, 0, 0), self.pos - self.game.offset, self.radius)
        pygame.draw.circle(self.game.emissive_surf, (255, 0, 0), self.pos - self.game.offset, self.radius * 1.3)
        

class Rope(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.points = pygame.sprite.Group()
        self.length = 20
        self.start = VerletParticle(self.game, [self.points], pos)
        self.start.pinned = True
        for i in range(self.length, 150, self.length):
            VerletParticle(self.game, [self.points], pos + vec(i, 0))
        self.end = VerletParticle(self.game, [self.points], pos + vec(150, 0))
        self.end.pinned = True

        self.links = [[i, i+1] for i in range(len(self.points) - 1)] + [[0, 1] for i in range(5)]
        self.lengths = [self.length * 0.95 for i in range(len(self.points) - 1 + 5)]
        

    def constraints(self):
        points = self.points.sprites()
        for i, (v1, v2) in enumerate(self.links):
            p1, p2 = points[v1], points[v2]
            delta: vec = p2.pos - p1.pos
            diff = (dist := delta.magnitude()) - self.lengths[i]
            offset = delta * (diff / dist) / 2
            p1.pos += offset
            p2.pos -= offset

    def update(self):
        self.constraints()
        self.draw()

    def draw(self):
        for start, end in self.links:
            pygame.draw.line(self.screen, (255, 0, 0), self.points.sprites()[start].pos - self.game.offset, self.points.sprites()[end].pos - self.game.offset, 4)
            pygame.draw.line(self.game.emissive_surf, (255, 0, 0), self.points.sprites()[start].pos - self.game.offset, self.points.sprites()[end].pos - self.game.offset, 4)

        self.points.update()

class VerletParticle(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, radius=5):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.prev_pos = self.pos.copy()
        self.acc = vec()
        self.vel = vec()

        self.radius = radius
        self.pinned = False

    def move(self):
        if self.pinned: return

        self.acc = vec(0, GRAV * 0) * self.game.dt

        self.vel = self.pos - self.prev_pos
        self.vel.x *= 0.97
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        self.prev_pos = self.pos.copy()
        self.pos += self.vel + self.acc
        
    def update(self):
        self.move()
        # self.draw()

    def draw(self):
        pygame.draw.circle(self.screen, (255, 12, 73), self.pos - self.game.offset, self.radius)