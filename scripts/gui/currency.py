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

class CurrencyGUI(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.player = self.game.player

        self.size = size = 3
        self.surf = pygame.Surface((6 * size, 8 * size), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (100, 97, 139), [2 * size, 0 * size, 4 * size, 5 * size])
        pygame.draw.rect(self.surf, (100, 97, 139), [0 * size, 3 * size, 4 * size, 5 * size])
        pygame.draw.rect(self.surf, (100, 97, 139), [1 * size, 1 * size, 1 * size, 2 * size])
        pygame.draw.rect(self.surf, (100, 97, 139), [4 * size, 5 * size, 1 * size, 2 * size])
        pygame.draw.rect(self.surf, (254, 252, 211), [1 * size, 3 * size, 3 * size, 4 * size])
        pygame.draw.rect(self.surf, (254, 252, 211), [2 * size, 1 * size, 3 * size, 4 * size])
        pygame.draw.rect(self.surf, (163, 179, 182), [2 * size, 1 * size, 1 * size, 1 * size])
        pygame.draw.rect(self.surf, (163, 179, 182), [4 * size, 1 * size, 1 * size, 4 * size])
        pygame.draw.rect(self.surf, (163, 179, 182), [3 * size, 3 * size, 1 * size, 1 * size])
        pygame.draw.rect(self.surf, (163, 179, 182), [2 * size, 4 * size, 1 * size, 1 * size])
        pygame.draw.rect(self.surf, (163, 179, 182), [1 * size, 5 * size, 3 * size, 2 * size])
        pygame.draw.rect(self.surf, (121, 132, 157), [4 * size, 2 * size, 1 * size, 1 * size])
        pygame.draw.rect(self.surf, (121, 132, 157), [4 * size, 4 * size, 1 * size, 1 * size])
        pygame.draw.rect(self.surf, (121, 132, 157), [3 * size, 5 * size, 1 * size, 2 * size])
        pygame.draw.rect(self.surf, (121, 132, 157), [2 * size, 7 * size, 1 * size, 1 * size])
        self.outline = pygame.mask.from_surface(self.surf).to_surface(setcolor=(0, 0, 0), unsetcolor=(0, 0, 0, 0))

        self.font = Custom_Font.font1_5
        self.text = None
        self.current_count = -1

    def gen_new_text(self, number):
        number = str(number)
        self.text = pygame.Surface((self.font.calc_surf_width(number) + 6, self.font.space_height + 6), pygame.SRCALPHA)
        self.font.render(self.text, number, (0, 0, 1), (6, 3))
        self.font.render(self.text, number, (0, 0, 1), (0, 3))
        self.font.render(self.text, number, (0, 0, 1), (3, 6))
        self.font.render(self.text, number, (0, 0, 1), (3, 0))
        self.font.render(self.text, number, (255, 255, 255), (3, 3))

    def update(self):
        count = self.player.silver
        if count != self.current_count:
            self.gen_new_text(count)

        self.draw()

    def draw(self):
        for y in range(-1, 2):
            for x in range(-1, 2):
                if x != y:
                    self.screen.blit(self.outline, (37 + 40 + self.size * x, 80 - 16 + 1 + self.size * y))
        self.screen.blit(self.surf, (37 + 40, 80 - 16 + 1))

        self.screen.blit(self.text, (37 + 40 + self.size * 8, 80 - 16 + 1))