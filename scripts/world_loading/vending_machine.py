import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

# from scripts.world_loading.tiles import Tile
# from scripts.world_loading.nature.manager import Nature_Manager

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE

    ##############################################################################################
    
class VendingMachine(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.o_pos = vec(pos) + vec(0, -HEIGHT * 2)
        self.target_pos = vec(pos)
        self.pos = self.o_pos.copy()
        self.surf = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_machine.png").convert_alpha(), 3.5)
        self.surf.set_colorkey((0, 0, 0))
        self.t = 0

        self.lights1 = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_lights1.png").convert_alpha(), 3.5)
        self.lights1.set_colorkey((0, 0, 0))

        self.lights2 = pygame.transform.scale_by(pygame.image.load("assets/currency/vending_lights2.png").convert_alpha(), 3.5)
        self.lights2.set_colorkey((0, 0, 0))
        self.flicker_timer = Timer(FPS, 1)
        self.lights2on = True

    def update(self):
        if self.t < 1:
            self.t += 0.4 * self.game.dt
            self.t = min(1, self.t)
            self.pos = self.o_pos.lerp(self.target_pos, 2 ** (10 * self.t - 10))
            if self.t == 1:
                self.pos = self.target_pos
                self.game.screen_shake.start(30, 15, 0.99)

        self.flicker_timer.update()
        if self.flicker_timer.finished:
            self.flicker_timer.change_speed(random.randint(1, 5))
            self.flicker_timer.reset()
            self.lights2on = not self.lights2on

        self.draw()

    def draw(self):
        self.screen.blit(self.surf, self.surf.get_rect(center=self.pos - self.game.offset))
        self.game.emissive_surf.blit(self.lights1, self.surf.get_rect(center=self.pos - self.game.offset))

        if self.lights2on:
            self.game.emissive_surf.blit(self.lights2, self.surf.get_rect(center=self.pos - self.game.offset))