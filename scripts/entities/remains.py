import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math
import random

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.utils.convex_hull import convex_hull
from scripts.config.SETTINGS import WIDTH, HEIGHT, FRIC, GRAV

    ##############################################################################################

class Remains(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}


    def __init__(self, game, groups, pos, colour, initial_height=0):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.colour = colour
        self.height = initial_height

        self.surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        points = []
        for i in range(random.randint(4, 8)):
            x = random.randint(0, self.surf.width - 1)
            y = random.randint(0, self.surf.height - 1)
            points += [(x, y)]
        
        try:
            pygame.draw.polygon(self.surf, self.colour, (ps := convex_hull(points)))
        except:
            return self.kill()

        self.shadow = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0, 150), unsetcolor=(0, 0, 0, 0))

        self.point_num = len(ps)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = vec(math.cos(angle), math.sin(angle)) * random.uniform(2, 10)

        self.to_player = False #whether it should be going towards the player or not
        self.player_tracking_t = 1

    def move(self):
        if self.to_player:
            delta = (self.game.player.pos - self.pos)
            distance = delta.magnitude()
            direction = delta.normalize()

            self.player_tracking_t += self.game.dt
            self.vel += direction * (300 / max(distance, 20)) * 0.25 * self.player_tracking_t
            self.vel += vec(delta.y, -delta.x) * (50 / max(distance, 20)) * 0.005

        self.pos += self.vel

        self.vel *= FRIC
        if self.vel.magnitude() < 0.25:
            self.vel = vec()
        
        if self.height > 0:
            self.height -= GRAV / 10
        else:
            self.height = 0

    def update(self):
        self.move()

        if (dist := (self.pos - self.game.player.pos).magnitude()) < self.game.player.size:
            self.game.player.energy += self.point_num
            return self.kill()
        
        elif dist <= self.game.player.pickup_radius:
            self.to_player = True

        self.draw()

    def draw(self):
        self.screen.blit(self.shadow, self.surf.get_rect(center=self.pos - self.game.offset + vec(0, 3)))
        self.screen.blit(self.surf, self.surf.get_rect(center=self.pos - self.game.offset + vec(0, -self.height)))
        self.game.emissive_surf.blit(self.surf, self.surf.get_rect(center=self.pos - self.game.offset + vec(0, -self.height)))