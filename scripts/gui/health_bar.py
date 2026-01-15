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
        self.screen = self.game.gui_surf
        self.player = self.game.player
        
        self.surf = pygame.image.load("assets/gui/health_bar.png").convert_alpha()
        self.surf.set_colorkey((0, 0, 0))
        self.t = 0


    def update(self):
        self.draw()

    def draw(self):
        t = min(1, 1 - (self.player.health / self.player.max_health))
        self.t = self.t + (t - self.t) * 0.5
        pygame.draw.polygon(self.screen, (237, 28, 36), [(37, 16), (37, 45), (213 - 180 * (self.t), 45), (233 - 180 * (self.t), 16)])
        self.screen.blit(self.surf, (15, 10))