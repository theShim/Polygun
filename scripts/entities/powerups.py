import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import os

from scripts.gui.custom_fonts import Custom_Font, Font

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE, SIZE

    ##############################################################################################
    
class PowerUp(pygame.sprite.Sprite):
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/power_ups/"
        for filename in os.listdir(path):
            img = pygame.image.load(path + filename).convert_alpha()
            cls.SPRITES[filename.split(".")[0]] = img

    def __init__(self, game, groups, mode, a_offset=0):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen if mode != "gui" else self.game.gui_surf
        self.mode = mode

        self.angle = a_offset + math.pi/6
        self.angle_offset = 8 * math.pi

        self.radius = 72
        self.surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (0, 0, 0), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.surf, (255, 255, 255), (self.radius, self.radius), self.radius, 8)
        self.surf = pygame.transform.pixelate(self.surf, 2)
        self.shadow = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))
        self.ring_radius = 0
        self.anchor = vec(WIDTH/2, HEIGHT/2)
        self.pos = self.anchor.copy()
        self.external_offset = vec()
        self.hover_offset = 0

        img = random.choice(list(self.SPRITES.values()))
        self.surf.blit(img, img.get_rect(center=vec(self.surf.size)/2))

    def update(self):
        if self.mode == "gui":
             self.gui_update()

    def gui_update(self):
        a = self.angle + self.angle_offset
        self.angle_offset *= 0.975

        t = (1 - (self.angle_offset / (8 * math.pi)))
        self.ring_radius = 170 * t

        self.pos = self.anchor + vec(math.cos(a), math.sin(a)) * self.ring_radius - vec(self.surf.size)/2
        self.pos.x += 220 * t

        if self.game.mousePos.distance_to(self.pos + vec(self.surf.size)/2) < self.radius:
            self.hover_offset += (-20 - self.hover_offset) * 0.2
        else:
            self.hover_offset += (0 - self.hover_offset) * 0.2

        self.screen.blit(self.shadow, self.pos + vec(6, 9 + t * 30) + self.external_offset)
        self.screen.blit(self.surf, self.pos + vec(0, t * 30 + self.hover_offset) + self.external_offset)