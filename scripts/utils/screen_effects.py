import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.utils.CORE_FUNCS import Timer, vec

    ##############################################################################################

class Screen_Shake:
    def __init__(self, game):
        self.game = game

        self.timer = 0
        self.intensity = 4
        self.drop_off = 1

    @property
    def on(self):
        return bool(self.timer)

    def start(self, duration: int, intensity=1, drop_off=1):
        self.timer = duration
        self.intensity = intensity
        self.drop_off = drop_off

    def update(self):
        if self.timer <= 0: return

        self.timer -= 1
        if self.drop_off < 1:
            self.intensity *= self.drop_off
        self.game.offset += vec(random.uniform(-1*self.intensity, 1*self.intensity), random.uniform(-1*self.intensity, 1*self.intensity))