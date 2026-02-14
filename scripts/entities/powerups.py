import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.gui.custom_fonts import Custom_Font, Font

from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS, TILE_SIZE, LEVEL_SIZE, SIZE

    ##############################################################################################
    
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game, groups, mode):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen if mode != "gui" else self.game.gui_surf
        self.mode = mode

        self.surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (0, 0, 0), (32, 32), 32)
        pygame.draw.circle(self.surf, (255, 255, 255), (32, 32), 32, 4)
        self.surf = pygame.transform.pixelate(self.surf, 2)
        self.pos = vec(SIZE)/2

    def update(self):
        a = random.uniform(0, 6)
        self.screen.blit(self.surf, vec(SIZE)/2 + vec(math.cos(a), math.sin(a)) * 200)