import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math
import random

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FRIC, GRAV, FPS

    ##############################################################################################

rot_2d = lambda points, a: points @ np.array([[math.cos(-a), -math.sin(-a)], [math.sin(-a), math.cos(-a)]])

    ##############################################################################################

class Bullet_Casing(pygame.sprite.Sprite):

    SPRITES = {}

    def __init__(self, game, groups, pos, angle, intial_height):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.size = size = 8
        self.points = np.array([
            [-size/2, 0.6 * -size/2],
            [size/2, 0.6 * -size/2],
            [size/2, 0.6 * size/2],
            [-size/2, 0.6 * size/2]
        ])

        self.pos = vec(pos)
        self.vel = vec(math.cos(angle), math.sin(angle)) * random.uniform(7, 10)

        self.angle = random.uniform(0, 2*math.pi)
        self.angle_mod = random.uniform(-0.5, 0.5)

        self.height = intial_height
        self.height_mod = -random.uniform(8, 10)

        self.lifetime = Timer(FPS * 4, 1)
        self.alpha_flash = Timer(20, 1)
        self.alpha = True

    def move(self):
        self.pos += self.vel

        self.vel *= FRIC
        if self.vel.magnitude() < 0.25:
            self.vel = vec()
        
        self.height.y += self.height_mod
        self.height_mod += GRAV / 20
        if self.height.y > 0:
            self.height.y = 0

    def update(self):
        self.lifetime.update()
        if self.lifetime.finished:
            return self.kill()

        elif self.lifetime.t / self.lifetime.end >= 0.5:
            self.alpha_flash.update()
            if self.alpha_flash.finished:
                self.alpha_flash.reset()
                self.alpha = not self.alpha

        self.move()

        self.angle += self.angle_mod
        self.angle_mod *= 0.95
        self.angle %= (2 * math.pi)

        self.draw()

    def draw(self):
        a = round(self.angle, 2)
        if (cached := self.SPRITES.get(a, None)) == None:
            surf = pygame.Surface((self.size * 1.5, self.size * 1.5), pygame.SRCALPHA)
            points = self.points.copy()
            pygame.draw.polygon(surf, (255, 183, 0), rot_2d(points, a) + vec(surf.size) / 2)
            points[:, 0] *= 0.4
            pygame.draw.polygon(surf, (160, 93, 0), rot_2d(points, a) + vec(surf.size) / 2)

            shadow = pygame.Surface((self.size * 1.5, self.size * 1.5), pygame.SRCALPHA)
            pygame.draw.polygon(shadow, (0, 0, 0), rot_2d(self.points, a) + vec(shadow.size) / 2)
            
            cached = (surf, shadow)
            self.SPRITES[a] = cached

        surf, shadow = cached
        surf.set_alpha(255 if self.alpha else 108)
        shadow.set_alpha(255 if self.alpha else 108)
        
        self.screen.blit(shadow, shadow.get_rect(center=self.pos - self.game.offset + vec(0, 2)))
        self.screen.blit(surf, surf.get_rect(center=self.pos - self.game.offset + self.height))

class Shotgun_Casing(Bullet_Casing):

    SHOTGUN_SPRITES = {}

    def __init__(self, game, groups, pos, angle, initial_height):
        super().__init__(game, groups, pos, angle, initial_height)

    def draw(self):
        a = round(self.angle, 2)
        if (cached := self.SHOTGUN_SPRITES.get(a, None)) == None:
            surf = pygame.Surface((self.size * 1.5, self.size * 1.5), pygame.SRCALPHA)
            points = self.points.copy()
            pygame.draw.polygon(surf, (255, 0, 47), rot_2d(points, a) + vec(surf.size) / 2)
            points[:, 0] *= 0.3
            points[:, 0] += -0.7 * self.size / 2
            pygame.draw.polygon(surf, (240, 152, 0), rot_2d(points, a) + vec(surf.size) / 2)

            shadow = pygame.Surface((self.size * 1.5, self.size * 1.5), pygame.SRCALPHA)
            pygame.draw.polygon(shadow, (0, 0, 0), rot_2d(self.points, a) + vec(shadow.size) / 2)
            
            cached = (surf, shadow)
            self.SHOTGUN_SPRITES[a] = cached

        surf, shadow = cached
        surf.set_alpha(255 if self.alpha else 108)
        shadow.set_alpha(255 if self.alpha else 108)
        
        self.screen.blit(shadow, shadow.get_rect(center=self.pos - self.game.offset + vec(0, 2)))
        self.screen.blit(surf, surf.get_rect(center=self.pos - self.game.offset + self.height))