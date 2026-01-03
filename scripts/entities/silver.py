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

class Silver(pygame.sprite.Sprite):
    
    @classmethod
    def cache_sprites(cls):
        size = 2
        cls.surf = pygame.Surface((6 * size, 8 * size), pygame.SRCALPHA)
        pygame.draw.rect(cls.surf, (100, 97, 139), [2 * size, 0 * size, 4 * size, 5 * size])
        pygame.draw.rect(cls.surf, (100, 97, 139), [0 * size, 3 * size, 4 * size, 5 * size])
        pygame.draw.rect(cls.surf, (100, 97, 139), [1 * size, 1 * size, 1 * size, 2 * size])
        pygame.draw.rect(cls.surf, (100, 97, 139), [4 * size, 5 * size, 1 * size, 2 * size])
        pygame.draw.rect(cls.surf, (254, 252, 211), [1 * size, 3 * size, 3 * size, 4 * size])
        pygame.draw.rect(cls.surf, (254, 252, 211), [2 * size, 1 * size, 3 * size, 4 * size])
        pygame.draw.rect(cls.surf, (163, 179, 182), [2 * size, 1 * size, 1 * size, 1 * size])
        pygame.draw.rect(cls.surf, (163, 179, 182), [4 * size, 1 * size, 1 * size, 4 * size])
        pygame.draw.rect(cls.surf, (163, 179, 182), [3 * size, 3 * size, 1 * size, 1 * size])
        pygame.draw.rect(cls.surf, (163, 179, 182), [2 * size, 4 * size, 1 * size, 1 * size])
        pygame.draw.rect(cls.surf, (163, 179, 182), [1 * size, 5 * size, 3 * size, 2 * size])
        pygame.draw.rect(cls.surf, (121, 132, 157), [4 * size, 2 * size, 1 * size, 1 * size])
        pygame.draw.rect(cls.surf, (121, 132, 157), [4 * size, 4 * size, 1 * size, 1 * size])
        pygame.draw.rect(cls.surf, (121, 132, 157), [3 * size, 5 * size, 1 * size, 2 * size])
        pygame.draw.rect(cls.surf, (121, 132, 157), [2 * size, 7 * size, 1 * size, 1 * size])
        cls.shadow = pygame.mask.from_surface(cls.surf).to_surface(setcolor=(0, 0, 0, 140), unsetcolor=(0, 0, 0, 0))

    def __init__(self, game, groups, pos, intial_height):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = vec(math.cos(angle), math.sin(angle)) * random.uniform(2, 12)

        self.height = intial_height
        self.height_mod = -random.uniform(8, 14)

        self.lifetime = Timer(FPS * 15, 1)
        self.alpha_flash = Timer(20, 1)
        self.alpha = True

        self.to_player = False #whether it should be going towards the player or not

    def move(self):
        if self.to_player:
            delta = (self.game.player.pos - self.pos)
            distance = delta.magnitude()
            direction = delta.normalize()

            self.vel += direction * (300 / max(distance, 20)) * 0.25
            self.vel += vec(delta.y, -delta.x) * (50 / max(distance, 20)) * 0.005

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

        elif self.lifetime.t / self.lifetime.end >= 0.7:
            self.alpha_flash.update()
            if self.alpha_flash.finished:
                self.alpha_flash.reset()
                self.alpha = not self.alpha

        self.move()

        if (dist := (self.pos - self.game.player.pos).magnitude()) < self.game.player.size:
            self.game.player.silver += 1
            return self.kill()
        
        elif dist <= self.game.player.pickup_radius:
            self.to_player = True

        self.draw()

    def draw(self):
        surf = self.surf.copy()
        shadow = self.shadow.copy()

        surf.set_alpha(255 if self.alpha else 108)
        shadow.set_alpha(255 if self.alpha else 108)
        
        self.screen.blit(shadow, shadow.get_rect(center=self.pos - self.game.offset + vec(0, 4)))
        self.screen.blit(surf, surf.get_rect(center=self.pos - self.game.offset + self.height))