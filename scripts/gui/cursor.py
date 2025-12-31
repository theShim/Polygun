import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import numpy as np
import math

from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Cursor(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        cls.SPRITES["cursor_base"] = pygame.image.load("assets/gui/cursor_base.png").convert_alpha()

        for spr in cls.SPRITES:
            cls.SPRITES[spr] = pygame.transform.scale_by(cls.SPRITES[spr], 0.5)
            # cls.SPRITES[spr].set_colorkey((0, 0, 0))
        
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.state = "base"

    def update(self):
        self.draw()

    def draw(self):
        self.screen.blit(spr := self.SPRITES["cursor_" + self.state], spr.get_rect(topleft=self.game.mousePos))