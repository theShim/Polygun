import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.states.state_loader import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")

    def update(self):
        self.screen.fill((255, 0, 0))