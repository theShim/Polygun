import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

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
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.pos.x == 16.: self.pos.y = 0
        dh = self.target_height - self.pos.y
        if abs(dh) < 0.01:
            self.pos.y = self.target_height
            
        self.vel += self.tension * dh - self.vel * self.dampening
        self.pos.y += self.vel

    def update(self, screen):
        self.move()
        pygame.draw.circle(screen, (255, 0, 0), self.pos, self.radius)

class EnergyBar(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.player = self.game.player

        self.surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.surf.fill((100, 100, 255))
        
        self.springs = pygame.sprite.Group()
        self.dist = int(self.surf.width / 12)
        for i in range(0, self.surf.width + self.dist, self.dist):
            self.springs.add(EnergySpring(self.game, [self.springs], (i, 0.6 * self.surf.height)))

    def update(self):
        self.surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.surf.fill((100, 100, 255))

        # self.surf.fill((255, 255, 255), [
        #     0, 
        #     self.surf.height * (1 - (self.player.energy / self.player.max_energy)), 
        #     self.surf.width, 
        #     self.surf.height * (self.player.energy / self.player.max_energy),
        # ])

        self.springs.update(self.surf)

        self.draw()

    def draw(self):
        self.screen.blit(self.surf, (37 - 24, 80 - 24))
        pygame.draw.circle(self.screen, (0, 0, 0), (37, 80), 24, 3)