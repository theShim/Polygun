import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math
import random

from scripts.gui.custom_fonts import Custom_Font, Font
from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class EnergySpring(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game

        self.pos = vec(pos)
        self.radius = 1
        self.target_height = self.pos.y

        self.dampening = 0.05 * 2
        self.tension = 0.01
        self.vel = 0
        # self.held = False

        # self.draw_flag = not False

    def move(self):
        dh = self.target_height - self.pos.y
        if abs(dh) < 0.01:
            self.pos.y = self.target_height
            
        self.vel += self.tension * dh - self.vel * self.dampening
        self.pos.y += self.vel

    def update(self, screen):
        self.move()
        # pygame.draw.circle(screen, (255, 0, 0), self.pos, self.radius)

class EnergyBar(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.overlay = pygame.Surface((48, 48), pygame.SRCALPHA)
        cls.overlay.fill((255, 0, 0))
        pygame.draw.circle(cls.overlay, (0, 0, 0, 0), (24, 24), 24)

    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.gui_surf
        self.player = self.game.player

        self.surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.surf.fill((100, 100, 255))
        
        self.springs = pygame.sprite.Group()
        self.dist = int(self.surf.width / 12)
        self.sinner = None

        for i in range(0, self.surf.width + self.dist, self.dist):
            s = EnergySpring(self.game, [self.springs], (i, self.surf.height))
            if i == 16.:
                self.sinner = s
        self.current_target_height = self.surf.height

        self.a = 0

    def spread_wave(self):
        spread = 0.08
        target_height = self.surf.height * (1 - (self.player.energy / self.player.max_energy))
        if (target_height - self.current_target_height) < 2:
            self.sinner = random.choice(self.springs.sprites())
            self.current_target_height = target_height
        self.sinner.target_height = self.sinner.target_height + (target_height - self.sinner.target_height) * random.uniform(-0.75, 1)

        for i in range(len(self.springs)):
            springs = self.springs.sprites().copy()
            if i > 0:
                springs[i - 1].vel += spread * (springs[i].pos.y - springs[i - 1].pos.y)
                springs[i - 1].target_height += spread * (springs[i].target_height - springs[i - 1].target_height)
            try:
                springs[i + 1].vel += spread * (springs[i].pos.y - springs[i + 1].pos.y)
                springs[i + 1].target_height += spread * (springs[i].target_height - springs[i + 1].target_height)
            except IndexError:
                pass

    def update(self):
        self.surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.surf.fill((255, 0, 0))

        # self.sinner.pos.y = self.surf.height * (1 - (self.player.energy / self.player.max_energy)) + math.sin(self.a) * 4
        # self.a += math.radians(20)

        pygame.draw.polygon(self.surf, pygame.Color(255, 255, 255).lerp((111, 178, 255), min(1, self.player.energy / self.player.max_energy)), [p.pos for p in self.springs] + [(self.surf.width, self.surf.height), (0, self.surf.height)])
        self.surf.blit(self.overlay)
        self.surf.set_colorkey((255, 0, 0))

        self.springs.update(self.surf)
        self.spread_wave()

        self.draw()

    def draw(self):
        self.screen.blit(self.surf, (37 - 24, 80 - 24))
        pygame.draw.circle(self.screen, (0, 0, 1), (37, 80), 24, 3)