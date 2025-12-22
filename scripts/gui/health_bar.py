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

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.player = self.game.player
        
        self.surf = pygame.image.load("assets/gui/health_bar.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0))


    def update(self):
        self.draw()

    def draw(self):
        self.screen.blit(self.surf, (15, 10))