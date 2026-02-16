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

class Item_Manager:
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen

        self.items = pygame.sprite.Group()

    @property
    def current_items(self):
        data = {}
        for item in self.items:
            data[item.name] = data.get(item.name, 0) + 1
        return data 

    def update(self):
        non_timed = []
        timed = []
        for item in self.items:
            if item.type_ == "timed": timed.append(item)
            else: non_timed.append(item)
        
        non_timed.sort(key=lambda p: p.name)
        timed.sort(key=lambda p: p.timer.t / p.timer.end)
        items = non_timed + timed

        for i, item in enumerate(items):
            item.update(index=i)